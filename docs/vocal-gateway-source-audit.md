# VocalGateway 来源 / 代码 / 素材审计（REA 第 4 轮 · 延伸）

研究日期：2026-11-18　对象：`https://www.vocalgateway.com/zh`
方法：只读取公开 HTML、公开 CSS、公开静态素材的响应头与体积；不登录、不抓会员内容、不复用其代码与素材。

---

## 1. 信息来源：三层，都能追到原始页面

**第一层 · 主办方官方页面（每条机会一个 `officialUrl`）**
例：`https://www.houstongrandopera.org/butler-studio/yava`、`https://www.saluzzooperaacademy.com/apply`、`adasari.pl`、`interkultur.com`、`carnegiehall.org`、`avaopera.org`、`icav.ca`、`berlinoperaacademy.com`、`operawards.org`……公开页里出现的官方域名约 30 个，全部是主办机构自己的站点。

**第二层 · 机构文件与政府口径（用在深度报告）**
`https://www.operaballet.nl/.../Jaarverslag-2023-web.pdf`、`.../Jaarverslag-2025-online.pdf`（荷兰国家歌剧院年报）、`ind.nl`（荷兰移民局）、`www.netherlandsworldwide.nl`（荷兰外交部）。

**第三层 · 辅助与存证**
`web.archive.org`（页面快照存证）、`casting42.com`、`bedandmarket.com`、`www.turkishairlines.com`（预算与出行口径）。

**关键：每条证据不是「一个链接」，而是一条记录。**

```json
{
  "id": "v15-evidence-hgo-yava-0",
  "officialUrl": "https://www.houstongrandopera.org/butler-studio/yava",
  "cycleId": "b40a862c68e6f64ff0d921cb4cc6ce71",
  "locator": "official page · current-cycle notice",
  "excerpt": "Official page says applications open 30 December 2026 and close 21 February 2027.",
  "language": "en",
  "fetchedAt": "2026-09-28T13:35:18.134Z",
  "reviewedAt": "2026-09-28T13:35:18.134Z",
  "reviewerId": "v15-local-review",
  "version": 1
}
```

十个字段，缺一不可地构成「可复核」：**哪个页面（officialUrl）· 页面里的哪个位置（locator）· 原文怎么说（excerpt）· 什么语言（language）· 什么时候抓的（fetchedAt）· 什么时候复核的（reviewedAt）· 谁复核的（reviewerId）· 第几版（version）**。

页面上的呈现只有一句：「申请前请以主办方最新公开资料为准 · 最后核对：2026-09-20」。

## 2. 代码与数据格式

**数据模型三层分离**：`opportunity`（这是什么机会）→ `cycle`（这一届的具体条件）→ `evidenceRefs`（凭什么这么说）。
多数同类站把三者混成一张卡片，他们拆开了，所以「上一届的条件」和「这一届的条件」可以同时存在而不打架。

字段级的诚实设计（逐项核实过）：

| 设计 | 真实取值 |
|---|---|
| 截止时间 | `{localDate, localTime, ianaTimezone, utcInstant, precision:"date_only", kind:"application", evidenceState:"verified", evidenceIds:[...]}` |
| 费用 | `{kind:"application_fee"/"tuition"/"housing"/"travel"/"stipend"/"prize", minorUnits:null, currency:null, condition:"not_stated", evidenceIds:[...]}` |
| 状态 | `listingState` / `applicationState` / `evidenceState` 三个独立枚举，不混用 |
| 评分 | `difficulty:{score, band, confidence:"LOW", policyVersion:"frozen-shared-scoring.v112d0"}`；`careerTier:{tier, score, policyVersion:"opportunity-career-tier.v10.5"}` |
| 报告模式 | `reportMode:"CURRENT_CYCLE_WITH_HISTORICAL_REFERENCE"`（枚举，非文字约定） |
| 材料 | `{id, name:{zh,en}, detail:{zh:"以官方原文为准。"}}`，把「我们不知道细节」写成正式文案 |

三个特别值得记的：

1. **金额用 `minorUnits` 整数 + `condition:"not_stated"`**，不用字符串和空值。
2. **每个分数带 `policyVersion`**：口径改版后旧分数仍可解释——分数变了是口径变了，不是事实变了。
3. **每个叶子字段独立带 `evidenceState` 和 `evidenceIds`**，不是整条机会一个「已核实」戳。

**一个真实的装配缺陷**：`costs[*].evidenceIds` 在公开 payload 里退化成了 React 引用路径字符串（`"$13:props:children:1:props:records:0:cycle:deadline:evidenceIds"`），说明这一层在序列化时丢了引用展开——也就是说六项费用实际上挂不上证据。这是「字段级证据」做得太细、装配没跟上时的典型失效，值得我们注意。

