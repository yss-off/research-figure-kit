# Contributing

感谢你改进 Research Figure Kit。提交变更前，请先说明要解决的真实绘图、验证或发布问题，并尽量提供最小可复现输入。

## 开发原则

- 保持各 skill 的职责边界：Draw.io 关系图与 Python 数据图不混用规范源和绘制后端。
- 优先修改权威源码，不回写已安装副本或插件 cache。
- 不把单个项目的术语、私有数据或敏感图例写入通用 skill；回归案例应匿名化。
- 新规则应对应可观察的失败，避免仅增加无法执行的长检查表。
- 新脚本必须有聚焦测试并实际运行。
- 保留第三方来源、固定版本和许可证归属。

## 本地检查

```bash
make test
make test-routing
make check
make check-base
make check-plugin
```

若修改插件打包内容，再运行：

```bash
make package
```

## 架构与定向验证

- `tools/project_config.py` 统一读取工程清单；验证器和两种打包入口共用配置类型与路径检查。
- `tools/archive_utils.py` 统一确定性 ZIP 写入；修改后运行 `pytest -q tests/test_project_config.py tests/test_plugin_packaging.py`，保留文件顺序、时间戳与权限语义。
- 学术 overlay 的 `figure_manifest.py` 保留公共校验入口；`_evidence.py` 执行独立证据检查，`_validation.py` 保存内部执行记录和问题归属。修改后运行 overlay smoke，再运行 `make test`、`make check-base`。
- 新增或调整证据规则时，补充组合故障用例：一层失败不能跳过另一层可执行检查，未执行的检查不能支撑 `evidence_checked`。已有 JSON 字段、CLI 退出码和审查历史语义需保持兼容。

## 路由用例与行为结果

`make test-routing` 只检查 gold 用例集，不运行模型，也不证明选中了正确 skill。
需要真实行为评估时，先确认模型运行授权，再使用相同用例、模型及指令版本比较。

```bash
python tools/score_routing.py --prompts > /tmp/routing-prompts.json
python tools/score_routing.py --results /tmp/routing-results.json
```

第一个命令只导出 `id`、原始 `prompt` 和用例集哈希，不导出预期答案或解释。
将原始 prompt 提供给评估环境，预期答案仅在运行后评分时读取。
结果 JSON 使用以下格式；每个用例记录一次实际选择及观察或日志定位信息：

```json
{
  "schema_version": "1.0",
  "gold_sha256": "从导出结果复制的哈希",
  "run_id": "本次运行标识",
  "model": "实际模型版本",
  "instruction_revision": "实际插件/指令版本及额外上下文标识",
  "observations": [
    {"id": "r01", "actual_route": "drawio-academic-skills", "evidence": "实际运行日志定位"}
  ]
}
```

评分器仅离线核对提供的记录，不验证日志真实性，也不评估后续绘图质量或组合任务的后端隔离。
用例未齐时输出 `incomplete`，整体准确率为 `null`；重复/未知 ID、过期用例集哈希或缺失记录元数据会被拒绝。
退出码：完整且全部匹配为 0，缺失或不匹配为 1，输入无效为 2。
测试中的合成结果只验证评分器，不作为模型能力证据。

## Pull Request

Pull request 应包含：

- 问题和用户可见影响；
- 修改范围及未修改边界；
- 已运行的验证命令和结果；
- 新增依赖、联网行为、许可证或兼容性变化；
- 对已有 YAML、`.drawio`、manifest 或图像输出的迁移影响。

提交代码即表示你同意按照本仓库的 MIT License 许可你的贡献。
