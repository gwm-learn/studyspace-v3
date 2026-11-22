#!/usr/bin/env python3
"""生成 .图表模板/examples/ 下的图型示例。

每个示例只演示一种图型，改图时直接复制对应函数即可。
"""
import importlib.util
from pathlib import Path

BASE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "svgfig", BASE.parent / "svg-figure-template.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
SvgFigure = mod.SvgFigure


def stack_example():
    """层叠结构：分区表 / 协议栈 / 镜像层。配 bracket 做分组。"""
    f = SvgFigure()
    f.header("示例 01 · 层叠结构（stack + bracket）",
             ["左侧单列、右侧分组；层数由内容决定，不写死。"])
    f.legend([("引导区", "slate"), ("系统镜像", "indigo"), ("配置层", "green")])

    f.section_title(40, 178, "单槽")
    b1 = f.stack(40, 190, 300, [
        dict(label="u-boot", tag="引导", color="slate"),
        dict(label="u-boot-env", tag="环境变量", color="slate"),
        dict(label="kernel", tag="内核", color="indigo"),
        dict(label="rootfs", tag="只读", color="indigo"),
        dict(label="rootfs_data", tag="overlay", color="green"),
    ])

    f.section_title(420, 178, "A/B 槽")
    b2 = f.stack(420, 190, 340, [
        dict(label="u-boot", tag="引导", color="slate"),
        dict(label="u-boot-env", tag="槽位 · 计数", color="slate"),
        dict(label="kernel_A", tag="内核 A", color="indigo"),
        dict(label="rootfs_A", tag="系统 A", color="indigo"),
        dict(label="kernel_B", tag="内核 B", color="indigo"),
        dict(label="rootfs_B", tag="系统 B", color="indigo"),
        dict(label="rootfs_data", tag="共用", color="green"),
    ])
    f.bracket(776, 278, 360, "A 槽", "indigo")
    f.bracket(776, 366, 448, "B 槽", "indigo")

    f.note(40, max(b1, b2) + 30, 740, "什么时候用",
           ["有明确的上下层/分区顺序，且每层要带一句说明时用 stack。",
            "分组关系用 bracket，不要靠留白暗示；说明框放在 stack 返回值之后，别写死 y。"],
           color="amber")
    f.footer(["示例：.图表模板/examples/01-stack.svg"])
    f.save(BASE / "01-stack.svg")


def sequence_example():
    """时序图：协议交互、握手、跨组件调用。"""
    f = SvgFigure()
    f.header("示例 02 · 时序图（sequence）",
             ["竖向是参与者，横向是消息；虚线是生命线，不要画成实体框。"])
    f.legend([("控制面", "indigo"), ("空口", "green"), ("可选/拒绝", "muted")])

    f.sequence(40, 190, [
        ("Controller", "indigo"),
        ("Agent A（旧）", "green"),
        ("Agent B（新）", "green"),
        ("终端 STA", "amber"),
    ], [
        dict(frm=1, to=0, label="① 上报终端与链路"),
        dict(frm=0, to=1, label="② Steering Request"),
        dict(frm=0, to=2, label="③ 通知准备"),
        dict(frm=1, to=3, label="④ 11k 邻居报告"),
        dict(frm=1, to=3, label="⑤ 11v BTM Request"),
        dict(frm=3, to=1, label="⑥ BTM Response", dashed=True, color="muted"),
        dict(frm=1, to=0, label="⑦ BTM Report"),
        dict(frm=3, to=2, label="⑧ 重关联 + FT"),
        dict(frm=2, to=0, label="⑨ 已上线"),
    ])

    f.note(40, 606, 900, "什么时候用",
           ["有先后顺序、且要看清「谁对谁说」时用时序图。",
            "只有步骤没有交互对象时，用 flow_row（流程行）更省地方。"],
           color="amber")
    f.footer(["示例：.图表模板/examples/02-sequence.svg"])
    f.save(BASE / "02-sequence.svg")


