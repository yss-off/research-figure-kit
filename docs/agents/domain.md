# Domain Docs

## 阅读规则

探索领域概念或设计决策前，读取根目录 `GLOSSARY.md`，
以及 `docs/adr/` 中与当前任务相关的决策记录。

文件不存在时直接继续；由 domain-modeling 在术语或决策实际确定后
按需创建，不预先生成空词汇表或占位 ADR。

## 布局

采用 single-context：

- `GLOSSARY.md`：仓库级领域词汇表。
- `docs/adr/`：仓库级架构决策记录。

既有 `management/` 记录保留原位，相关工程约束仍以根目录
`AGENTS.md` 为准。本配置用于仓库开发，不增加插件运行时依赖。

## 使用规则

输出中的领域概念使用词汇表定义的名称。
缺失术语确有必要时，记录为待 domain-modeling 处理的缺口。
方案与既有 ADR 冲突时，明确指出冲突和重新讨论的理由。
