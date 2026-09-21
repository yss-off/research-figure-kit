# Academic Figure Skills 协作与工程约束

## 执行与完成

- 以用户要求的结果和验收条件为准。讨论、调研、审查只读；明确要求修改或修复时，完成范围内的本地改动及验证，不停在建议或计划。
- 已有授权在任务中持续有效。常规、可逆的实现选择自行判断；仅在缺失信息会实质改变结果或触及未授权边界时提问，并继续不依赖答案的工作。用户要求先讨论或冻结方案时遵守该阶段边界。
- 用户明确指令优先于本文件和 skill 指南，但不越过系统、开发者和工具权限限制。若 skill 导致暂停或额外确认，指出实际读取的 `SKILL.md` 路径、原文及适用原因，不从建议推导新的审批要求。
- 修改前检查工作目录、Git 状态和相关文件；以当前源码、配置、日志及产物为证据，保护已有用户改动。只读任务不顺带修复，不扩大到无关重构。
- 仅加载当前任务相关的 skill 和引用。小任务直接完成；多步任务维护简短计划。用户中途补充要求时调整剩余工作，保留仍然有效的目标和已完成结果。
- 默认不启动子代理；仅在用户明确要求时委派独立子任务，主代理负责整合和最终验证。独立的只读工具调用可批量执行，有依赖的修改与验证按顺序执行。
- 默认用中文简洁汇报，保留准确的路径、命令和标识符。多步工作开始前说明第一步，关键发现或方向改变时更新；完成时说明改动、实际验证、未验证项和必要的用户后续动作。
- 所需检查通过且验收条件满足后结束。检查失败时定位原因并在授权范围内修复；无法继续时报告具体阻塞和已完成部分，不把计划、工具成功提示或未执行检查当作完成证据。

## 权威源与安装边界

- `plugins/academic-figure-skills/` 是自包含 Codex 插件的唯一工程源；其 `skills/` 下的 `drawio/`、`drawio-academic-skills/`、`scientific-visualization/` 分别是通用 base、论文关系图 overlay、科研数据图的权威源。新增 `drawio-poster/` 承载非学术品牌流程海报；既有插件和三个 skill 名称保持兼容。
- `pyproject.toml` 是工程、插件和各 skill 的版本与路径清单唯一权威；插件 `.codex-plugin/plugin.json`、各 frontmatter/eval 必须同步，由 `tools/verify_project.py` 校验。读取清单获取当前版本，避免在本文件重复维护版本号。
- bundled `drawio` 固定为 `bahayonghang/drawio-skills` v2.7.0 commit `27dac02ce3b4901c844aaa623ad64c3d577c3a72`；来源同时记录于 `pyproject.toml` 和 `management/08-codex-plugin-refactor.md`，只通过固定权威上游 rebase 更新。若问题属于 base，记录证据并停止相关修改，不在 overlay 复制 runtime 修补。
- `$CODEX_HOME/skills/` 和插件 cache 中的副本不是工程源。未经明确授权，不同步、覆盖、删除或安装运行副本；不把已安装的 `drawio` 当作回写目标。
- 提交、推送、发布、外部写入、破坏性操作、付费或高成本计算须有用户明确授权。需要确认前，先完成已授权且不依赖该确认的准备与验证，使待批准结果可审阅。

## 目录与运行时范围

- 工程根目录维护版本、跨 skill 路由、开发说明和打包工具；插件目录保存 manifest、许可和运行时 skills。`management/` 只保存基线、设计决定、审计和验收记录，不得被 skill 运行时加载。
- 运行时 skill 目录只保留实际执行所需的 `SKILL.md`、`agents/`、`assets/`、`references/`、`scripts/`、`styles/`、`evals/` 和显式可选运行配置；项目 README、CHANGELOG、安装说明和 management 记录留在工程根目录。
- 不安装大型图库，不把外部图像生成或视觉模型设为必经路径，不新增联网运行依赖。

## 设计约束

- 变更保持 skill-local，overlay 薄且 `SKILL.md` 精简；共享执行继续走同一插件内 sibling base。
- `scientific-visualization` 保持 Python plotting 后端，不把 Matplotlib/Seaborn/Plotly 代码塞入 draw.io overlay，也不强迫数据图生成 `.drawio`。
- 三个 skill 共享插件版本治理和路由 gold cases，但除既有 draw.io base/overlay seam 外，不抽取会破坏独立入口的共享运行时模块。
- 数据图与关系图通过语义输入和绘制后端区分。跨 skill 请求允许组合交付，每个 panel 保留自己的规范源、生成命令、artifact 和证据。
- 对 `drawio-academic-skills`，YAML 仍是规范源；布局候选只规划语义和几何意图，不直接生成最终图片或改写科学内容。
- 参考索引只保存元数据、许可、来源、可借鉴布局特征和稳定 ID；不得把参考图内容、文字、商标或受保护构图当作可复制资产。
- manifest 记录合同、语义 inventory、布局选择、palette/font/export/QA/provenance；任何未知证据标为 `pending` 或 `not_checked`，不得伪造 PASS。
- 对 `drawio-academic-skills`，学术交付以该 skill 下 `references/docs/academic-figure-playbook.md § Academic Delivery Matrix` 为唯一选择权威：始终交付 `.drawio`，并在 `raster-publication`、`vector-submission`、`draft-preview` 中选择一个主类别；该合同不得套用到数据图后端。
- 不把启发式、VLM 评分、模板名或 venue 风格名表述为科学正确性、版权安全或投稿合规证明。

## 修改与验证

- 按变更影响选择检查，先聚焦再扩展。低影响文档修改检查 diff、路径和指令一致性；不为措辞修改新增测试或自动运行完整导出、打包流程。相关检查通过后，仅在新改动、失败或未解决疑点出现时扩大或重复验证。

| 变更或交付 | 验证入口 |
| --- | --- |
| skill 行为或运行时脚本 | 聚焦检查后运行 `make test`（各 skill smoke 回归） |
| 触发、路由或跨 skill 边界 | `make test-routing` |
| 版本、manifest、目录或工程结构 | `make check` |
| base/overlay 接口或 draw.io 示例 | `make check-base`（含 example strict validation） |
| 插件打包交付或打包工具 | `make check` 后运行 `make package`，核验确定性插件 ZIP |
| 明确要求兼容独立 skill 包 | `make package-skills` |

- 新增脚本必须实际运行；运行时脚本变更先做聚焦测试，再做插件/skill 结构验证、相关现有 example strict validation 和代表性 exported-artifact forward test。
- forward test 使用原始任务和最少上下文，不向测试代理泄露预期答案；子代理测试仍须用户明确要求。无法完成的验证明确记录为未执行及其原因，不伪造通过。
- 结束前复核最终 diff 和实际产物，确认只修改授权范围。报告检查命令及结果；文档和静态校验通过不等于模型行为或视觉质量已经实测。

<!-- GPT-6 Astra 提示适配依据（2026-09-06 核对）：
https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices
https://learn.chatgpt.com/docs/agent-configuration/agents-md
模型选择与 reasoning 配置由宿主控制，本文件仅规定仓库协作行为。
-->
