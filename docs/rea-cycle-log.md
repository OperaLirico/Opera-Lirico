# REA 循环日志

记录每一轮做了什么、依据是谁、门槛结果如何。台账优先于叙述：改了什么以 commit 为准，结论以数据门为准。

## 第 1 轮 · 2026-11-17 · 字段待核 12 → 0

**入口问题**：`data/voice-structures.json` 有 12 条结构挂着 `pending_fields`，页面在这些字段上显示「待核（暂不展示）」。这是结构层唯一未闭合处。

**发现 → 验证 → 开发 → 测试**

| 结构 | 待核字段 | 核定结论 | 依据 |
|---|---|---|---|
| 腭帆提肌 | innervation | 迷走神经（CN X）经咽丛的咽支 | E14 |
| 腭帆张肌 | innervation | 三叉神经下颌支（V3）内侧翼突神经；软腭五肌中唯一不走迷走者 | E14 |
| 腭咽肌 | innervation | 迷走神经（CN X）经咽丛 | E14 |
| 腭舌肌 | innervation | 迷走神经（CN X）经咽丛；舌肌中唯一不由舌下神经支配者 | E14 / E15 |
| 颏舌肌 / 舌骨舌肌 / 茎突舌肌 | innervation | 舌下神经（CN XII） | E15 |
| 膈 | innervation | 膈神经（C3–C5） | E16 |
| 肋间外肌 | innervation | 肋间神经（T1–T11 前支） | E16 |
| 腹肌群 | innervation | 胸腰段脊神经前支（T7–L2；部分文献记 T6–L1，属节段计数差异） | E17 |
| 肺 | innervation | 无自身运动肌；肺丛（X＋交感）管气道，胸膜/心包由膈神经供应 | E18 |
| 真声带 | layers | Hirano cover-body：被覆 / 移行（声韧带）/ 体（甲杓肌） | E19 |

**门槛结果**：`entries=47 verified=47 pending=0`，证据 17 条，`errors=0`（CI 跑 `python3 research/validate.py`）。

**本轮刻意没做**：声门下压与音强的定量区间、腭帆肌群歌唱时的 EMG 证据。两者属于 P2 动态层的口径，不属于结构层字段，不硬塞进来。

## 外部站点观察 · Singing Carrots `/about` · 2026-11-17

1. **免费工具做入口，付费教练做留存**：音域测试、音准测试、选歌都属于「关于你自己的数据」，不是知识文章。
2. **工具互相喂数据**：免费工具测出的音域与音准进入教练，形成闭环。
3. **把边界写在明面上**（a tool in the toolbox, complements a human teacher）——和本站「AI 生成 · 非真实病例」是同一类做法。

对我们的启示：结构层现在是纯阅读，缺一个「你记住了吗」的出口。P4 的三题自测应该挂在每条结构卡下方，而不是单独做一页。

## 外部站点观察 · Visible Body（官方帮助中心）· 2026-11-17

来源：https://support.visiblebody.com/hc/en-us/articles/360045539374-Getting-Started

1. **选中即出信息面板**：点结构→Info box，定义、发音、起止点、相关病理分图标分栏，而不是一整段堆在一起。
2. **Hide / Isolate / Dissect 三件套**：把一个结构从周围「剥」出来，是回答「它到底在哪」的最短路径。
3. **双击设旋转中心**：把焦点钉死在目标结构上，而不是自由旋转。
4. **解剖测验（dissection quiz）**：给名字，让你在模型上点出结构；必要时先旋转、先隐藏遮挡。
5. **Review checklist**：学员自己勾「我掌握了」，用它做学习进度。
6. **三维切片配 CT/MRI/尸检片对照**：和本站「喉镜帧对示意图」是同一逻辑。

本轮落地的那一条：结构层加了一个「发声通路小测」——随机报一个结构名，用户在 SVG 上点热区作答，答错直接标出正确块。对应上面第 4 条，也补上了之前指出的「纯阅读缺出口」。

待办（按性价比排序）：面包屑（通路 › 分组 › 名称）；自评勾选写 localStorage；每张卡片加「只看它」；三维的 isolate 留到 P3。

## 第 2 轮 · 2026-11-17 · 结构层整页重写（只改交互层，不动一个字段）

**入口问题**：结构层能读、能搜、能测，但缺三样：这块在通路的哪一层；怎么把一块从其余结构里剥出来看；学习者自己的进度。上一轮读 Visible Body 时记下的 Info box / Isolate / review checklist，正好对应这三点。

| 改动 | 对应外部做法 | 实现 |
|---|---|---|
| 面包屑：发声通路 › 分组 › 名称，点层级可回跳分组 | Anatomical hierarchy / breadcrumb trail | 卡片顶部三段可点路径 |
| 「只看选中」：开启后其余 12 块降到 30% 不透明度 | Isolate | 图下按钮 + 卡片「在图上定位」 |
| 掌握勾选：localStorage 记录、进度芯片、只看未掌握 | Review checklist | 键 `operalab-mastered`，不上传不统计 |
| 深链 `?id=…`：每个结构有可分享地址 | — | `history.replaceState` |
| 上一个 / 下一个：按当前筛选顺序走 | — | 卡片内导航按钮 |
| 图上无块的结构明确说明，而不是假装有 | — | 「该结构在图上没有独立块，可从相邻结构的位置推断」 |

