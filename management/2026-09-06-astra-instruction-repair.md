# GPT-6 Astra 指令修复记录

## 范围与来源

本次请求：修复先前审查发现的 Skill 指令冲突。只修改工程源中的指令和引用，
不提交、推送、发布或安装运行副本；不修改 CLI、schema、renderer 或科学数据。

依据已核对的官方指南：

- [GPT-6 Astra prompting best practices](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices)
- [Codex AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

开始时工作树已经包含 `AGENTS.md`、三个 Skill 入口、base `visual-review.md`
及数据图 `visual_review.md` 的未提交修改；工作期间发现 playbook 已有配色和标签
措辞修改。保留这些已有修改，补齐仍冲突的引用，不将这些修改归为本次新增工作。

## 已落实的行为

- 学术 overlay 显式拥有投稿交付、配色、科学原文和确认规则；base 提供共享执行机制。
- 学术直接 XML 路径只读取技术规范，不再加载包含自动更新流程的历史上游 Skill。
- 常规几何选择可自行完成，用户明确要求的审批和未解决科学关系仍必须等待。
- 线框 `approved` 表示已完成结构检查；`decision` 记录 agent/user、证据及授权，
  不把代理自查表述为用户批准。未解决语义仍保持 `pending`，不放松 strict validator。
- 固定布局和纯外观编辑复用已有计划；节点预算建议触发可读性检查，不自动触发删减。
- 保留原文，先修换行、边界、间距和连线路径；压缩科学文字须在已授权内容编辑范围内。
- Desktop 缺失时先按交付矩阵检查允许的浏览器派生或矢量导出路径，仅报告确实缺失的产物。
- 修复轮次用于重新评估进展；相关引用不再将两轮当成无条件停止点。
- 数据图的期刊核验仅适用于有明确投稿目标的交付；探索图可完成并标明暂定规则。

## 固定上游边界

`AGENTS.md` 规定 bundled base 只通过固定权威上游 rebase 更新。2026-09-06，用户
对已准备的 5 文件文档补丁明确回复“同意”，授权本次本地文档例外。
`2026-09-06-astra-base-instructions.patch` 已应用并保留为审计记录，不能重复应用。
该授权不扩展到 runtime 代码、安装副本或后续上游更新；未来 rebase 时需核对并保留
本次规则修复，或确认上游已包含等效修复。

发布时补丁改存为零上下文 diff，避免补丁语法的空白上下文被仓库空白检查误报；
变更内容保持一致。当前审计补丁的应用/反向检查需带 `--unidiff-zero`。

补丁以本次当前工作树为输入，仅涉及 5 个文件：base `SKILL.md`、历史 XML 参考、
`color-guide.md`、`create.md` 和 `edit.md`；去除历史自动更新指令入口及命令，
统一配色/确认条件，清除 base 中竞争的学术交付默认值。没有 runtime 代码修改。

## 验证

- `make test`：通过，overlay 10 个、数据图 6 个 smoke 测试及 base CLI help。
- `make check-base`：base 补丁应用后重新执行通过，含工程/插件/skill 结构、14 个路由 case 和 10 个现有
  academic example/template 的 strict validation。
- `git diff --check`：通过。
- `git apply --check management/2026-09-06-astra-base-instructions.patch`：通过，
  应用前验证补丁与当前工作树匹配。
- `git apply management/2026-09-06-astra-base-instructions.patch`：用户授权后已执行；
  `git apply --reverse --check` 通过，确认补丁已完整应用到 5 个 base 文档。
- base 仍输出旧提示 `academic-paper profile recommends SVG export for paper-ready vector output`；
  这属于未修改的 runtime 建议，不能替代 overlay 的交付矩阵。

本轮没有执行独立 Astra 行为对照或子代理 forward test，不将文档/确定性回归通过
表述为模型行为验证通过。未改动运行时脚本，因此没有新增脚本测试或自动打包。

## 后续本地部署与 GitHub 同步

用户随后明确要求将新插件部署到本地并上传 GitHub，本节记录该新增授权范围。
工程/插件版本更新为 `0.3.3`，overlay 为 `0.1.2`，数据图为 `1.2.1`；
base 保留固定上游 `2.7.0` 来源标识和已授权的文档例外。

- `make check`、`make check-plugin` 和 `make package` 通过。
- 两次独立输出目录打包的 ZIP 逐字节一致，包含 363 个文件；SHA-256 为
  `6bfdb7e1c201c92f6f166b097be615b25ca5013906f6c8226a98888eec938ac0`。
- `codex plugin add academic-figure-skills@research-figure-kit --json` 安装成功。
- `codex plugin list --json --available` 确认 `0.3.3` 已安装并启用。
- 安装缓存的 363 个文件与 ZIP 逐字节一致；新进程 `codex debug prompt-input`
  的 Skill 根路径别名解析后，三个入口均指向 `0.3.3/skills/`。
- GitHub 目标为 `yss-off/research-figure-kit` 的 `main`；推送结果以远端提交回读为准。

本次正式版本号递增用于发布修复，不追加仅用于开发迭代的 cachebuster。
旧任务已经加载的 Skill 不会据此证明已刷新，使用新任务加载新版。