**页面层**

- Next.js App Router + Turbopack，`vg-ui-exact` 作样式命名空间，RSC payload 内嵌整页数据；公开页只带 50 条机会（免费层），其余 445 条不进 payload。
- CSS：**21 个自定义属性（`--navy` `--ink` `--line` `--paper` `--wine` `--accent`…），但硬编码 hex 有 442 个**。令牌立了，实际在漂移。
- **没有 `@font-face`，全站系统字体**：正文 `Georgia, Songti SC, serif` 系，标题 `Iowan Old Style, Baskerville, Noto Serif CJK SC`。不下载字体＝零字体成本，靠衬线排版撑「编辑部」气质。
- 版式：`display:grid` 280 处、`flex` 178 处、`clamp()` 87 处、媒体查询 56 处——响应式是真做了的。
- SEO：`canonical` 全页有；**hreflang 有**（zh/en/x-default，React 渲染成 `hrefLang`）；JSON-LD 只有首页 `WebSite` 和详情页 `BreadcrumbList`，**没有 Event / JobPosting / Organization**；`og:image` 全站共用一张 1500×1500 logo。
- 报告：13 页，每页一张 WebP（98–185KB），另有 `/api/v1/public/sample-report?locale=zh&v=report-recovery-v3&download=1` 作为 PDF 下载（该接口响应极慢，40 秒超时未取到）。
- 托管：自托管 nginx，`cache-control: private, no-store`，无 CDN。

## 3. 素材来源：几乎「零素材」

全站可枚举的自产素材只有四类：

| 素材 | 规格 | 体积 |
|---|---|---|
| 品牌 logo（OG 用） | 1500×1500 PNG | 345KB |
| logo 深底版 | 384 宽 WebP（`<picture>` + `srcSet`） | 46KB |
| apple-touch-icon | 180×180 PNG | 22KB |
| 样例报告页 | 13 张 WebP，逐页 | 98–185KB / 张 |

**没有摄影、没有插画、没有人物图、没有网页字体、没有任何第三方图库素材。** 视觉全部由排版、色块、细线、数字构成。

这个选择对他们的业务是成立的（卖的是信息，不是氛围），对我们的业务不成立——我们需要结构与动态的可视化。

## 4. 可借鉴 / 不可借鉴

**借（模式，不借文件）**

1. 证据记录的十字段结构（尤其 `locator` + `excerpt` + `fetchedAt` + `reviewedAt`）——这是把「可核对」从形容词变成字段。
2. 字段级 `evidenceState` + `evidenceIds`：不是整条结论一个戳，而是每个数字各自有出处。
3. `condition:"not_stated"`、`minorUnits` 整数金额、`precision:"date_only"`：把「不确定」建成枚举，而不是留空或猜。
4. `policyVersion` 冻结评分口径：口径迭代不污染历史数据。
5. `listingState` / `applicationState` / `evidenceState` 三态分离。
6. `materials` 归一化 + 「以官方原文为准」：能给结构的地方给结构，不能给的地方明确交回原文。
7. 零 webfont 的系统衬线栈（`Georgia + Songti SC`）：移动端首屏省一次字体请求。

**不借**

1. 442 个硬编码色（令牌漂移是我们的反面教材，我们应保持 token 收敛）。
2. 全站共用一张方形 OG 图（社交卡片会被裁成竖条，等于浪费）。
3. 深度报告用逐页图片而非文本（不可检索、不可复制、不可无障碍阅读；我们要出报告就出真文本）。
4. 无 CDN + `no-store`（他们首字节慢到 20–40 秒超时，我们 Service Worker 方案已优于这一点）。
5. 字段级证据做到 `costs` 却没装配上（教训：粒度要配得上装配能力）。
6. 他们的机会数据、评分口径、报告正文、文案与素材——一律不取。

## 5. 落到我们身上的三件事（细化版）

1. **`research/evidence.json` 升级**：现在只有 `{id, kind, title, url}`；补 `locator`（章节/表名）、`excerpt`（≤25 词短摘，标语言）、`fetchedAt`、`reviewedAt`。页面证据卡能显示「这句话出自官方哪一段」。
2. **`data/voice-structures.json` 字段级状态**：给关键字段（`function`、`innervation`、`singing_role`）各自带 `evidenceState` + `last_checked`；`pending_fields` 保留为「尚未核」的清单。
3. **大师班页采用材料归一化 + 准备复杂度**：`materials[{name, detail:"以官方原文为准"}]` 结构 + 三行「准备复杂度」，不写录取概率。

参考页面（公开可访问）：首页 `/zh`、机会库 `/zh/opportunities`、详情 `/zh/opportunities/hgo-yava`、样例报告 `/zh/sample-report`、会员 `/zh/membership`。
