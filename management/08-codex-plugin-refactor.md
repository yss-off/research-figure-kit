# Codex 插件重构记录

## 决定与范围

2026-08-20，用户确认按“自包含三-skill 插件”方案重构当前工程。插件稳定标识为
`academic-figure-skills`，工程版本和插件版本统一为 `0.3.0`。本轮允许修改工程源，
首次重构阶段不安装到 `/home/yss/.codex/`；随后用户单独授权本地安装和同名 skill
冲突清理。commit、push 和发布始终未获授权。

运行时插件位于 `plugins/academic-figure-skills/`，包含：

- `drawio`：通用 draw.io base；
- `drawio-academic-skills`：论文关系图/示意图 overlay；
- `scientific-visualization`：科研数据图工作流。

工程级 `tools/`、`evals/` 和 `management/` 不由插件运行时加载。

## Draw.io base 来源与许可

- 权威上游：<https://github.com/bahayonghang/drawio-skills>
- 固定提交：`27dac02ce3b4901c844aaa623ad64c3d577c3a72`
- 上游 skill 版本：`2.7.0`
- 许可证：MIT，`Copyright (c) 2026 bahayonghang (李永航)`
- 导入范围：上游 `skills/drawio/`

没有从 `/home/yss/.codex/skills/drawio/` 复制运行时内容。该已安装副本与固定上游在
`SKILL.md`、`agents/openai.yaml`、`evals/evals.json`、`edge-quality-rules.md` 和
`visual-review.md` 上存在差异，因此继续只作为历史运行副本，不作为发布来源。

为通过当前 Codex skill schema，bundled base 对 `SKILL.md` frontmatter 做兼容调整：
将上游的 `version`、`homepage`、`compatibility`、`platforms` 和 `argument-hint` 移出
顶层允许字段，并把版本与固定提交记录到 `metadata`。未改写 base CLI、schema、renderer、
themes、palettes 或 shared workflows。

2026-09-06 补充：用户明确授权一次 base 文档修复例外，已应用 Astra 指令补丁。
上述“未改写 shared workflows”描述的是首次导入状态；当前指令文档存在本地修订，
CLI、schema、renderer、themes 和 palettes 仍未因此变更。授权、补丁及验证见
[Astra 指令修复记录](2026-09-06-astra-instruction-repair.md)；后续 rebase 需核对这些修订。

Codex plugin ingestion 只接受 skill `agents/openai.yaml` 的 `interface`、`policy` 和
`dependencies` 顶层字段，因此 bundled base 和 academic overlay 原有的说明性
`capabilities`、`prerequisites` 被移除；必要前置条件仍保留在各自 `SKILL.md`。上游
`CHANGELOG.md`、`reports/` 和安装脚本不属于插件运行时，未纳入 bundled base。

插件根目录 `THIRD_PARTY_NOTICES.md` 保留 Draw.io Skill 与 K-Dense Scientific Agent
Skills 的 MIT 归属；base 自带的 vendor/icon/shape 许可证继续原位保留。

## 验证边界

实施前，固定上游 base 已对当前 overlay 的 10 个 example/template 完成
`--validate --strict-warnings` 兼容检查并通过。

最终验证：

- `plugin-creator/scripts/validate_plugin.py`：工程源和解包后的插件均通过；
- 三个 `SKILL.md`：`skill-creator/scripts/quick_validate.py` 均通过；
- `make test`：draw.io CLI help、academic overlay 10 项 smoke、scientific visualization 6 项 smoke 通过；
- `make test-routing`：14 个 gold cases 通过；
- `make check`：插件/marketplace/三 skill 结构、版本、JSON、CLI 和回归通过；
- `make check-base`：bundled base 对 10 个 academic example/template 的 strict validation 通过；
- 解包后代表性 `system-architecture-paper.yaml` 生成 `.drawio` 和 sidecars，spec/XML 严格校验通过；
- 插件 ZIP 连续生成两次 SHA-256 一致。

产物：

- `academic-figure-skills-0.3.0.zip`：362 个文件，SHA-256 `bb1a7de4805080665cb51932f871ba8882894e0e7e6aec1017dd3cfc31c00176`；
- `drawio-2.7.0.zip`：298 个文件，SHA-256 `54d987b7e0df63787ff0d1b6744c23ba447031c3c4509d3c3a7d9c90c5ed85ca`；
- `drawio-academic-skills-0.1.0.zip`：31 个文件，SHA-256 `1676b6ba7dcd366aef5b9fc8a74e5f29e9aad5a205ada78fc4ef03ef7e5df6d9`；
- `scientific-visualization-1.2.zip`：30 个文件，SHA-256 `ab15179b57352612f98ab4fe8fa447f9a481f020c248be4827d1d99014620875`。

## 本地安装与冲突迁移

用户随后明确要求安装到本地服务器并解决与其他 skills 的冲突。实查 Codex CLI 为
`0.148.0`，安装前没有同名插件；唯一冲突来自 `/home/yss/.codex/skills/` 下三个独立
真实目录，其他活动 skill 根与 plugin cache 没有同名项。

- 本地 marketplace：`personal`，root `/home/yss/code/drawio_academic_skill`；
- 插件：`academic-figure-skills@personal` v0.3.0；
- cache：`/home/yss/.codex/plugins/cache/personal/academic-figure-skills/0.3.0`；
- `codex plugin list --json --available`：`installed=true`、`enabled=true`；
- source/cache `diff -qr` 无差异，manifest SHA-256 一致；
- cache 内 plugin validator、draw.io strict render 和 scientific profiler CLI probe 通过。

三个旧独立 skill 未删除，而是整体移入可恢复备份：

`/home/yss/.codex/skill-backups/academic-figure-pre-plugin-20260820-01/`

搬迁前后确定性树哈希一致：

- `drawio`：`ee9316c93d149bfbccaac6e1f16324861de0b43f1f40aa61f4fa720b9336f992`；
- `drawio-academic-skills`：`00e381f54ae8c34d61e6b142e8349d1559008592ece097f65ef4181e28253630`；
- `scientific-visualization`：`61b931136b1ebf040932e15cb3cb859c19b55384e0e72c8da0a17e0c18c771de`。

最终两个全新 `codex debug prompt-input` 进程各只加载一次：

- `academic-figure-skills:drawio`；
- `academic-figure-skills:drawio-academic-skills`；
- `academic-figure-skills:scientific-visualization`。

旧 `/home/yss/.codex/skills/<name>/SKILL.md` 加载计数为 0，因此同名冲突已消除。
本轮未 commit、push 或发布。
