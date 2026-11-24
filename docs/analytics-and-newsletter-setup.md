# Website analytics and newsletter setup

## Newsletter

订阅入口是站点自己的表单（`index.html` 的 `#newsletterForm` + `subscribe.js`），不再外链 Buttondown 的托管订阅页：

- 表单字段：邮箱、声部、同意勾选；提交到 `site-config.js` 里的 `subscribeEndpoint`（运营 Worker 的公开路由 `POST /api/subscribe`）。
- Worker 把邮箱、声部、同意记录写入 Buttondown 订阅者（`type: unactivated`，双确认后才算订阅成功）。
- 邮件由 Buttondown 发送；退订用每封邮件页脚的链接。
- 隐私说明在 `privacy.html`，表单必须勾选后才允许提交。
- 按声部细分的实现与运维见 `docs/newsletter-segmentation.md`；正文写法见 `docs/newsletter-copy-guide.md`。

后台（`ops-dashboard`）提供登录保护、订阅汇总、邮件草稿预览与审核发送入口。发送入口默认关闭，必须由 Worker 环境变量 `NEWSLETTER_SEND_ENABLED=true` 显式启用；站点前台不展示订阅人数。

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


## Visual media for events and institutions

Masterclass records may include `poster_image_url`, `image_alt_zh`, `image_source_url`, and `image_rights_status`. Opportunity records may additionally include `institution_image_url` for an official theatre, conservatory, or organizer image. These fields are optional: existing records remain valid and render without an image.

- Prefer images supplied by the organizer or theatre, or images with documented permission/public-domain status.
- Record the source page and a concise Chinese alt text.
- Do not download, mirror, or republish an image when rights are unknown; leave the image URL empty and link to the official page instead.
- Use lazy loading and responsive containment so portrait posters remain legible on mobile and do not distort card layouts.

## Current operational status (2026-11-24)

The repository already contains a working subscription architecture: the site form posts to the operations Worker, which creates an unactivated Buttondown subscriber; Buttondown sends the confirmation email. A verification record dated 2026-11-15 documents a successful end-to-end subscription write and a successful weekly segmented draft. The scheduled weekly workflow creates a private draft only; it does not send. The product decision is a staged workflow: initially, a human reviews the prepared campaign in the private operations dashboard and explicitly clicks **审核并发送**; later, weekly automated checks run in shadow mode before any unattended sending is enabled.

## Newsletter operating model: human approval first, guarded automation later

### Phase 1 — review in the operations dashboard (initial launch)

The weekly job prepares a campaign; it must not send it. The private dashboard should show:

- Campaign period, subject, preheader, segmented audience counts, and the exact content preview for each voice segment.
- Included items with source URL, publication/event date, last-checked timestamp, and an explanation of why each item is included.
- Validation results for broken links, missing dates, duplicate stories, stale/expired opportunities, missing source attribution, empty segments, and unsubscribe/footer presence.
- A clear status lifecycle: `draft` → `ready_for_review` → `approved` → `sending` → `sent`, with `blocked` and `failed` terminal/recoverable states as appropriate.
- Actions: preview, edit content in Buttondown, approve and send, or leave pending. The send action requires an authenticated same-origin POST, an explicit confirmation click, and a visible active-subscriber count before confirmation. The first implementation exposes the send button only for the expected weekly voice-segment draft slug.

The send endpoint is server-side only. Never expose the Buttondown API key in browser code, static assets, logs, or downloadable preview artifacts. The initial Worker implementation checks the signed dashboard session, same-origin request, explicit confirmation, exact weekly draft slug, Buttondown draft status, disabled archive mode, and a KV send-attempt lock. It sends by changing the existing draft status to `about_to_send`; the UI reports that the request was queued, not that delivery is complete. KV locking is a duplicate-attempt guard, not a mathematically strong exactly-once guarantee under concurrent cross-region requests; the dashboard must retain the Buttondown status as the final source of truth. An ambiguous provider timeout is locked for manual reconciliation rather than retried automatically.

### Phase 2 — automated checks, with human approval retained

Once Phase 1 is stable, run the same checks automatically every week and prepare a review-ready campaign. The system may recommend “all checks passed”, but sending remains behind the human **Approve & send** action. This is the rollout period for measuring false positives/negatives and editorial quality.

### Phase 3 — opt-in automatic sending

Only after a sustained successful review period, add an explicit owner-controlled setting for automatic sending. Default it to OFF. Automatic sending is allowed only when all mandatory checks pass and the campaign is within the configured schedule, audience, and content limits. Any failed, uncertain, or unavailable check must fail closed: hold the campaign in `blocked`/ `ready_for_review`, notify the owner, and do not send.

Provide a global pause switch, a per-campaign manual hold, a maximum-recipient guard, a test-send/preview path, and a visible send log. Changing auto-send from OFF to ON must require an authenticated owner action and a clear confirmation; the system must never enable it as a side effect of deployment.

### Release gates

1. Verify the existing subscription confirmation and segmentation flow.
2. Deploy and verify the authenticated dashboard preview and gated manual-send action; confirm the Worker has its `CONTENT_DRAFTS` KV binding and `NEWSLETTER_SEND_ENABLED` variable.
3. Test with a dedicated internal/test audience and verify suppression/unsubscribe behavior.
4. Confirm provider responses, audit logs, retry behavior, and duplicate-send protection.
5. Launch Phase 1 with automatic sending disabled.
6. Run automated checks in shadow mode for several campaigns, then explicitly enable Phase 2 automatic sending only after the owner accepts the observed results; do not enable unattended sending merely because CI passes.



## Implementation status (2026-11-24)

The operations Worker branch now includes:
- A sandboxed in-dashboard email body preview loaded server-side from Buttondown.
- An **审核并发送** action with a confirmation prompt and current active-subscriber count.
- Server-side session and same-origin checks; only the exact weekly `-voiced` draft slug, still in `draft` state with archive disabled, is eligible.
- A send-attempt KV lock; ambiguous provider results are held for manual reconciliation.
- Sending is disabled unless `NEWSLETTER_SEND_ENABLED=true` is explicitly configured in the Worker environment, and the existing `CONTENT_DRAFTS` KV binding is available.

This is implementation on the PR branch only. It has not been deployed or exercised against the live Buttondown account. Keep the feature flag OFF until the Worker binding and manual test procedure are verified. The scheduled digest workflow remains draft-only.
