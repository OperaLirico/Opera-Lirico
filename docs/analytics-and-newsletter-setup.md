# Website analytics and newsletter setup

## Newsletter

订阅入口是站点自己的表单（`index.html` 的 `#newsletterForm` + `subscribe.js`），不再外链 Buttondown 的托管订阅页：

- 表单字段：邮箱、声部、同意勾选；提交到 `site-config.js` 里的 `subscribeEndpoint`（运营 Worker 的公开路由 `POST /api/subscribe`）。
- Worker 把邮箱、声部、同意记录写入 Buttondown 订阅者（`type: unactivated`，双确认后才算订阅成功）。
- 邮件由 Buttondown 发送；退订用每封邮件页脚的链接。
- 隐私说明在 `privacy.html`，表单必须勾选后才允许提交。
- 按声部细分的实现与运维见 `docs/newsletter-segmentation.md`；正文写法见 `docs/newsletter-copy-guide.md`。

后台（`ops-dashboard`）只读订阅汇总与草稿，不提供发送操作。站点前台不展示订阅人数。

## Cloudflare Web Analytics

Analytics are deliberately disabled until the site owner configures a token.

1. Add the website to Cloudflare if it is not already there.
2. Open Web Analytics and add the exact public website hostname.
3. Copy the site's Web Analytics token (not an API token).
4. Edit `site-config.js` and set `cloudflareWebAnalyticsToken` to that value.
5. Leave it empty to disable analytics.

The loader only inserts Cloudflare's beacon script when a non-empty, valid-looking site token is configured. Do not put Cloudflare API tokens, account credentials, or other secrets in `site-config.js`; this file is public.

## Verification

- With an empty analytics token, no Cloudflare beacon request should be made.
- With a configured site token, inspect the browser Network panel for `beacon.min.js` and successful analytics collection.
- Submit the site form once with a test address, confirm the confirmation email arrives and the subscriber appears as `unactivated` in Buttondown with `metadata.voice` set.
- Empty `subscribeEndpoint` in a local copy: the form must show "订阅服务还没配置好" and make no network request.
