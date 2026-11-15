---
# 按声部细分的邮件订阅链路

状态：已上线并完成线上端到端验证（除 Buttondown 后台预览一项需人工核对）。
相关文档：`docs/newsletter-copy-guide.md`（正文怎么写）、`docs/analytics-and-newsletter-setup.md`（统计与订阅总览）、`docs/ops-dashboard-setup.md`（后台）。

## 一、链路总览

```
网站首页表单
  └─ POST https://opera-lirico-ops.wl19971007.workers.dev/api/subscribe   （公开路由，无后台密码）
       └─ POST https://api.buttondown.com/v1/subscribers                   （type=unactivated，双确认）
            └─ Buttondown 发确认邮件 → 用户点确认 → 成为 regular 订阅者
                  └─ metadata.voice 决定他在每期邮件里看到哪一段

GitHub Actions（每周一 08:00 UTC）
  └─ weekly_digest.py --mode segmented
       └─ POST /v1/emails (status=draft, email_type=private)               （只建草稿，从不发送）
            └─ 正文含 7 个声部件段 + 1 个“不限声部”段 + 2 个兜底段，均为 {% if subscriber.metadata.voice … %} 条件段
                 └─ 人工在 Buttondown 预览、检查、点发送
```

## 二、为什么用一条邮件 + 条件段，而不是八条邮件

三条路都可行，选的是第三条：

| 方案 | 前置条件 | 结论 |
| --- | --- | --- |
| 每条声部一封，用 tag 过滤受众 | tag 需要 Basic 及以上套餐；邮件 `filters` 必须用 tag 的 ID 而不是名字 | 当前账号 tag 数量为 0，若发新 tag 会返回 403 `feature_disabled`，会把订阅请求本身打挂 |
| 每条声部一封，用 metadata 过滤受众 | 需要确认 metadata 过滤的字段名与算子 | 未验证，且八封群发会放大退信与限流风险 |
| 一条邮件 + 模板条件段 | 只需 metadata 可写、模板支持 `{% if %}`（已核实官方文档） | 采用。一次发送，按订阅者渲染，不依赖付费套餐 |

代价：八个声部的内容都在同一封正文里，邮件偏长（约 8 段卡片 + 一个列表）。当前的替代收益是链路稳定、不误发多封。

## 三、订阅表单与公开端点

### 表单（`index.html` + `subscribe.js`）

- 字段：邮箱、声部（下拉，8 个选项含“不限声部”）、同意勾选、隐藏蜜罐字段。
- 声部键值与站点数据完全一致：`soprano / mezzo_soprano / contralto / countertenor / tenor / baritone / bass / all_voices`，中文标签见 `app.js` 与 `weekly_digest.py` 的 `VOICE_LABELS`。
- 提交前在浏览器侧校验邮箱格式、声部、同意勾选；失败文案全部在 `subscribe.js` 的 `MESSAGES` 里，端点只返回错误码。
- 端点地址写在 `site-config.js` 的 `subscribeEndpoint`，是可公开的地址，不含任何凭据。

### 端点（`ops-dashboard/worker.js` 的 `POST /api/subscribe`）

- 仅接受 `Content-Type: application/json`，因此跨域请求必然先发预检；`Origin` 只允许：
  `https://operalirico.github.io`、`https://www.operalirico.github.io`、本地 8080 两个调试源。
- 每 IP 十分钟最多 5 次提交（内存计数，按 Worker 实例计，重启即清零）。这是第一道闸，真正的滥用拦截由 Buttondown 的防火墙承担。
- 蜜罐字段非空时返回成功但什么都不写。
- 校验：邮箱格式、声部必须在白名单内、必须传 `consent: true`、请求体 ≤ 2000 字节。
- 写入 Buttondown 的字段：
  - `email_address`
  - `type: "unactivated"`（强制双确认，即“同意”必须由用户点邮件确认，不能由脚本代劳）
  - `metadata`: `voice`、`voice_label`、`consent: true`、`consent_at`、`source: "site:newsletter-form"`、`locale`
  - `notes`、`referrer_url`、`ip_address`
- `X-Buttondown-Collision-Behavior: add`：同一邮箱重复提交时合并，不报错。
- 已存在（400/409）与新建（201）返回同一句成功，避免用这个端点探测某邮箱是否已订阅。
- 不写 `tags`。当前账号没有 tag，写新 tag 会 403 并让订阅整体失败；声部只靠 metadata。

### 后台展示

`/api/data` 增加 `buttondown.voice_breakdown`（按 `metadata.voice` 聚合的有效订阅者数量），后台“邮件草稿”区块显示一行声部分布。站点前台不展示任何订阅人数。

## 四、邮件生成

`weekly_digest.py` 默认 `--mode segmented`：

- 复用原来的三道闸：`publisher_status=official` + `review_status=verified` + `publication_status=published`，且截止时间在未来。
- 每条声部段落 = 该声部命中的公告（`voice_types` 含该声部，或含 `all_voices`），最多 5 条；空则明确写“本周没有新增点名该声部的已核验机会”。
- 条件段一共 10 个：7 个声部 + 1 个 `all_voices` + 2 个兜底（`{% if not subscriber.metadata.voice %}` 与 `{% if subscriber.metadata.voice == "unspecified" %}`）。兜底段给“没填声部的人”看全量列表，避免旧订阅者或 metadata 没写进去的人收到一封没有个人段落的邮件。`--mode single` 保留旧的单版本简报，供对比和回退。
- 草稿 slug 为 `opera-lirico-weekly-<date>-voiced`，与旧的单版本草稿分开，避免去重把新草稿吞掉。
- 仍然只建 `status=draft`、`email_type=private`、`archival_mode=disabled` 的草稿，从不调用发送。

