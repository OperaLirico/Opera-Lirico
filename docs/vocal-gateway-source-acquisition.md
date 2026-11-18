# VocalGateway 的信息是怎么来的（REA 第 5 轮 · 获取机制复原）

研究日期：2026-11-18　方法：从公开 payload 的字段分布反推流程，并与它自己的「原则」页对照。不做登录、不抓会员内容。

---

## 1. 结论：三个渠道 + 一条带版本的抽取管线

| 渠道 | 可观察证据 | 用于 |
|---|---|---|
| A. 主办方官网定向抓取 | 50 条免费机会共 35 个不同 `officialUrl`，均为机构自有域名；公开 slug 里出现 `global41-013`、`global41-036` 这类批次编号 | 机会库（卡片与详情） |
| B. AI 联网检索 | 报告样例的可见链接多为 `?utm_source=openai` 结尾（如 `operaballet.nl/...?utm_source=openai`、`ind.nl/...?utm_source=openai`、`netherlandsworldwide.nl/...?utm_source=openai`） | 深度研究报告 |
| C.  Wayback 机器查询 + 机构长文档 | 报告里直接给出 CDX API 调用：`web.archive.org/cdx/search/cdx?url=...&output=json&fl=timestamp,original,statuscode&filter=timestamp:202[1-5]&collapse=digest` | 历史存证、往届数据 |

第三层辅助源（仅报告）：荷兰国家歌剧院年报 PDF（2023 / 2025）、`ind.nl` 移民局、`netherlandsworldwide.nl` 外交部、`casting42.com`、`bedandmarket.com`、`turkishairlines.com`（预算测算）。

## 2. 抽取管线：可量化的形状

公开 payload 里共 54 条 evidence 记录，覆盖 51 个 cycle（50 条机会 + 1 条详情页重复）、35 个不同官方 URL。字段分布：

- `fetchedAt` 只有 **15 个不同值**，集中在几个批次：`2026-09-28T13:31 / 13:34 / 13:35`（同一分钟 6 条）、`2026-09-29T08:00`（14 条）、`12:00`（6 条）、`15:00`（6 条）、`2026-10-06T04:22`（4 条）。→ **定时批量抓取，不是持续监控**。
- 其中部分时间戳是完全规整的整点或 `12:00:00.000Z`，而真实抓取时间是 `13:31:40.974Z` 这种毫秒级。→ **一部分时间戳是回填，不是真实抓取时刻**。
- `reviewerId` 54 条全部是同一个常量 `v15-local-review`；`reviewedAt` 在多条记录里与 `fetchedAt` **同毫秒**。→ **复核是管线里的一个 stage 名，不是独立人工环节**。
- `locator` 是受控词表：`official page`(27)、`official page · current-cycle notice`(4)、`official organizer domain`(4)、`official page · application deadline`(4)、`organizer-controlled domain`(2)、`recurring program / next intake`(2)、`verified official page`(2)、`V3 reviewed evidence`(2)。少量做到了真页码级：`2027 Participant Information pp. 6, 10, 13`。→ **网页类靠标签，PDF 类靠半人工阅读**。
- `language` 54 条全为 `en`。→ **以英文抽取，中文是下游翻译**。
- 命名可读出代数：`v15-evidence-*`（证据第 15 代）、`frozen-shared-scoring.v112d0`（评分口径 v112d0）、`opportunity-career-tier.v10.5`。

## 3. 与它自己「原则」的落差（对我们最有用）

它在 `/zh/about` 写明：官方来源优先、无法核实应明确标为未知、历史参考不得冒充当届。实测差距：

| 自述 | 实测 |
|---|---|
| 官方来源优先 | 是的，35 个 URL 全是主办方域名；但摘录是**转述句**不是原文：49 条里 18 条以「Official page says / Organizer-controlled page confirms」开头，其余也是概述句，**无法逐字回核** |
| 无法核实应标未知 | **51 个 deadline 里有 24 个 `evidenceState:"verified"` 但 `evidenceIds` 为空**；且有 **24 条机会的 `evidenceRefs` 完全为空**却带着「来源已核对」戳上架 |
| 每个数字有出处 | **306 项费用的 `evidenceIds` 全部退化为 React 路径字符串**（如 `"$13:…:cycle:deadline:evidenceIds"`），等于费用无一可追随 |
| 复核 | 单一 reviewerId + 同毫秒时间戳，**无第二人签核痕迹** |

这四行不是抓错处，而是告诉我们：**字段级证据一旦比装配能力强半步，就会大面积退化成装饰**。

## 4. 对我们（OperaLab）的结论

1. 我们的证据必须是**可逐字回核的原文短摘**，不是概述句。`research/evidence.json` 新增 `locator` + `excerpt` 时，`excerpt` 只存原文片段（≤25 词），并加一个 `paraphrase: false` 标记；需要概述就另开 `summary` 字段。
2. `fetchedAt` 必须是真实抓取时刻（毫秒），`reviewedAt` 必须是**人实际看过的时间**，两者相同即视为未复核。复核人写具体标识，不用管线名。
3. `reviewStatus` 三态里 `unknown` 必须是合法输出：没有证据就不能是 `verified`。我们的 `validate.py` 已有「verified 必带 evidence」，需再补一条「evidence 必须带 excerpt + fetchedAt」。
4. 批量抓取可以，但要保留**批次 ID**（我们已有 REA 轮次编号），并在页面上把「本轮核对时间」与「原始抓取时间」分开显示。

---

来源页面（公开）：`/zh/about`、`/zh/sample-report`、`/zh/opportunities`、`/zh/opportunities/hgo-yava`；报告内可见 `utm_source=openai` 链接与 Wayback CDX API 调用。
