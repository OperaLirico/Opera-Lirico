# VocalGateway 会员付费链路拆解（REA 第 7 轮）

研究日期：2026-11-18　方法：只读公开页面、公开脚本中的接口调用字符串、公开条款；**未发起任何下单、支付或写请求**。

---

## 1. 链路全貌（从点击到开通）

```
会员页 ¥99 CTA
   │  未登录
   ▼
/zh/register?returnTo=/zh/membership/checkout      ← 注册后才进结算
   │
   ▼
/zh/membership/checkout      （未登录 GET 直接返回登录表单，实测 200）
   │
   ├─ 国内：微信支付  POST /api/v1/membership/orders {mode:"native"} → 二维码
   │        微信内：provider=wechat_pay, payment.kind=jsapi（WeixinJSBridgeReady）
   │
   ├─ 海外：GET  /api/v1/payments/stripe/checkout 探活 → POST 建会话 → 跳 Stripe
   │        不可用时页面直说「International checkout is not open yet. No payment will be taken.」
   │
   └─ 演示：POST /api/v1/membership/orders/{id}/mock-notify（带 mockToken，UI 标「不会真实扣款」）
   │
   ▼
前端轮询 GET /api/v1/membership/orders/{id}（setInterval）直到 status 变化
   │
   ▼
/zh/membership/success?returnTo=… → membership.status = "annual_active"
```

## 2. 关键实现细节（都能从公开脚本里读到）

- **订单创建**：`POST /api/v1/membership/orders`，body `{mode:"native", returnTo, feature}`。返回对象含 `id`、`provider`（`wechat_pay` / 其他）、`payment{kind:"jsapi"|"native", jsapi…}`、二维码地址。
- **确认方式是轮询，不是推送**：`native` 模式下每轮 `GET /api/v1/membership/orders/{id}`（`cache:"no-store"`），看到 `membership` 字段变化才跳成功页。`jsapi` 模式在微信内监听 `WeixinJSBridgeReady` 并配合轮询。
- **重复购买拦截**：Stripe 分支对已激活用户返回错误码 `MEMBERSHIP_ALREADY_ACTIVE`，页面直接提示，不进入支付。
- **状态枚举**：`membership.status === "annual_active"`。
- **价格只有 CNY**：二维码页文案「待支付 · ¥99 CNY」；Stripe 分支在可用性未确认前**不展示任何美元价**。
- **埋点**：`/api/v1/analytics/events`（客户端事件上报，用于转化漏斗）。
- **账号墙在付款之前**：注册链接带 `returnTo=/zh/membership/checkout`，即「先有账户，再有订单」。这样会员权益、历史报告、降级保留都挂在账户上，而不是匿名订单上。

## 3. 一条留在生产代码里的开发者注释（重要）

Stripe 分支的 fineprint 原文：

> IMPORTANT: This is a design preview, not a checkout. CNY ¥99 is the publicly listed China membership price. **No invented USD price or overseas payment entitlement is implied.** The live site currently shows **inconsistent free featured-count copy**; the template intentionally avoids hard-coding it until source-of-truth…

三件事由此确认：

1. 这套结算界面某种程度上是**设计预览**，海外价与海外权益**尚未定义**，Stripe 只是探活占位。
2. 他们自己承认线上「免费精选条数」文案前后不一致（50 与 100+ 并存），模板刻意不硬编码。
3. 我在第 3 轮记的「495 条」与定价页「100+」的差距，属于他们自己已知的文案问题，不是我抓错。

## 4. 条款与产品规则怎么咬合

| 环节 | 规则 | 出处 |
|---|---|---|
| 有效期起算 | 支付确认之日起 **365 天**，不自动续费 | 会员页 + 条款第 5 条 |
| 额度 | 每自然月 3 份，按上海时区自然月重置，不累计 | 条款第 5 条 |
| 计入 | 只有成功完成的新报告计数；失败/未完成/重看/下载不扣 | 条款第 5 条 |
| 历史 | 快照更新不改写已生成报告 | 条款第 4 条 |
| 到期 | 保留账户、历史报告、PDF、免费主页；失去会员权益 | 条款第 5 条 |
| 退款 | 仅限重复扣费、状态异常、故障导致未开通或法律要求 | 条款第 6 条 |
| 支付范围 | 在线支付只用于 ¥99 年度会员；点评/课程/协助申请走线下 | 会员页 + 条款第 6 条 |

## 5. 这套链路的长处与短处

**长处**

1. 先账户后订单：权益、额度、历史、降级都挂在账户上，任何一环都不会丢。
2. 双通道但**只承认一个价**：海外通道未开时明确说「不收款」，不硬凑美元价。
3. 重复购买有明确错误码与提示，不产生重复扣费争议。
4. 未登录也能看到价格与权益，结算才要求登录——转化阻力在前端被最小化。
5. 演示通道（mock）让产品能在无支付资质时完整走通流程。

**短处**

1. **轮询确认**：用户关掉二维码页再回来，状态可能靠重新查询兜底；没有公开证据显示有支付回调通知用户。
2. **无自动续费**：好消息是退款面小，坏消息是**续费要靠用户自己想起来**，没看到续费提醒机制。
3. **海外权益空白**：Stripe 代码在，定价与权益没定义，等于半成品。
4. mock 接口留在生产：靠 token 保护，一旦配置疏漏就是风险点（属提示，非结论）。

## 6. 对 OperaLab 的结论

1. **先账户后订单**，这一条直接照做。
2. 只承认一个价、一个币种（我们以 EUR 为主），未开通的通道明确写「暂不收款」。
3. 重复购买要能拦截并给出人话提示。
4. 支付确认用**回调 + 页面查询双保险**，而不是纯轮询。
5. 我们不需要微信支付（用户在欧洲），Stripe 是主通道；但**演示模式**要保留，便于在无真实收款时演示完整包生成流程。
6. 续费提醒要自己设计（他们缺这一环）：到期前 14 天、3 天各一封邮件。

---

公开依据：`/zh/membership`、`/zh/membership/checkout`、`/zh/terms`、`/zh/register?returnTo=…`，以及页面脚本中的 `/api/v1/membership/orders`、`/api/v1/payments/stripe/checkout`、`/api/v1/analytics/events` 调用字符串。
