#!/usr/bin/env python3
"""统一 SVG 图表模板。

设计原则：
- 不把画布宽度、泳道数量、颜色写死；宽度和高度根据内容自动计算，也可手动指定。
- 只提供默认语义色和常用组件；实际图可按内容覆盖颜色、尺寸和布局。
- 只依赖 Python 标准库，不引入第三方包。

用法：
    python3 svg-figure-template.py example.svg

改图时：
1. 复制本文件或修改 build_example()；
2. 用 SvgFigure 的方法画标题、图例、泳道、节点、箭头、说明框、矩阵；
3. 生成 SVG 后，在 Markdown 中用图片链接引用。
"""

from __future__ import annotations

import math
import sys
from html import escape
from pathlib import Path

MARGIN = 36
MIN_WIDTH = 800
MIN_HEIGHT = 400
FONT_SANS = "'Noto Sans CJK SC','Source Han Sans SC','WenQuanYi Micro Hei',sans-serif"
FONT_MONO = "'DejaVu Sans Mono','Noto Sans Mono CJK SC',monospace"

# 默认语义色。不是强制规范：可以在 SvgFigure(palette={...}) 中覆盖，
# 也可以给单个组件传十六进制颜色。
PALETTE = {
    "ink": "#0f172a",
    "body": "#334155",
    "dim": "#64748b",
    "line": "#e2e8f0",
    "bg": "#f8fafc",
    "slate": "#475569",
    "muted": "#94a3b8",
    "grid": "#cbd5e1",
    "white": "#ffffff",
    "green": "#0f9d58",
    "green_bg": "#f2fcf5",
    "indigo": "#4f46e5",
    "indigo_bg": "#eef2ff",
    "amber": "#d97706",
    "amber_bg": "#fff9ee",
    "red": "#dc2626",
    "red_bg": "#fff5f5",
    "cyan": "#0891b2",
    "cyan_bg": "#ecfeff",
    "header_bg": "#f1f5f9",
}

TINTS = {
    "slate": "bg",
    "green": "green_bg",
    "indigo": "indigo_bg",
    "amber": "amber_bg",
    "red": "red_bg",
    "cyan": "cyan_bg",
}