**修掉一个真 bug**：选中「声门」这类图上没块的结构、又开着「只看选中」时，整张图会被调暗 13/13。现在只在目标结构确实有块时才调暗。

**验证**（本机浏览器控制通道不可用，改用可重现的脚本验证）：
- `node --check` 语法通过；
- 最小 DOM 桩 + 真实 47 条结构与 17 条证据，跑 18 项检查全带走：列表 47 条、分组计数（通路 7 / 软骨 5 / 喉黏膜 5 / 喉内肌 8 / 喉外肌 7 / 软腭 4 / 舌 2 / 舌肌 3 / 呼吸 4）、分层行、面包屑、掌握写 localStorage 并在列表与卡片同步、未掌握筛选 46/47、小测答错标绿红、答对计分 1/1、无块结构提示。

**没动的**：`data/voice-structures.json`、`research/**`、`research/validate.py`。这一轮只改展示层，数据门仍然一票否决；页面对 `pending_fields` 的处理方式（显示「暂不展示」而不是用推测填满）不变。

**下一轮候选**：把「掌握」接进小测（答对自动标记）；按「未掌握」出题而不是纯随机；三维 isolate 留到 P3。

## 第 3 轮 · 2026-11-18 · 外部观察：VocalGateway

对象 `https://www.vocalgateway.com/zh`。全文见 `docs/vocal-gateway-teardown.md`。

**观察到的事实**：免费 50 条精选 + 会员 495 条（¥99/年·365 天·不自动续费）；深度报告样例 21 章、13 页、证据编号 `[S1]`–`[S19]`、每判断带置信度、预算三档、显式「不预测录取」；sitemap 43 条（16 功能页 ×2 语言 + 27 详情），无任何文章/术语/教学页；技术为 Next.js 自托管 nginx，`cache-control: no-store`，无 CDN。

**可借鉴**：未知做成正式取值（未说明/具体时刻待确认/变更待复核）；证据编号 + 置信度；排除性声明前置；免费层给够用、付费层给完整。

**不可借鉴**：他们的机会整理与难度评分口径、报告正文、素材与品牌。要做机会数据只能从主办方官方来源自建。

**对我们排的三个动作**：① `review_status` 三级化（verified/pending/unknown + `last_checked`）；② 大师班页加「准备复杂度」而非「录取难度」；③ 每场大师班配一页 8 章深入，等积累到 4–6 场再上。

**结论**：他们卖机会广度，我们卖机制深度 + 意大利落地，不是同维度竞争；真正的交集是把「准备」做成我们自己的可核对产品。

## 第 4 轮 · 2026-11-18 · VocalGateway 来源 / 代码 / 素材审计

（延伸第 3 轮，全文见 `docs/vocal-gateway-source-audit.md`）

**信息来源三层**：主办方官方页面（每条机会一个 `officialUrl`，公开页出现约 30 个主办域名）→ 机构文件与政府口径（operaballet.nl 年报 PDF、ind.nl 移民局、netherlandsworldwide.nl）→ 辅助与存证（web.archive.org、casting42、bedandmarket、turkishairlines）。

**最值得学的一条**：证据不是链接而是记录——`id / officialUrl / cycleId / locator / excerpt / language / fetchedAt / reviewedAt / reviewerId / version` 十字段。

**代码格式**：opportunity→cycle→evidenceRefs 三层分离；字段级 `evidenceState` + `evidenceIds`；费用 `minorUnits` 整数 + `condition:"not_stated"`；截止 `localDate+localTime+ianaTimezone+utcInstant+precision:"date_only"`；评分带 `policyVersion`（`frozen-shared-scoring.v112d0` / `opportunity-career-tier.v10.5`）；`listingState`/`applicationState`/`evidenceState` 三态分离。CSS 只有 21 个令牌却有 442 个硬编码色（漂移）；无 `@font-face`，全站系统衬线栈；JSON-LD 仅 WebSite + BreadcrumbList，无 Event/JobPosting；hreflang 存在但渲染为 `hrefLang`。

**素材**：几乎零素材——1500×1500 logo PNG（345KB，全站共用作 OG）、384 宽 WebP 深底 logo（46KB）、180 apple-touch（22KB）、13 张报告页 WebP（98–185KB/张）。无摄影、无插画、无人物图、无 webfont。

**可借**：十字段证据、字段级状态、`not_stated` 枚举、口径版本化、三态分离、材料归一化、零字体请求的系统衬线栈。
**不借**：442 色漂移、方形共享 OG 图、图片式报告、无 CDN 且 `no-store`、粒度过细而装配失灵的 `costs.evidenceIds`（公开 payload 里退化为 React 路径字符串）。

