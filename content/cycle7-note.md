
## 第 7 轮 · 2026-11-18 · VocalGateway 会员付费链路

（全文见 `docs/vocal-gateway-payment-flow.md`；未发起任何下单或支付请求）

**链路**：会员页 → 未登录跳 `/zh/register?returnTo=/zh/membership/checkout` → 结算页（未登录 GET 直接返回登录表单）→ 微信支付 `POST /api/v1/membership/orders {mode:"native"}` 出二维码，微信内走 `jsapi` + `WeixinJSBridgeReady`；海外走 `GET/POST /api/v1/payments/stripe/checkout` 探活，未开放时明示「No payment will be taken」；另有 `mock-notify` 演示通道 → 前端轮询 `GET /api/v1/membership/orders/{id}` 直到 `membership.status = "annual_active"` → `/zh/membership/success`。已激活用户下单返回 `MEMBERSHIP_ALREADY_ACTIVE`。价格只有 `¥99 CNY`。

**生产代码里的一條注释**：Stripe 分支 fineprint 写明「这是设计预览不是结算」「未定义美元价与海外支付权益」「线上免费精选条数文案前后不一致，模板故意不硬编码」——解释了定价页 100+ 与我们此前记录的 495 之间的差距。

**长处**：先账户后订单；只承认一个价一个币种；重复购买有错误码；未登录可见价与权益，仅结算要登录；保留演示通道。
**短处**：支付确认靠轮询而非回调；无自动续费且无续费提醒；海外权益空白；mock 接口留在生产。

**对我们**：先账户后订单；单币种 EUR；回调 + 查询双保险；Stripe 主通道不要微信支付；保留演示模式；补上他们缺的续费提醒（到期前 14/3 天邮件）。