def _num(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def _round_up(value: float, step: int = 20) -> int:
    return int(math.ceil(value / step) * step)


class SvgFigure:
    """按内容自动计算画布大小的 SVG 画布。"""

    def __init__(self, width=None, height=None, min_width=MIN_WIDTH,
                 min_height=MIN_HEIGHT, palette=None):
        self.width = width
        self.height = height
        self.min_width = min_width
        self.min_height = min_height
        self.palette = {**PALETTE, **(palette or {})}
        self.parts: list[str] = []
        self._max_x = 0.0
        self._max_y = 0.0
        self._divider_y = None
        self._footer_lines: list[str] = []
        self._footer_y = None

    # ---------- 基础图元 ----------

    def add(self, xml: str) -> None:
        self.parts.append(xml)

    def _track(self, x, y):
        self._max_x = max(self._max_x, x)
        self._max_y = max(self._max_y, y)

    def _color(self, color):
        return self.palette.get(color, color)

    def _tint(self, color, tint=None):
        if tint:
            return self.palette.get(tint, tint)
        return self.palette.get(TINTS.get(color, "bg"), self.palette["bg"])

    def rect(self, x, y, w, h, fill="white", stroke=None, sw=1.0, rx=0):
        attrs = [
            f'x="{_num(x)}"', f'y="{_num(y)}"',
            f'width="{_num(w)}"', f'height="{_num(h)}"',
            f'fill="{self._color(fill)}"',
        ]
        if rx:
            attrs.append(f'rx="{_num(rx)}"')
        if stroke:
            attrs += [f'stroke="{self._color(stroke)}"', f'stroke-width="{_num(sw)}"']
        self.add("<rect " + " ".join(attrs) + "/>")
        self._track(x + w, y + h)

    def line(self, x1, y1, x2, y2, color="line", width=1.2, dashed=False):
        attrs = [
            f'x1="{_num(x1)}"', f'y1="{_num(y1)}"',
            f'x2="{_num(x2)}"', f'y2="{_num(y2)}"',
            f'stroke="{self._color(color)}"', f'stroke-width="{_num(width)}"',
        ]
        if dashed:
            attrs.append('stroke-dasharray="3 3"')
        self.add("<line " + " ".join(attrs) + "/>")
        self._track(max(x1, x2), max(y1, y2))

    def polygon(self, points, fill):
        pts = " ".join(f"{_num(x)},{_num(y)}" for x, y in points)
        self.add(f'<polygon points="{pts}" fill="{self._color(fill)}"/>')
        for x, y in points:
            self._track(x, y)

    def _text_xml(self, x, y, value, size=10.6, color="body", weight=None,
                  anchor=None, mono=False):
        attrs = [
            f'x="{_num(x)}"', f'y="{_num(y)}"',
            f'font-size="{_num(size)}"', f'fill="{self._color(color)}"',
            'xml:space="preserve"',
        ]
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if anchor:
            attrs.append(f'text-anchor="{anchor}"')
        if mono:
            attrs.append(f'font-family="{FONT_MONO}"')
        return "<text " + " ".join(attrs) + ">" + escape(str(value)) + "</text>"

    def text(self, x, y, value, size=10.6, color="body", weight=None,
             anchor=None, mono=False):
        self.add(self._text_xml(x, y, value, size, color, weight, anchor, mono))
        width = self._text_width(value, size)
        if anchor == "middle":
            x0 = x - width / 2
        elif anchor == "end":
            x0 = x - width
        else:
            x0 = x
        self._track(x0 + width, y + size * 0.3)
        self._track(x0, y - size * 0.8)

    # ---------- 版式组件 ----------

    def header(self, title, subtitles=(), divider_y=112):
        self.text(MARGIN, 42, title, 23, "ink", 700)
        y = 70
        for line in subtitles:
            self.text(MARGIN, y, line, 12.3, "dim")
            y += 22
        self._divider_y = divider_y
        return divider_y

    def section_title(self, x, y, title):
        self.text(x, y, title, 12.0, "ink", 700)

    def legend(self, items, x=MARGIN, y=142, gap=24):
        """items: [(label, color_key), ...]；颜色可按图覆盖。"""
        cursor = x
        for label, color in items:
            self.line(cursor, y, cursor + 30, y, color, 3)
            self.text(cursor + 38, y + 4, label, 11.0, "body", 600)
            cursor += 38 + self._text_width(label, 11.0) + gap
        return y

    def lane(self, x, y, w=108, h=90, title="", subtitle="", lines=(), color="indigo"):
        stroke = self._color(color)
        fill = self._tint(color)
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.2, rx=9)
        self.text(x + 10, y + 22, title, 10.6, "ink", 700)
        yy = y + 38
        if subtitle:
            self.text(x + 10, yy, subtitle, 9.4, "dim")
            yy += 18
        for line in lines:
            self.text(x + 10, yy, line, 9.0, "dim")
            yy += 13

    def node(self, x, y, w=220, h=76, title="", lines=(), mono_lines=(),
             color="slate", tint=None, badge=None, small=False):
        stroke = self._color(color)
        fill = self._tint(color, tint)
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.1, rx=8)
        self.rect(x, y, 4.5, h, fill=stroke, rx=2)
        title_size = 10.2 if small else 11.8
        body_size = 8.8 if small else 9.6
        self.text(x + 13, y + 19, title, title_size, "ink", 700)
        if badge:
            self.text(x + w - 9, y + 19, badge, 10.2, stroke, 700, anchor="end")
        yy = y + 36
        for line in lines:
            self.text(x + 13, yy, line, body_size, "body")
            yy += 15.4
        for line in mono_lines:
            self.text(x + 13, yy, line, body_size, "body", mono=True)
            yy += 15.4

    def flow_row(self, x, y, nodes, gap=10, node_h=82):
        """按顺序横向排节点，自动画箭头；节点数量由内容决定。

        nodes 是 dict 列表，字段同 node()；w/h 可省略。
        """
        cursor = x
        for i, spec in enumerate(nodes):
            spec = dict(spec)
            w = spec.pop("w", 158)
            h = spec.pop("h", node_h)
            self.node(cursor, y, w=w, h=h, **spec)
            if i < len(nodes) - 1:
                self.arrow(cursor + w, y + h / 2, cursor + w + gap, y + h / 2,
                           "muted", 1.5)
            cursor += w + gap
        return cursor - gap

    def arrow(self, x1, y1, x2, y2, color="slate", width=2.4,
              dashed=False, label=None, label_offset=(8, -6)):
        self.line(x1, y1, x2, y2, color, width, dashed)
        angle = math.atan2(y2 - y1, x2 - x1)
        size = 9.0
        bx = x2 - size * math.cos(angle)
        by = y2 - size * math.sin(angle)
        half = size * 0.5
        left = (bx + half * math.sin(angle), by - half * math.cos(angle))
        right = (bx - half * math.sin(angle), by + half * math.cos(angle))
        self.polygon([(x2, y2), left, right], color)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.text(mx + label_offset[0], my + label_offset[1],
                      label, 10.2, "dim", 600)

    def note(self, x, y, w, title, lines, color="amber", pad=16, line_h=18):
        stroke = self._color(color)
        fill = self._tint(color)
        h = pad * 2 + (24 if title else 0) + len(lines) * line_h
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.0, rx=10)
        yy = y + pad + 14
        if title:
            self.text(x + pad, yy, title, 10.6, "ink", 700)
            yy += 24
        for line in lines:
            self.text(x + pad, yy, line, 10.2, "body")
            yy += line_h
        return y + h

    def matrix(self, x, y, w, headers, rows, row_h=30, header_h=30):
        col_w = w / len(headers)
        self.rect(x, y, w, header_h, fill="header_bg", rx=6)
        for i, header in enumerate(headers):
            anchor = "start" if i == 0 else "middle"
            tx = x + 8 if i == 0 else x + col_w * (i + 0.5)
            self.text(tx, y + 20, header, 10.0, "dim", 700, anchor=anchor)
        yy = y + header_h
        for row in rows:
            self.rect(x, yy, w, row_h, fill="white")
            self.line(x, yy, x + w, yy, "line", 0.8)
            for i, cell in enumerate(row):
                anchor = "start" if i == 0 else "middle"
                tx = x + 8 if i == 0 else x + col_w * (i + 0.5)
                color = "ink" if i == 0 else "body"
                weight = 700 if i == 0 else None
                if cell == "✓":
                    color, weight = "green", 700
                elif cell == "✗":
                    color, weight = "red", 700
                self.text(tx, yy + 20, cell, 10.0, color, weight, anchor=anchor)
            yy += row_h
        self.line(x, yy, x + w, yy, "line", 0.8)
        return yy

    def footer(self, lines, y=None):
        """记录底部说明；实际位置在 render() 时按最终高度计算。"""
        self._footer_lines = list(lines)
        self._footer_y = y

    # ---------- 输出 ----------

    def render(self):
        footer_h = 36 + 18 * len(self._footer_lines) if self._footer_lines else 36
        width = self.width or max(self.min_width, _round_up(self._max_x + MARGIN, 20))
        height = self.height or max(self.min_height, _round_up(self._max_y + footer_h, 20))

        body = []
        if self._divider_y is not None:
            body.append(
                f'<line x1="{MARGIN}" y1="{_num(self._divider_y)}" '
                f'x2="{width - MARGIN}" y2="{_num(self._divider_y)}" '
                f'stroke="{self._color("line")}" stroke-width="1.2"/>'
            )
        body.extend(self.parts)

        if self._footer_lines:
            y = self._footer_y or (height - MARGIN - 18 * (len(self._footer_lines) - 1))
            for line in self._footer_lines:
                body.append(self._text_xml(MARGIN, y, line, 12.3, "dim"))
                y += 18

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" '
            f'font-family="{FONT_SANS}">\n'
            f'<rect width="{width}" height="{height}" fill="{self._color("white")}"/>\n'
            + "\n".join(body) + "\n</svg>\n"
        )

    def save(self, path):
        Path(path).write_text(self.render(), encoding="utf-8")

    @staticmethod
    def _text_width(value, size):
        # 粗略估算：中文按 1em，英文/数字按 0.6em。
        return sum(size if ord(ch) > 127 else size * 0.6 for ch in value)