**落地三件事**：① `research/evidence.json` 从 4 字段扩到带 `locator/excerpt/fetchedAt/reviewedAt`；② `voice-structures.json` 关键字段各自带 `evidenceState + last_checked`；③ 大师班页用 `materials` 归一化 + 准备复杂度。

## 第 5 轮 · 2026-11-18 · VocalGateway 信息来源机制复原

（全文见 `docs/vocal-gateway-source-acquisition.md`）

**三个渠道**：① 主办方官网定向批量抓取（50 条免费机会共 35 个官方 URL，slug 带 `global41-013` 批次号）；② AI 联网检索（报告样例链接多处带 `?utm_source=openai`）；③ Wayback CDX API 机器查询 + 年报 PDF/移民局文件。

**管线的可量化形状**：54 条 evidence 只对应 15 个不同 `fetchedAt`，集中在 9-28 13:31–13:35、9-29 08:00/12:00/15:00、10-06 04:22 几个批次；部分时间戳是整点回填；`reviewerId` 全是常量 `v15-local-review`，`reviewedAt` 与 `fetchedAt` 同毫秒；`locator` 是受控词表（official page / current-cycle notice / organizer-controlled domain），仅 PDF 类做到页码级；`language` 全 en。

**与自述原则的落差（重要）**：51 个 deadline 中 24 个 `evidenceState:"verified"` 而 `evidenceIds` 为空；24 条机会 `evidenceRefs` 全空却带「来源已核对」；306 项费用的 `evidenceIds` 全部退化为 React 路径字符串；摘录是转述句而非原文（49 条中 18 条以「Official page says…」开头）。

**对我们的四条结论**：excerpt 只存原文短摘并标 `paraphrase`；`fetchedAt` 与 `reviewedAt` 不得相同；`unknown` 必须是合法状态且 `validate.py` 补「evidence 必带 excerpt + fetchedAt」；批次 ID 与页面核对时间分开显示。

## 第 6 轮 · 2026-11-18 · VocalGateway 会员与订阅板块拆解

（全文见 `docs/vocal-gateway-membership-teardown.md`）

**产品架构**：免费 50 条精选 + 免费主页（1 模板）；年度会员 ¥99/365 天/不自动续费，100+ 机会完整查看、每自然月 3 份深度报告、3 模板。页面明写「在线支付只用于 ¥99 年度会员」，视频点评/一对一/协助申请全部线下另行支付——支付面只留一个 SKU。

**额度五条规则（最值得学的结构）**：按上海时区自然月重置不累计；只算成功完成的新报告；失败/未完成/重开历史/下载 PDF 不扣；研究快照更新不改写历史报告；额度与产物分离。

**降级**：到期保留账户、历史报告、历史 PDF、免费主页；只停新增。

**会员墙**：列表页 126 个锁图标；「基础信息可见，完整详情、官方申请入口与资格核对需要会员」——他们连官方入口也锁。我们不借这一条。

**条款三段**：未知字段可「标为官方未公布/待确认或隐藏该字段」，并写「未知信息不等于零费用、无要求或自动符合」；AI 报告的研究性估计免责写在条款里；反抓取靠条款而非技术（robots Allow 全站）。

**对我们**：免费层＝现有全部公开层；会员＝每月 2 份「大师班准备包」（8 章）+ 历史包永久可读；额度规则同构但多一条「修正以版本形式进行」；不锁官方链接；不跟 ¥99 定价，先做 10 份试用包测工时再定价。

## 第 7 轮 · 2026-11-18 · VocalGateway 会员付费链路

（全文见 `docs/vocal-gateway-payment-flow.md`；未发起任何下单或支付请求）

**链路**：会员页 → 未登录跳 `/zh/register?returnTo=/zh/membership/checkout` → 结算页（未登录 GET 直接返回登录表单）→ 微信支付 `POST /api/v1/membership/orders {mode:"native"}` 出二维码，微信内走 `jsapi` + `WeixinJSBridgeReady`；海外走 `GET/POST /api/v1/payments/stripe/checkout` 探活，未开放时明示「No payment will be taken」；另有 `mock-notify` 演示通道 → 前端轮询 `GET /api/v1/membership/orders/{id}` 直到 `membership.status = "annual_active"` → `/zh/membership/success`。已激活用户下单返回 `MEMBERSHIP_ALREADY_ACTIVE`。价格只有 `¥99 CNY`。

**生产代码里的一條注释**：Stripe 分支 fineprint 写明「这是设计预览不是结算」「未定义美元价与海外支付权益」「线上免费精选条数文案前后不一致，模板故意不硬编码」——解释了定价页 100+ 与我们此前记录的 495 之间的差距。

**长处**：先账户后订单；只承认一个价一个币种；重复购买有错误码；未登录可见价与权益，仅结算要登录；保留演示通道。
**短处**：支付确认靠轮询而非回调；无自动续费且无续费提醒；海外权益空白；mock 接口留在生产。

**对我们**：先账户后订单；单币种 EUR；回调 + 查询双保险；Stripe 主通道不要微信支付；保留演示模式；补上他们缺的续费提醒（到期前 14/3 天邮件）。
