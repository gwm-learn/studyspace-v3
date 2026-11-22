---
name: Knowledge Base Refactor
description: 把任意素材（源仓库、网页/博客、文档链接、粘贴的对话文本、PDF/幻灯片、drawio/既有笔记）重构为目标知识库的分层笔记：边界划分、素材可信度分级与事实核对、笔记模板、SVG 配图、三列名词解释、全量审计与提交规范
---

# Knowledge Base Refactor

Use this skill when the user asks to **create or fill notes in a knowledge directory**, whatever the material is: another repository, a blog post, a doc link, a pasted chat log, slides, or a pile of drawio files.

Typical triggers:

- "把 studyspace 的内容重构到 studyspace-v3/xx"
- "把这几个链接/博客整理成一篇笔记"
- "我把和豆包/AI 的对话贴给你，整理进 xx"
- "按 netfilter 那篇的模板写"
- "补齐图、名词解释、英文全称"
- "扫描所有文档，看图/术语/索引是否完整"

**Not this skill:** 目标笔记已经存在、要加深/重写/丰富 → 用 `knowledge-enrich`。本技能负责"从素材到第一篇"，那个负责"第二遍及以后"。

## Non-negotiables

1. **先定边界，再动笔**：目标目录只写它该管的层；实现细节、产品方案、厂商 SDK 链接到其他目录，不复制。
2. **一篇一个主题**：同一主题只保留一个正本，其他位置链接。
3. **单篇串行**：一次只重构一篇；读完素材 → 提纲 → 成篇 → 自检/评审 → 过门禁再开下一篇。
4. **不编造**：RFC/端口/函数/寄存器/默认值无法核对时，写"待验证"，不写"大概"。
5. **不写三类内容**：`抓包`、`常见坑`、`命令速查` 章节不要；需要时把可观测现象写进"设计取舍与边界"。
6. **图要放在流程章节**，不能只堆在文档开头；每张图配"读图"说明。
7. **缩写必须给英文全称**：术语表三列：术语 / 英文全称 / 解释；非缩写用 `—`。
8. **不自动 commit/push**，除非用户明确要求。
9. **素材要分级，不把二手当一手**：博客、AI 回答、公众号、二手教程都是二手，结论必须核对；核对不了的写"待验证"（见 §2）。
10. **取不到就停**：登录墙、JS 空壳页、需要扫码/付费的链接，先向用户要正文；**不要用记忆补全**。

## Workflow

### 1. Scope and ownership

- Read `AGENTS.md`, root `README.md`, target `.readme.md`.
- Write a boundary table: target directory vs source directories vs "只链接不搬" 的目录。
- Decide the target note list before writing. Number files `NN-主题.md`.
- 如果用户只给了素材、没说放哪：先按现有目录结构提议落点，得到确认再写。

### 2. Ingest the source

素材形态决定了取用方式、可信度和落库要求。**先判断形态，再决定流程**。

#### 2.1 六种形态

| 素材形态 | 怎么取 | 可信度 | 落库要求 |
|---|---|---|---|
| 本地仓库/目录 | `find`/`grep`，先读索引再读正文 | 一手（代码/配置/输出为准） | footer 记仓库内相对路径 |
| 单文件 md/html | 直接读；大文件先 grep 标题/关键词 | 视来源 | 大 HTML 只提取章节，不整篇塞 |
| 网页/博客/文档站 | `webfetch`（先 markdown，失败换 `html`，再不行找官方文档或镜像） | 二手 | footer 记 URL + 访问日期 |
| 分享链接（登录墙、JS 壳） | 先试；返回空壳（如 `shareInfo: {}`、`请登录`、`account_info_error`）即判定不可用 | 不可用 | **停下来让用户粘贴正文** |
| 粘贴文本（对话/聊天/邮件） | 直接当素材；先拆成"结论 / 依据 / 引用"三栏再动笔 | 二手 | footer 注明"用户提供" |
| PDF/幻灯片 | 只提炼结构与结论；图不搬，必要时重画 | 二手 | 需要时记页码 |
| drawio/svg | 抽 label 当提纲（脚本见 2.4） | 一手（设计意图） | 不直接嵌入成品，重画为统一风格 SVG |

判定不可用时，给用户三个选项而不是一个死胡同：① 粘贴正文；② 换公开来源；③ 由我按一手资料（规范/源码/官方文档）写，无法核对的标"待验证"。

#### 2.2 按断言分级，不按文档分级

同一篇博客里，可能既有可用的结论，也有错的事实。**逐条判，不整篇信**：

| 级别 | 例子 | 写法 |
|---|---|---|
| 一手 | 规范原文、上游源码、设备实际配置/输出、官方 wiki | 直接写，附引用位置 |
| 二手 | 博客、AI 汇总、厂商白皮书、二手教程 | 至少一处一手或两处独立二手印证，否则 `待验证` |
| 推断 | 从机制推出的结论（"因此不会…"） | 必须写出前提；前提变了结论就失效 |

冲突时**以一手为准**，并在正文里说明"常见说法 X，实际 Y"，而不是静默改掉——读者可能正带着那个错误认知来。

#### 2.3 必须核对的五类断言

这几类最容易在二手素材里出错，也最容易污染整个知识库：

| 断言类型 | 典型错法 | 核对位置 |
|---|---|---|
| 标准归属/版本/年份 | 把商品名当 IEEE 标准；把已撤销的标准当现行 | 标准编号页、状态（active/withdrawn） |
| 进程/包/二进制名 | 不同实现分支命名不同，被写成"都没有/都有" | 上游仓库、发行版包索引 |
| 默认值/阈值/超时 | 版本升级后默认值变了 | 官方文档、源码里的默认赋值 |
| 地址/端口/以太类型/消息编号 | 记忆串号 | 规范表格、官方解析文档 |
| "某实现必须 X" | 依赖具体版本、补丁集、profile | 该实现的部署文档 |