def graph_example():
    """有向图 / DAG：提交历史、依赖关系、变基前后。"""
    f = SvgFigure()
    f.header("示例 03 · 有向图（graph）",
             ["节点用 chip，边自动选边、可走直角；分支图不要手连斜线。"])
    f.legend([("主分支", "indigo"), ("中间分支", "slate"), ("被移动的段", "amber")])

    f.section_title(40, 178, "变基前")
    f.graph([
        dict(id="A", x=40, y=200, label="A", color="indigo"),
        dict(id="B", x=120, y=200, label="B", color="indigo"),
        dict(id="C", x=200, y=200, label="C", color="indigo"),
        dict(id="N1", x=200, y=270, label="N1", color="slate"),
        dict(id="N2", x=280, y=270, label="N2", color="slate"),
        dict(id="T1", x=360, y=340, label="T1", color="amber"),
        dict(id="T2", x=440, y=340, label="T2", color="amber"),
    ], [
        {"from": "A", "to": "B"}, {"from": "B", "to": "C"},
        {"from": "B", "to": "N1"}, {"from": "N1", "to": "N2"},
        {"from": "N2", "to": "T1"}, {"from": "T1", "to": "T2"},
    ])

    f.section_title(560, 178, "变基后")
    f.graph([
        dict(id="A", x=560, y=200, label="A", color="indigo"),
        dict(id="B", x=640, y=200, label="B", color="indigo"),
        dict(id="C", x=720, y=200, label="C", color="indigo"),
        dict(id="T1", x=880, y=340, label="T1′", color="amber"),
        dict(id="T2", x=960, y=340, label="T2′", color="amber"),
    ], [
        {"from": "A", "to": "B"}, {"from": "B", "to": "C"},
        {"from": "C", "to": "T1", "color": "amber"},
        {"from": "T1", "to": "T2", "color": "amber"},
    ])
    f.text(560, 300, "next：N1、N2 未变，省略不画", 9.4, "dim")

    f.note(40, 420, 960, "什么时候用",
           ["有分叉、合并、依赖方向时用 graph；线性步骤用 flow_row。",
            "边交给 edge_boxes 自动选边；节点挡路时，删掉无关分支比强行绕线更清楚。"],
           color="amber")
    f.footer(["示例：.图表模板/examples/03-graph.svg"])
    f.save(BASE / "03-graph.svg")


def decision_example():
    """决策 / 分流：排障路径、报错分类、选型判断。"""
    f = SvgFigure()
    f.header("示例 04 · 决策分流（decision）",
             ["一个根、N 个分支，每支给一句「动作」；分支数由内容决定。"])
    f.legend([("补历史", "indigo"), ("权限", "amber"), ("冲突", "cyan"), ("危险", "red")])

    f.decision(40, 180, 1000, dict(title="push 被拒", lines=["先读报错关键词"]), [
        dict(title="① 非快进", lines=["non-fast-forward", "远程有你没有的提交"],
             color="indigo", action="fetch → merge/rebase → 再 push"),
        dict(title="② 权限", lines=["403 / Permission denied", "protected branch"],
             color="amber", action="走 PR；查 PAT / SSH key"),
        dict(title="③ 引用冲突", lines=["tag 已存在", "shallow update not allowed"],
             color="cyan", action="换名，或 fetch --unshallow"),
        dict(title="④ 硬推", lines=["绕过非快进", "别人的提交被抹掉"],
             color="red", action="只对个人分支用 --force-with-lease"),
    ])

    f.note(40, 440, 1000, "什么时候用",
           ["知道「有几种可能」但需要按证据分流时用 decision。",
            "分支超过 5 个就说明该拆图，或改成矩阵。"],
           color="amber")
    f.footer(["示例：.图表模板/examples/04-decision.svg"])
    f.save(BASE / "04-decision.svg")


def timeline_example():
    """时间线：版本演化、协议阶段、历史里程碑。"""
    f = SvgFigure()
    f.header("示例 05 · 时间线（timeline）",
             ["横轴是时间，菱形是节点；说明文字上下交错，避免挤在一行。"])
    f.legend([("规范版本", "indigo"), ("能力增强", "green")])

    f.timeline(80, 250, 840, [
        dict(label="R1", sub="2018 · 基础组网", color="indigo", above=True),
        dict(label="R2", sub="2019 · 诊断/隔离", color="green"),
        dict(label="R3", sub="2021 · 6 GHz", color="indigo", above=True),
        dict(label="R4", sub="2022 · 多介质", color="green"),
        dict(label="R5", sub="2024 · Wi-Fi 7", color="indigo", above=True),
    ])

    f.note(80, 330, 840, "什么时候用",
           ["有明确先后、且重点是「什么时候发生了什么」时用 timeline。",
            "要表达因果或分叉，用 graph；要表达步骤，用 flow_row。"],
           color="amber")
    f.footer(["示例：.图表模板/examples/05-timeline.svg"])
    f.save(BASE / "05-timeline.svg")


if __name__ == "__main__":
    stack_example()
    sequence_example()
    graph_example()
    decision_example()
    timeline_example()
    print("ok")
