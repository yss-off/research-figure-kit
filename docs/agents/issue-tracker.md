# Issue tracker: GitHub

工单和规格记录在 `yss-off/research-figure-kit` 的 GitHub Issues。
使用 `gh` CLI，并显式指定 `--repo yss-off/research-figure-kit`。

## 操作约定

- 发布到 issue tracker：创建 GitHub issue。
- 获取相关 ticket：读取 issue 正文、标签和评论。
- 创建或评论时，多行正文写入临时文件，使用 `--body-file`。
- 父子任务使用 GitHub sub-issues；不可用时，在子任务正文记录
  `Part of #<parent>`，并在父任务中维护任务列表。
- 阻塞关系使用 GitHub 原生 issue dependencies；不可用时，在正文记录
  `Blocked by: #<number>`。所有阻塞项关闭后，任务才可开始。
- 关闭工单前先单独发表评论，说明结果或关闭理由。
- 标签名称按 `docs/agents/triage-labels.md` 映射。

外部写入遵循根目录 `AGENTS.md` 的授权边界；
配置 tracker 本身不构成后续发布、评论或关闭工单的授权。

## Pull requests as a triage surface

**PRs as a request surface: no.**
