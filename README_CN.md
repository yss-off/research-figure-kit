# Research Figure Kit（科研配图工具箱）

[English](README.md)

![Research Figure Kit](assets/social/research-figure-kit-x-launch.png)

> Research figures you can edit, check, and reproduce.

Research Figure Kit 是一个面向 Codex 的开源科研配图插件工程。它解决的不是“快速生成一张看起来像论文图的图片”，而是让关系图和数据图同时具备：

- 可编辑的规范源；
- 可重复执行的生成流程；
- 明确的视觉、语义和出版检查；
- 可追溯的来源、版本、artifact 和验证证据。

项目内部保留四个独立 skill，由一个插件统一安装：

- `drawio`：YAML-first、offline-first 的通用 draw.io 能力；
- `drawio-academic-skills`：论文、学位论文和技术文档中的架构、机制、流程及路线图；
- `drawio-poster`：品牌服务流程海报、手机阅读检查、简洁备注和局部修订；
- `scientific-visualization`：基于 Matplotlib、Seaborn 或 Plotly 的数据剖析、统计视觉编码和出版导出审查。

关系图和数据图共享发布治理，但不混用绘制后端：关系图始终保留可编辑 `.drawio`，数据图保留数值变量、变换和统计证据。

## 主要能力

- 从 YAML 生成并验证可编辑 Draw.io 图；
- 对复杂图比较 2–3 个结构化布局方案；
- 记录节点、边、禁止边、禁止误读和跨域支撑区；
- 检查箭头方向、回路、标签归属、字体回退、黑白打印和目标页面可读性；
- 为 Word、论文和投稿场景区分 `raster-publication`、`vector-submission` 与 `draft-preview`；
- 只读剖析 CSV/TSV，并审计缺失值、不确定性、重复单位和统计视觉编码；
- 生成带哈希、渲染器、证据状态和残余风险的 figure manifest；
- 离线执行核心生成、验证和打包流程。

## 安装

克隆仓库并将其作为本地 Codex marketplace 添加：

```bash
git clone https://github.com/yss-off/research-figure-kit.git
cd research-figure-kit
codex plugin marketplace add .
codex plugin add academic-figure-skills@research-figure-kit
```

确认插件已加载：

```bash
codex plugin list --json --available
```

插件默认的 YAML/Draw.io 和数据图工作流可以离线运行。`drawio/.mcp.json` 中的实时浏览器后端是可选能力，首次使用会通过 `npx` 获取其固定版本，不是普通生成和验证的前提。

## 使用示例

```text
使用 drawio-academic-skills，把这段方法描述画成可编辑的论文流程图，先比较布局方案。
```

```text
使用 scientific-visualization，先只读检查 results.csv，再选择能如实表达不确定性的图形。
```

```text
编辑这个 .drawio，保持节点和科学关系不变，只修复箭头、标题和A4页面可读性。
```

## Skill 路由

| 请求核心 | 使用的 skill |
|---|---|
| 非出版用途的通用 Draw.io、系统架构、网络拓扑、UML、流程图或 `.drawio` 编辑 | `drawio` |
| 论文、学位论文、投稿或 Word 技术文档中的关系图、机制图、架构图和路线图 | `drawio-academic-skills` |
| 数值变量、重复单位、缺失值、不确定性、统计视觉编码或 Matplotlib/Seaborn/Plotly | `scientific-visualization` |
| 同一交付物包含关系图与数据图 | 组合使用后两个 skill，并分别保留规范源和证据 |

## 工程结构

```text
.
├── .agents/plugins/marketplace.json
├── plugins/academic-figure-skills/
│   ├── .codex-plugin/plugin.json
│   ├── LICENSE
│   ├── THIRD_PARTY_NOTICES.md
│   └── skills/
│       ├── drawio/
│       ├── drawio-academic-skills/
│       └── scientific-visualization/
├── evals/routing-boundaries.json
├── tools/
├── management/
├── tests/
├── pyproject.toml
└── Makefile
```

`plugins/academic-figure-skills/` 是可安装插件源；`management/` 保存来源、设计决定和验证记录，不会进入运行时插件包。

## 开发与验证

```bash
make test                # 三个 skill 的聚焦回归
make test-routing        # 跨 skill 路由契约
make check               # 插件、版本、JSON、CLI 和回归校验
make check-plugin        # Codex 插件 manifest 校验
make check-base          # bundled drawio 与 academic overlay 兼容性
make package             # 生成确定性插件 ZIP
```

提交 pull request 前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。安全问题请按 [SECURITY.md](SECURITY.md) 私下报告，不要在公开 issue 中披露。

## 许可证与来源

本项目使用 [MIT License](LICENSE)。bundled `drawio` 固定自 `bahayonghang/drawio-skills@27dac02` v2.7.0；`scientific-visualization` 包含对 K-Dense AI `scientific-agent-skills` 的适配。完整归属、许可证文本和内嵌第三方组件说明见 [THIRD_PARTY_NOTICES.md](plugins/academic-figure-skills/THIRD_PARTY_NOTICES.md)。

项目和插件版本见 [pyproject.toml](pyproject.toml)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。
