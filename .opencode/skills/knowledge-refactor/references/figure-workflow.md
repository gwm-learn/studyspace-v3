# 配图工作流

## 1. 原则

- 图放在**对应流程/框架章节**，不是文档开头。
- **先选图型**：按 `.图表模板/figure-style.md` §2.1 判断知识点属于哪类（分层 / 交互 / 依赖 / 分流 / 演化 / 线性步骤 / 多选对比），再选组件。不要默认 `node` + `flow_row`。
- 一张图只回答一个问题：路径、分层、状态、拓扑、对比。
- 同一篇有多个独立流程时，各配一张；不要用一张图硬塞。
- 图是结构示意，不追求截图级细节；文字解释放"读图"。

## 2. 模板

只用 `.图表模板/svg-figure-template.py`，不要手写 SVG。

```python
import importlib.util
spec = importlib.util.spec_from_file_location(
    "svgfig", "/path/to/.图表模板/svg-figure-template.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SvgFigure = mod.SvgFigure
```

常用组件：

| 方法 | 用途 |
|---|---|
| `header(title, subtitles)` | 标题/副标题/分隔线 |
| `legend(items)` | 图例 |
| `node(x,y,w,h,title,lines,color)` | 节点 |
| `flow_row(x,y,nodes)` | 横向流程 + 箭头 |
| `arrow(...)` | 箭头/标签 |
| `note(x,y,w,title,lines)` | 读图/边界说明 |
| `matrix(x,y,w,headers,rows)` | 矩阵/表 |
| `lane(...)` | 泳道 |
| `footer(lines)` | 底部来源 |
| `stack(x,y,w,rows)` | 层叠：分区表、协议栈、镜像层 |
| `bracket(x,y1,y2,label)` | 分组括号（A 槽 / B 槽） |
| `sequence(x,y,lanes,messages)` | 时序：谁对谁说什么 |
| `graph(nodes,edges)` / `edge_boxes(a,b)` | 有向图 / DAG，自动选边 |
| `chip(x,y,label)` | 小标签块（DAG 节点、状态） |
| `decision(x,y,w,root,branches)` | 决策分流（报错分类、排障路径） |
| `timeline(x,y,w,items)` | 时间线（版本、代际） |

图型与组件的对应关系见 `figure-style.md §2.1`；可复制样板在 `.图表模板/examples/`（层叠、时序、有向图、决策、时间线各一张）。

默认语义色：`indigo` 主路径、`green` 成功/就绪、`amber` 注意/延后、`red` 风险、`cyan` 辅助、`slate` 中性。

## 3. 生成脚本结构

```python
BASE = Path("target/dir")

def newfig(title, subs):
    f = SvgFigure()
    f.header(title, subs)
    return f

def finish(f, sub, name):
    d = BASE / sub / "images"
    d.mkdir(parents=True, exist_ok=True)
    f.footer([...])
    f.save(d / name)
```

每篇一个规格：

```python
flow("02-链路层", "图01-ARP同网段与跨网段.svg",
     "图 01 · ARP：问的是下一跳",
     ["同网段问目的主机，跨网段问网关。"],
     [dict(title="查缓存", lines=["命中直接封装"], color="slate"), ...],
     ["请求广播，应答单播。"])
```

## 4. 插入 Markdown

```markdown
![图 01 · ARP 同网段与跨网段](images/图01-ARP同网段与跨网段.svg)

**读图**：上行同网段问目的主机，下行跨网段问网关；请求广播、应答单播。

> 图源：`images/图01-ARP同网段与跨网段.svg`
```

不要只写“图源”，必须有“读图”。

## 5. 常见排版坑

### 5.1 图例压住节点

模板图例默认 `y=142`，正文节点从 `y=190` 开始。节点放在 `y<190` 会压住图例。**顶层节点从 190 起。**

### 5.2 箭头穿过文字

节点正文从 `y+36` 开始，箭头若从侧面中心进入会顶到第一行文字。让边从 `y+h-12` 进入（或从顶部/底部进入）：

```python
def boundary(n, toward):
    ...
    if abs(dx) >= abs(dy):
        return (x + w if dx > 0 else x, y + h - 12)
    return (cx, y + h if dy > 0 else y)
```

### 5.3 标签重叠

短边（<80px）不要放长标签；宁可删标签，让节点文字解释。长标签只在宽间距使用。

### 5.4 多余的右括号

批量追加规格时容易出现 `..."]))`，应为 `..."])`。生成前先 `python3 script.py` 看语法错误行。

### 5.5 宽图预览被裁切

- `qlmanage` 会按方形缩略图裁切宽图，**不要用它判断**。
- 用 `sips -s format png x.svg --out /tmp/x.png`，按原始宽高渲染。

## 6. 生成后校验

```bash
python3 - <<'PY'
import re,glob,xml.etree.ElementTree as ET
for p in glob.glob('**/images/*.svg', recursive=True):
    ET.parse(p)
    s=open(p,encoding='utf-8').read()
    w=float(re.search(r'width="([\d.]+)"',s).group(1))
    h=float(re.search(r'height="([\d.]+)"',s).group(1))
    mx=my=0
    for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',s):
        x,y,rw,rh=map(float,m.groups()); mx=max(mx,x+rw); my=max(my,y+rh)
    for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*font-size="([\d.]+)"[^>]*>([^<]*)',s):
        x,y,fs=map(float,m.groups()[:3]); t=m.group(4)
        tw=sum(fs if ord(c)>127 else fs*.6 for c in t)
        mx=max(mx,x+tw); my=max(my,y+fs*.3)
    if mx>w-2 or my>h-2:
        print('OVERFLOW',p,mx,my,w,h)
print('done')
PY
```

## 7. 图片索引

每个 `images/` 目录补 `.readme.md`：

```markdown
# 图片索引

本目录存放 XX 篇的插图，由 `.图表模板/svg-figure-template.py` 生成。

- [图01-xxx.svg](./图01-xxx.svg)：一句话说明。
```

并在所属目录 `.readme.md` 的“图表”一节链接 `images/`。
