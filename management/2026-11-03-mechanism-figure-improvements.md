# 科研机制图复盘后的插件改进

本轮以绘图经历为问题来源，核对一手资料与当前工程后实现。仅修改
drawio-academic overlay；不修改论文、模型、图稿、bundled base 或运行缓存。

## 调研依据与采用决定

| 一手资料 | 本轮采用方式 | 不据此声称什么 |
| --- | --- | --- |
| [draw.io 固定与浮动连接](https://www.drawio.com/docs/manual/connectors/connector-fixed-vs-floating/) | 分开检查 attachment、port、route、landing；固定端口本身不是居中保证 | 不把所有端口居中规定为期刊要求 |
| [draw.io 连线标签](https://www.drawio.com/docs/manual/connectors/connector-labels/) | 优先支持的原生 edge label；实际导出再检查标签归属 | 不以 Desktop 行为证明 standalone 导出一致 |
| [Graphviz xlabel](https://graphviz.org/docs/attrs/xlabel/) | 把标签完整性和归属与路由质量分开检查 | 不新增 Graphviz 依赖或宣称已有自动排版器 |
| [Microsoft CHI 2019 人机交互指南](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/) | 对用户明确工具覆盖及错误边界；输出分层状态 | 不将文献结论当作本插件漏检率降低的证据 |
| [CheckList, ACL 2020](https://aclanthology.org/2020.acl-main.442/) | 能力维度、缺陷/正确对照、修订不变性回归 | 这是向图审查的工程迁移，并非已验证的视觉评测结论 |

资料核对日期：2026-11-03，Asia/Shanghai。参考文献用于设计依据，运行时保持离线。

## 实现

1. `scripts/figure_delivery.py` 重放严格 manifest 验证，分别汇总结构/导出、
   几何、科学证据、实际成图可读性、出版检查。只有完整记录才给
   `evidence_complete`；不自动写 accepted，不自动关闭问题，不证明科学真伪。
   `--strict` 对不完整证据返回 1；输入/输出操作错误返回 2。
2. `--previous-review` 比较旧 review 保存的上下文与当前文件，报告合同字段、
   节点/边差异、源文件/产物变化和已有问题。只报告影响，不自动判定改动获得授权。
   保留原 `start-round` 生命周期，避免另造问题台账。
3. 在既有 contract 中增加可选 `reader_questions`，在 readback 中增加可选
   `answers`。声明问题后，严格检查要求稳定 ID、有效对象、完整且唯一的当前观察。
   新轮次清空答案；老文件未声明问题时兼容。字段校验不能证明答案正确。
4. `mechanism-readback.md` 集中说明源码到图和图到源码的双向检查、抽象边界、
   面板关系、标签归属、端口/路线、素材角色、图注分工及修订复核。
   SKILL.md 只增加入口与交付命令，不重复长篇规范。
5. 增加 11 项确定性回归和 6 个匿名可渲染对照案例；另列残差、布局取舍、
   展开对象、虚构操作、素材角色、图注变化的行为任务。

## 实际验证与局限

- 11 项新增回归通过：缺审查、空出版检查、过期图注/导出、未关闭问题、
  读图问题漏答/重复/空白、修订对比、CLI 退出码、不覆盖输入、畸形输入。
- 特意构造自洽但语义错误的 claim：合同仍能通过。此测试固定了能力边界，
  不把其误称为科学检测成功。
- `make test`：poster 6、academic overlay 81、scientific visualization 7 项通过。
- `make check-base`：工程/技能结构、路由和 base 示例检查通过。
- 6 个 YAML 案例实际导出 SVG 和 drawio。5 个使用 strict warnings；
  `port-offset` 有意保留路由诊断，按普通验证导出，不能改好缺陷再充当负例。
- Chromium 逐图按 100 mm CSS 宽度查看（377.9375 CSS px），核对端口偏移/居中、
  标签游离/归属明确、查询身份缺失/明确三组差异。使用每张独立 SVG 图片，
  避免组合 SVG 的重复 marker ID 影响观察。此为已知答案的主线程自查，
  未执行独立或盲评，不报告模型准确率或漏检率降低。
- 以现有复杂模型图的真实 SVG/scene/text metrics/geometry report 做只读重放，
  临时诊断 manifest 不伪造语义审查：几何 `evidence_checked`，读图/科学/出版
  `not_checked`，总状态 `needs_review`，严格命令返回 1。未重画或验收该论文图。
- 其余六项文字行为任务未进行独立模型测试；已有确定性生命周期测试只覆盖
  相应证据规则，不替代实际读图测试。

可重放源位于 overlay `evals/mechanism-fixtures/*.yaml`，任务和答案键位于
`evals/mechanism-review-cases.json`。实际临时导出与截图保存于本仓库忽略目录
`outputs/mechanism-review-20261103/`，不进入插件包。临时诊断 manifest 仅供本机
验证，包含本机绝对路径；不是可移植论文发布文件。

## 尚未实施的能力

不增加新的自动路由器或图像语义裁判。标签归属、面板使命、参考图适配质量
仍需要实际成图判断。本轮也未改动图像绑定/复杂几何的 base 渲染能力；这些
应作为单独的上游最小复现处理，避免在 overlay 复制 renderer。

版本号未提升，未提交/推送/发布，运行缓存未同步。工程实现和缓存加载是不同状态。


## 2026-11-04 implement 收尾复核

本地代码审查发现并修复两类缺口：非空 publication.checks 中的空白/null/
无证据/未通过条目可错误计入证据；缺少完整 context 的旧 review 可被当作
可比较快照。补充三项回归，先复现失败，再修复通过。出版检查支持非空观察
字符串，或具备 name、status=pass、非空 evidence 的对象。旧快照必须具有
匹配的 figure_id、contract 及 node/edge inventory。

当前针对性测试 14 项通过；make test 共 97 项通过（6+84+7）；
make check-base 通过。已核对最终差异，未修改 base、运行缓存或 Git 提交状态。
独立读图评测与自动语义正确性判断仍未实现，不声称漏检率已降低。
