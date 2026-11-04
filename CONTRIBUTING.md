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

## Pull Request

Pull request 应包含：

- 问题和用户可见影响；
- 修改范围及未修改边界；
- 已运行的验证命令和结果；
- 新增依赖、联网行为、许可证或兼容性变化；
- 对已有 YAML、`.drawio`、manifest 或图像输出的迁移影响。

提交代码即表示你同意按照本仓库的 MIT License 许可你的贡献。
