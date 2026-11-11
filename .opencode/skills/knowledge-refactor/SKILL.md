---
name: Knowledge Base Refactor
description: 将源仓库的 Markdown/drawio 素材重构为目标仓库的分层知识库，包含边界划分、笔记模板、SVG 配图、三列名词解释、全量审计与提交规范
---

# Knowledge Base Refactor

Use this skill when the user asks to **fill, refactor, or expand a knowledge directory** from another source repository, especially when the result must match an existing note style and include diagrams and glossaries.

Typical triggers:

- “把 studyspace 的内容重构到 studyspace-v3/xx”
- “按 netfilter 那篇的模板写”
- “补齐图、名词解释、英文全称”
- “扫描所有文档，看图/术语/索引是否完整”

## Non-negotiables

1. **先定边界，再动笔**：目标目录只写它该管的层；实现细节、产品方案、厂商 SDK 链接到其他目录，不复制。
2. **一篇一个主题**：同一主题只保留一个正本，其他位置链接。
3. **单篇串行**：一次只重构一篇；读完素材 → 提纲 → 成篇 → 自检/评审 → 过门禁再开下一篇。
4. **不编造**：RFC/端口/函数/寄存器无法核对时写“待验证”。
5. **不写三类内容**：`抓包`、`常见坑`、`命令速查` 章节不要；需要时把可观测现象写进“设计取舍与边界”。
6. **图要放在流程章节**，不能只堆在文档开头；每张图配“读图”说明。
7. **缩写必须给英文全称**：术语表三列：术语 / 英文全称 / 解释；非缩写用 `—`。
8. **不自动 commit/push**，除非用户明确要求。

## Workflow

### 1. Scope and ownership

- Read `AGENTS.md`, root `README.md`, target `.readme.md`, and the source index.
- Write a boundary table: target directory vs source directories vs “只链接不搬”的目录.
- Decide the target note list before writing. Number files `NN-主题.md`.

### 2. Inventory the source

- `find`/`grep` the source; classify each md/drawio as **thick / medium / thin**.
- For drawio, extract labels:
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
- Map each target note to a **primary source**; list merge/补写/新写.

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

### 4. Figures

Follow `references/figure-workflow.md`.

- Use `.图表模板/svg-figure-template.py`; do not hand-write SVG.
- Put figures in the note's `images/`, named `图NN-主题.svg`.
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
python3 scripts/audit_kb.py <target-dir>
```

It checks:

- note count, SVG count, image references
- dead links
- forbidden headings (`抓包`/`常见坑`/`命令速查`)
- missing `layer:` frontmatter
- glossary presence, 3-column shape
- figures per note
- image refs that are not files

Also scan “framework/flow sections without a figure”:

```bash
python3 scripts/audit_kb.py <target-dir> --figure-gaps
```

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
6. 状态机/定时器（或明确“没有”）
7. 与相邻主题关系
8. 标准与关联链接
9. 图在对应章节 + 读图说明
10. 名词解释三列 + 英文全称

Pass: ≥9/10 and items 1/4/9/10 must pass. Otherwise rewrite the weak sections.

## Supporting files

- `references/note-template.md` — 8-section skeleton + glossary block
- `references/quality-checklist.md` — rubric, completeness, audit commands
- `references/figure-workflow.md` — SVG generation, placement, common layout bugs
- `scripts/audit_kb.py` — generic audit script

## Failure modes to avoid

- Putting all figures at the document top.
- One figure per document regardless of multiple flows.
- Glossary without English full names.
- Duplicating implementation details from another directory.
- Writing many notes in parallel and leaving link/index debt.
- Adding figures without checking XML/canvas overflow.
- Using `qlmanage` thumbnails to judge wide SVGs (it crops); use `sips -s format png`.
