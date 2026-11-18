
## 第 5 轮 · 2026-11-18 · VocalGateway 信息来源机制复原

（全文见 `docs/vocal-gateway-source-acquisition.md`）

**三个渠道**：① 主办方官网定向批量抓取（50 条免费机会共 35 个官方 URL，slug 带 `global41-013` 批次号）；② AI 联网检索（报告样例链接多处带 `?utm_source=openai`）；③ Wayback CDX API 机器查询 + 年报 PDF/移民局文件。

**管线的可量化形状**：54 条 evidence 只对应 15 个不同 `fetchedAt`，集中在 9-28 13:31–13:35、9-29 08:00/12:00/15:00、10-06 04:22 几个批次；部分时间戳是整点回填；`reviewerId` 全是常量 `v15-local-review`，`reviewedAt` 与 `fetchedAt` 同毫秒；`locator` 是受控词表（official page / current-cycle notice / organizer-controlled domain），仅 PDF 类做到页码级；`language` 全 en。

**与自述原则的落差（重要）**：51 个 deadline 中 24 个 `evidenceState:"verified"` 而 `evidenceIds` 为空；24 条机会 `evidenceRefs` 全空却带「来源已核对」；306 项费用的 `evidenceIds` 全部退化为 React 路径字符串；摘录是转述句而非原文（49 条中 18 条以「Official page says…」开头）。

**对我们的四条结论**：excerpt 只存原文短摘并标 `paraphrase`；`fetchedAt` 与 `reviewedAt` 不得相同；`unknown` 必须是合法状态且 `validate.py` 补「evidence 必带 excerpt + fetchedAt」；批次 ID 与页面核对时间分开显示。
