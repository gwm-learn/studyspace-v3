# studyspace-v3

通信产品软件工程师的个人学习仓库。

## 怎么读

- 第一次进入：先读 [AGENTS.md](./AGENTS.md)，了解仓库用途、索引和上下文节约规则。
- 按主题阅读：从下面的知识地图进入对应目录，再读该目录的 `.readme.md`。
- 每个目录的 `.readme.md` 是该目录的索引，正文笔记从这里链接出去。

## 知识地图

| 目录 | 内容 |
|---|---|
| [00-关于我](./00-关于我/.readme.md) | 技术背景、技术方向、学习路线 |
| [10-基础理论](./10-基础理论/.readme.md) | 网络科学、通信科学、计算机基础 |
| [20-平台与系统](./20-平台与系统/.readme.md) | Linux、OpenWrt、嵌入式基础 |
| [30-平台与芯片](./30-平台与芯片/.readme.md) | 海思、MTK、QCA、展锐等平台差异 |
| [40-产品与方案](./40-产品与方案/.readme.md) | CPE、智能网关、FTTR、ONU/ONT 等 |
| [60-软件开发](./60-软件开发/.readme.md) | C、数据结构、Shell、Python、构建调试 |
| [80-工具与环境](./80-工具与环境/.readme.md) | Git、Docker、WSL 等 |

## 提交规范

提交信息统一使用 `.gitmessage` 模板，并由 `.githooks/commit-msg` 校验。

格式：

```text
<type>(<scope>): <subject>
```

示例：

```text
docs(network): 补充 netfilter hook 流程说明
chore(repo): 更新目录索引
```

启用：

```bash
git config commit.template .gitmessage
git config core.hooksPath .githooks
chmod +x .githooks/commit-msg
```

允许的 type：`docs`、`feat`、`fix`、`refactor`、`chore`、`test`、`style`、`perf`、`ci`、`build`、`revert`。

## 维护约定

- 新增目录必须补 `.readme.md`，说明目录用途和内容索引。
- 新增笔记后，更新所属目录的 `.readme.md` 链接。
- 目录名使用 `NN-名称`，文件使用短横线命名，不使用空格。
- 跨主题内容用链接引用，不在多个目录重复维护。
- 公开仓库不提交 SDK 源码、原理图、运营商规范、现网日志、密钥和客户信息。