核对完在报告里写"修正 N 处"，让用户知道二手素材被动过哪里。

#### 2.4 Inventory the material

- `find`/`grep`；把每份 md/drawio 标成 **thick / medium / thin**（能直接撑起一节 / 只能补一段 / 只有标题）。
- drawio 抽 label：

  ```bash
  python3 - <<'PY'
  import re,html,sys
  s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
  vals=[]
  for v in re.findall(r'value="([^"]*)"',s):
      v=html.unescape(re.sub(r'<[^>]+>',' ',v))
      v=re.sub(r'\s+',' ',v).strip()
      if v and v not in vals: vals.append(v)
  print('\n'.join(vals))
  PY
  ```

- Map each target note to a **primary source**; 标明是 merge / 补写 / 新写。
- 素材只够写半篇时：先写能撑住的部分，剩下标"待补"，不要用废话填满。

### 3. Build the note

Use `references/note-template.md`:

1. 一句话结论与边界
2. 速览
3. 报文/结构/字段
4. 交互/流程
5. 状态机与定时器（没有就写明）
6. 设计取舍与边界
7. 与相邻主题的关系
8. 参考与关联

Add a three-column `## 名词解释` before references, and a TOC entry `- [名词解释](#名词解释)`.

文风基准：`20-平台与系统/21-Linux/06-网络子系统/01-netfilter/netfilter框架入门.md`。它的标志性手法（"为什么"先行、表格带边界列、推论 blockquote、编号走查）见 `../knowledge-enrich/references/golden-sample-dna.md`。

### 4. Figures

Follow `references/figure-workflow.md`.

- Use `.图表模板/svg-figure-template.py`; do not hand-write SVG.
- Put figures in the note's `images/`, named `图NN-主题.svg`；**编号接着目录里已有的往下排**，不要从 01 重来。
- Insert **inside the relevant section**, not at the top:
  ```markdown
  ![图 NN · 主题](images/图NN-主题.svg)

  **读图**：先看什么、箭头代表什么、边界在哪。

  > 图源：`images/图NN-主题.svg`
  ```
- Generate `images/.readme.md` with one-line descriptions.
- Validate XML, canvas overflow, and Markdown image links.

### 5. Glossary

- Three columns: `术语 | 英文全称 | 解释`.
- Expand every abbreviation; keep non-abbreviations as `—`.
- Watch context conflicts, e.g. VLAN `PCP` = Priority Code Point vs UPnP `PCP` = Port Control Protocol.
- Add TOC entry before `参考与关联`.

### 6. Indexes and SSOT

- Update the target directory `.readme.md`: links + one-line summaries + figure count.
- Update parent `.readme.md` counts.
- If a protocol/term matrix exists, update it before writing the note; it is the SSOT.

### 7. Audit

Run:

```bash
python3 .opencode/skills/knowledge-refactor/scripts/audit_kb.py <target-dir>
```

It checks:

- note count, SVG count, image references
- dead links
- forbidden headings (`抓包`/`常见坑`/`命令速查`)
- missing `layer:` frontmatter
- glossary presence, 3-column shape
- figures per note
- image refs that are not files

Also scan "framework/flow sections without a figure":

```bash
python3 .opencode/skills/knowledge-refactor/scripts/audit_kb.py <target-dir> --figure-gaps
```

脚本不检查素材可信度——那部分靠 §2.3 的人工核对和 footer 的来源记录。

### 8. Commit

Only when explicitly asked:

```bash
git add <target-dir>
git commit -m "docs(<scope>): <subject>" -m "<body>"
```

- Subject ≤50 chars, no trailing period.
- Must pass `.githooks/commit-msg`.
- Do not push unless asked.

## Review gate per note

Score 0/1 on:

1. 开头一句话结论 + 可复述模型
2. 为什么需要、不用会怎样
3. 字段/结构表完整，含作用与坑
4. 正常流程 + 异常分支
5. 适用边界/反例
6. 状态机/定时器（或明确"没有"）
7. 与相邻主题关系
8. 标准与关联链接
9. 图在对应章节 + 读图说明
10. 名词解释三列 + 英文全称

Pass: ≥9/10 and items 1/4/9/10 must pass. Otherwise rewrite the weak sections.

Additional gates (must also pass):

- **来源可追溯**：footer 有素材来源（仓库路径 / URL+访问日期 / 用户提供），二手断言要么已核对、要么标了"待验证"。
- **没有静默矛盾**：同一事实在正文里只有一种说法。

## Supporting files

- `references/note-template.md` — 8-section skeleton + glossary block + source footer
- `references/quality-checklist.md` — 素材门禁、rubric、完备性、审计命令
- `references/figure-workflow.md` — SVG generation, placement, common layout bugs
- `scripts/audit_kb.py` — generic audit script（`knowledge-enrich` 复用同一份，不复制）

## Failure modes to avoid

- Putting all figures at the document top.
- One figure per document regardless of multiple flows.
- Glossary without English full names.
- Duplicating implementation details from another directory.
- Writing many notes in parallel and leaving link/index debt.
- Adding figures without checking XML/canvas overflow.
- Using `qlmanage` thumbnails to judge wide SVGs (it crops); use `sips -s format png`.
- **把登录墙/空壳页面的"没有内容"当成"这个主题没有内容"，然后用记忆补全。**
- **把一篇博客的结论当规范结论**，或把 AI 回答里的进程名、默认值、版本号直接抄进正文。
- **静默改掉原文的错误**，导致读者带着旧认知看新结论时对不上。
- 素材不够就注水凑长度（正确做法：标"待补"，或缩短篇幅）。