def build_example() -> SvgFigure:
    # 不指定 width/height：由内容自动计算。
    f = SvgFigure()
    f.header(
        "图 0 · 流程与矩阵（模板示例）",
        [
            "所有图共用默认字体和组件；画布宽高、泳道数量、颜色都按内容调整。",
            "读法：先看图例，再看泳道；颜色只是辅助，文字标签才是主要依据。",
        ],
    )
    f.legend([
        ("共用段", "slate"),
        ("路径 A", "green"),
        ("路径 B", "indigo"),
        ("路径 C", "amber"),
    ])

    # 三条泳道只是示例，实际可以是 1-N 条。
    f.section_title(36, 176, "① 泳道：数量按内容决定")

    f.lane(36, 190, title="路径 A", subtitle="（示例）",
           lines=["第一步", "第二步"], color="green")
    f.flow_row(154, 190, [
        dict(title="接收", lines=["输入数据", "或事件"], color="indigo", small=True),
        dict(title="判断", lines=["满足条件？", "走哪条路径"], color="indigo", small=True),
        dict(title="处理", lines=["执行动作", "记录结果"], color="green", badge="A", small=True),
        dict(title="返回", lines=["输出结果", "结束"], color="green", badge="A", small=True),
    ])

    f.lane(36, 302, title="路径 B", subtitle="（示例）",
           lines=["第一步", "第二步"], color="indigo")
    f.flow_row(154, 302, [
        dict(title="接收", lines=["输入数据", "或事件"], color="indigo", small=True),
        dict(title="判断", lines=["满足条件？", "走哪条路径"], color="indigo", small=True),
        dict(title="分流", lines=["交给其他", "模块处理"], color="indigo", badge="B", small=True),
        dict(title="输出", lines=["继续传递", "或落盘"], color="indigo", small=True),
    ])

    f.lane(36, 414, title="路径 C", subtitle="（示例）",
           lines=["本机产生", "新的数据"], color="amber")
    f.flow_row(154, 414, [
        dict(title="生成", lines=["构造数据", "或请求"], color="amber", badge="C", small=True),
        dict(title="处理", lines=["执行动作", "记录结果"], color="amber", small=True),
        dict(title="发送", lines=["交给下游", "或设备"], color="green", small=True),
    ])

    # 右侧矩阵：宽度按列数和内容给定，不依赖固定画布宽度。
    f.section_title(1024, 176, "② 矩阵：行列数按内容决定")
    f.matrix(
        1024, 190, 600,
        ["对象 ＼ 阶段", "准备", "执行", "检查", "输出", "归档"],
        [
            ["对象 A", "✓", "", "", "✓", ""],
            ["对象 B", "✓", "✓", "✓", "✓", "✓"],
            ["对象 C", "✓", "", "", "✓", "✓"],
            ["对象 D", "", "✓", "✓", "✓", ""],
            ["对象 E", "", "✓", "✓", "✓", ""],
        ],
    )

    f.note(
        1024, 390, 600, "读图顺序",
        [
            "① 先看图例：颜色分别代表什么？",
            "② 再看泳道：每一步在哪个阶段发生？",
            "③ 最后看矩阵：对象和阶段如何对应？",
        ],
        color="amber",
    )

    f.footer([
        "模板：.图表模板/svg-figure-template.py",
        "改图时优先复制本脚本，不要手改 SVG；生成后检查 XML 和 Markdown 图片链接。",
    ])
    return f


if __name__ == "__main__":
    out = Path(__file__).with_name("example.svg") if len(sys.argv) < 2 else Path(sys.argv[1])
    build_example().save(out)
    print(f"wrote {out}")
