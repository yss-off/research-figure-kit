# Changelog

## 0.3.3 - 2026-09-06

- 适配 GPT-6 Astra 的指令遵循行为，明确已有授权、科学决策与常规排版的边界；
- 统一配色、方案选择、线框审查及修复轮次规则，避免重复确认和无条件停止；
- 修复学术交付矩阵、Desktop 缺失回退及探索性数据图期刊核验的冲突；
- 保留科学标签原文，清除直接 XML 路径中的历史静默更新指令；
- overlay 更新为 0.1.2，scientific-visualization 更新为 1.2.1；bundled drawio 保留上游 2.7.0 标识，文档例外授权及补丁见 management/2026-09-06-astra-instruction-repair.md。

## 0.3.2 - 2026-09-04

- 将公开仓库统一命名为 `research-figure-kit`，保留兼容的插件 ID 和三个 skill 名；
- 默认 README 改为面向全球 AI/Codex 开发者的英文首页，并保留独立中文说明；
- 新增项目主视觉、状态徽章、能力矩阵、安装示例、质量门禁和仓库导航；
- 插件公开显示名更新为 Research Figure Kit，统一作者、主页、仓库和安全报告链接；
- 新增 GitHub Actions 持续集成、固定开发依赖和 Dependabot 配置，成功构建可下载的确定性插件包。

## 0.3.1 - 2026-09-02

- 将 `drawio-academic-skills` 更新为 0.1.1，新增关系敏感图的语义边界与线框门禁；
- figure manifest 新增 `non_edges`、`forbidden_inferences`、`cross_cutting_regions`、`wireframe_gate` 和显式 `color_policy`；
- manifest 校验器可拒绝已声明禁止却实际存在的边、未知边界端点、重复禁止误读、未知跨域成员和未完成的线框门禁；
- 新增匿名语义边界回归案例、学术视觉问题分类、标题/泳道/支撑区间距审查和严格纯黑白规则；
- 增加根级 pytest 包装测试，使通用 pre-push 钩子按项目既有隔离方式运行两个同名 smoke suite；
- 完成公开仓库整备：采用 Research Figure Kit 项目名称，补充安装、贡献、安全、行为准则和 GitHub 协作模板；
- 保持 bundled `drawio` v2.7.0 上游源码不变，未同步或安装任何运行时副本。

## 0.3.0 - 2026-08-20

- 将工程重构为 `academic-figure-skills` skills-only Codex 插件，并加入 repo marketplace；
- 将运行时入口迁入 `plugins/academic-figure-skills/skills/`，工程治理文件继续留在插件外；
- 从 `bahayonghang/drawio-skills@27dac02` 引入 MIT 许可的 `drawio` v2.7.0 base，形成自包含三-skill 安装包；
- 新增插件 manifest、第三方许可归属、插件结构校验和确定性插件 ZIP；
- 保留三个 skill 的独立打包入口，未修改或同步任何已安装运行副本。

## 0.2.0 - 2026-08-20

- 将 `scientific-visualization` v1.2 权威源和来源/验收记录迁入同一工程；
- 保留 `drawio-academic-skills` 与 `scientific-visualization` 两个独立运行时入口和绘制后端；
- 将工程名称调整为 `Academic Figure Skills`，建立统一 skill 清单和独立版本字段；
- 新增跨 skill 路由 gold cases，覆盖数据图、关系图、组合图和信息不足四类请求；
- 统一双 skill 结构验证、smoke/CLI 回归、sibling-base 兼容检查和确定性独立打包。

## 0.1.0 - 2026-08-20

首个个人工程版本：

- 从已安装 overlay 基线建立独立权威源；
- 引入布局候选、许可可追溯参考索引和统一 figure manifest；
- 统一场景化学术交付合同并加入机器校验；
- 建立 overlay-local 回归、sibling-base 兼容验证和代表性 forward test；
- 将开发文档、版本、打包和验收从运行时 skill 中分离到工程根目录。

上游迁移前的历史记录保存在 `management/upstream/`。