本地预览产物（`build/email-draft/`）：`preview.html`、`preview.txt`，以及每个声部的 `voice-*.html`，用于人工核对某段落是否正确命中。

## 五、隐私与同意

- `privacy.html`：写明数据控制者、收集字段（邮箱/声部/同意记录/技术事件）、用途（发送 + 分拣）、处理者（Buttondown、Cloudflare、GitHub Pages）、保留期、退订与删除方式、权利与投诉渠道。
- 表单必须勾选同意才能提交，且 `consent` 写入 metadata，`consent_at` 留时间戳。
- `docs/ai-assisted-development.md` 的约束（没有已批准的隐私披露与明确同意，不得收集歌手档案或关联订阅者身份）由此满足：只收声部一个字段，不建歌手档案，不与其他身份信息关联。
- 退订走 Buttondown 的页脚链接；改声部目前是“回复邮件说明”，由人工在 Buttondown 后台改 metadata。没有做自助改声部的页面（避免再加一个公开写入端点）。

## 六、运维要点

| 场景 | 动作 |
| --- | --- |
| 上线新的声部或改键值 | 同时改 `app.js` 的标签、`weekly_digest.py` 的 `VOICE_LABELS`/`VOICE_ORDER`、`worker.js` 的 `VOICE_LABELS`、`index.html` 的 `<option>`，四处必须一致 |
| 订阅端点报 502 | 查 `BUTTONDOWN_API_KEY` 是否还有效；端点不返回上游响应体，日志里只有状态码 |
| 草稿里出现裸露的 `{% if %}` | 说明模板不支持条件语法，立刻停止发送，改用 `--mode single`，并记录到本节 |
| 想改成每条声部一封 | 先 `GET /v1/tags` 确认套餐支持 tag，再按 tag ID 建 `filters`，不要用 tag 名字 |
| 误建了草稿 | 在 Buttondown 删除草稿即可，链路不会自动发送 |
| 想暂停订阅 | 把 `site-config.js` 的 `subscribeEndpoint` 置空，表单会提示“订阅服务还没配置好” |
| 想复查账号能力 | 手动触发 `Newsletter capability probe`（只读，打印 `/newsletters`、`/tags`、`/subscribers`、`/emails` 的 HTTP 状态与片段） |
| 想复查订阅者与草稿 | 手动触发 `Newsletter state check`（只读，把订阅者声部与草稿 slug、条件段数量写进 job summary） |
| 想发一封一次性公告 | 改 `content/newsletter-announcement.md` 后手动触发 `Newsletter draft from file`（只建草稿，`content_engine/buttondown_draft.py` 负责提交） |

## 七、验证记录

- 2026-11-15：`GET /v1/newsletters` 200、`GET /v1/tags` 200（`results: []`，count 0）、`GET /v1/subscribers` 200、`GET /v1/emails?status=draft` 200。结论：可读、可写订阅者，但没有 tag，条件段方案是唯一不依赖付费套餐的可行路径。
- 2026-11-15：本地 `python -m unittest tests.test_newsletter_segments tests.test_weekly_digest` 通过；`node --check subscribe.js site-config.js ops-dashboard/worker.js` 通过。
- 2026-11-15：本地 `python weekly_digest.py --now 2026-11-15T12:00:00+01:00` 生成 7 条机会、10 个条件段；男高音 3 条、男低音 3 条、女低音 1 条、不限声部 1 条按预期分配。
- 线上端到端（2026-11-15）：
  - 订阅写入：`POST /api/subscribe`（Origin `https://operalirico.github.io`，`voice=tenor`）返回 `200 {"ok":true,"result":"pending_confirmation"}`；`Newsletter state check` 运行 `43742422885` 读到该订阅者 `type=unactivated voice='tenor' consent=True source=site:newsletter-form`，说明 metadata 已落库。
  - 拒绝路径：`voice=unknown` 与缺 `consent` 都返回 400；预检 `OPTIONS` 返回 204 且带 `Access-Control-Allow-Origin: https://operalirico.github.io`。
  - 草稿生成：`Weekly email digest (draft only)` 运行 `43741859570` 成功，新建草稿 `Opera Lirico 每周简报｜2026-11-15｜按你的声部`（`slug=opera-lirico-weekly-2026-11-15-voiced`，`type=private`，当时为 8 个条件段，现已扩为 10 个）。
  - 公告草稿：`Newsletter draft from file` 运行 `43770309938` 成功，以 `content/newsletter-announcement.md` 为源建了草稿（`email_type=public`、`archival_mode=enabled`）。
  - 清理：测试地址标记 `+voicetest` 的记录已用一次性 workflow 删除，订阅者数回到 2（运行 `43742679241` 记录 `before 3, deleted 1, after 2`），该 workflow 已从仓库移除。
  - 未自动化的一步：Buttondown 的“按订阅者预览”需要登录后台才能看到渲染结果，这一步留给人工在发送前核对（清单见 `docs/newsletter-copy-guide.md` 第七节）。
