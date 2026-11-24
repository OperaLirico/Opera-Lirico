# Opera Lirico 私有运营后台

后台运行在独立的 Cloudflare Worker，不部署到公开 GitHub Pages。页面需要密码登录；浏览器只接收统计汇总和邮件草稿标题，不接收订阅者邮箱或 API 密钥。

## 连接后可查看

- Cloudflare Web Analytics：过去 30 天页面浏览量、访问次数和每日趋势。
- Buttondown：当前有效订阅人数、过去 7 天新增人数、待审核草稿数量、标题和创建日期。
- GitHub Actions：最近 20 次自动化工作流运行状态、失败结论、分支和运行链接；只读取公开仓库的 Actions 元数据，不需要新增 GitHub Token。
- 后台可预览每周邮件草稿；在功能开关开启后，可对符合规则的每周按声部简报执行人工审核发送。不会提供订阅者邮箱导出或删除操作。每周定时任务仍然只创建草稿。
- 工作流状态来自公开 GitHub Actions API；后台仅显示运行元数据和运行链接，不读取构建日志、仓库密钥或私有内容。

## 首次部署前需要配置的 GitHub Actions Secrets

在仓库 Settings → Secrets and variables → Actions → New repository secret 中添加：

| Secret 名称 | 用途 |
| --- | --- |
| `CF_ACCOUNT_ID` | Cloudflare Account ID |
| `CF_WORKERS_DEPLOY_TOKEN` | 部署 Worker 的 API Token |
| `CF_ANALYTICS_API_TOKEN` | 读取 Cloudflare Analytics 的 API Token |
| `BUTTONDOWN_API_KEY` | Buttondown API Key（如果每周简报已在使用同名 Secret，可复用） |
| `OPS_DASHBOARD_PASSWORD` | 后台登录密码，建议使用密码管理器生成至少 32 个随机字符 |

### Cloudflare Token 权限

请创建两个独立的 Custom API Token，均只授权当前 Cloudflare Account：

1. `CF_WORKERS_DEPLOY_TOKEN`：为已创建的 `opera-lirico-ops` Worker 授予 Workers Editor（旧权限界面可能显示为 Workers Scripts Edit）。只用于部署和更新该 Worker。
2. `CF_ANALYTICS_API_TOKEN`：Account → Account Analytics → Read。只用于读取统计。

首次部署前，请先在 Cloudflare Dashboard → Workers & Pages → Create application → Create Worker，使用 Hello World 模板创建名为 `opera-lirico-ops` 的 Worker，并启用 workers.dev。然后创建部署 Token，给这个 Worker 授予 Workers Editor（旧权限界面可能显示为 Workers Scripts Edit）。这样部署凭证只需要管理这个 Worker，不必长期持有整个账户的 Admin 权限。

不要使用 Global API Key，也不要把这些 Token 发到聊天或写进代码。Cloudflare Account ID 可在 Cloudflare Dashboard 的账户概览中复制。

## 部署

添加以上 Secrets 后，进入 GitHub 仓库 Actions，运行 **Deploy private operations dashboard**。也可以修改 `ops-dashboard/` 下文件后合并到 main 自动部署。

首次部署需要 Cloudflare 账户已启用 Workers & Pages，并激活 workers.dev 子域名。部署日志会显示后台 URL，格式为：

`https://opera-lirico-ops.<你的-workers.dev-子域名>.workers.dev`

打开 URL，使用 `OPS_DASHBOARD_PASSWORD` 登录。

## Newsletter 人工审核发送

- `NEWSLETTER_SEND_ENABLED` 由 GitHub Actions 仓库变量控制；未设置或不等于 `true` 时默认关闭。初期保持关闭，完成预览、KV 绑定和测试后，管理员才可在 Settings → Secrets and variables → Actions → Variables 中设置为 `true`。
- 发送按钮仅对 `opera-lirico-weekly-YYYY-MM-DD-voiced` 格式、仍处于 `draft` 状态且 `archival_mode=disabled` 的邮件开放。
- 后台先显示正文预览与当前有效订阅人数；点击「审核并发送」后还会要求浏览器二次确认。
- Worker 验证登录会话和严格同源请求，使用 `CONTENT_DRAFTS` KV 记录发送尝试，设置默认 250 人的收件上限。若 Buttondown 请求超时或结果不明确，后台锁定该次尝试，要求先人工核对 Buttondown 状态，不会自动重试。
- Buttondown API 把邮件状态改为 `about_to_send` 即会将邮件排入发送队列；这不是可撤回的草稿保存操作。必须先展开预览、检查声部条件段和退订页脚，再确认发送。
- 当前功能仅为人工审核发送；定时工作流不会自动发送。后续自动审核必须先经过多期 shadow mode 验证，自动发送开关默认关闭。

## 安全与数据边界

- 后台不在公开 GitHub Pages 中；只有知道地址且持有密码的人可查看。
- 会话 Cookie 使用 HttpOnly、Secure、SameSite=Strict，最长有效期 8 小时。
- 登录有基础失败次数限制；请使用强随机密码。
- Buttondown API 返回的邮箱字段只在 Worker 内存中用于计数，不会写日志、保存或返回给浏览器。
- 后台仅读取 Cloudflare RUM 数据和 Buttondown 订阅/草稿信息；只有在功能开关开启且管理员明确点击确认后，才会调用 Buttondown 发送状态接口。
- 如果 Cloudflare 统计暂时没有数据，可能需要等待 Beacon 收集并处理首批访问数据。

## 自动化失败提醒

仓库中的 `.github/workflows/workflow-failure-alert.yml` 监听项目工作流。任一受监控工作流失败时，会创建或更新一个统一的 GitHub Issue，附上失败运行链接、分支、提交和失败 Job，并提醒仓库维护账号。成功或取消的运行不会创建失败记录。该提醒只记录失败信息，不会自动重跑工作流或修改网站数据。

## 大师班候选审核

私有后台新增“大师班候选审核”区域，读取公开仓库中的 `data/masterclass_candidates.json`，并把人工审核决定保存在现有的 `CONTENT_DRAFTS` KV 命名空间中，使用独立的 `masterclass-review:` 前缀，与社交媒体草稿分开。

可选择三种状态：

- 核实通过（待发布）：仅允许主办方官方来源的候选项；表示已完成人工核实，仍需整理完整课程信息并单独更新 `data/masterclasses.json`。
- 需要补充信息：保留候选项，等待进一步核对。
- 排除：标记为不采用，不会自动从原始发现队列删除。

第三方目录只能作为发现线索，后台不会允许直接把第三方来源标记为核实通过。所有审核接口都要求有效后台会话；写入操作还会检查同源请求。审核记录保留一年，不包含订阅者邮箱或其他个人信息。

此流程不会自动发布大师班，也不会修改公开课程数据。只有经过核实、整理并单独提交到课程数据文件的内容才会展示在网站上。

## 数据口径与可信度检查

- Cloudflare 页面浏览量以 Web Analytics 的 RUM pageload 数据为准；它不等同于服务器请求量，也不代表独立真实访客。
- 访问次数（Visits）使用同一 Web Analytics 数据集的 `sum.visits`，不可与独立访客数（Unique visitors）混为一谈。
- 查询按日期聚合，并使用 `CF_WEB_ANALYTICS_SITE_TAG` 精确限定站点。该 Site Tag 在 `ops-dashboard/wrangler.toml` 的变量中配置，不是 API 密钥；部署前应确认它与公开页面 Beacon 中的 token 对应。
- 最近 30 天查询返回的日期记录、最近事件日期和查询区间会显示在后台。若 API 查询成功但没有事件记录，后台显示“暂无事件记录”，指标显示为破折号，而不是把空结果伪装成真实的 0。
- 缺少 Account ID、Analytics Token 或 Site Tag、API 报错、返回字段异常，或结果达到 1,000 条分组上限时，统计会标记为不可用，不展示为完整数据。
- Cloudflare 对较长时间范围的数据可能使用采样估算，因此趋势适合观察变化，不应当作精确审计数字。页面统计也可能因浏览器隐私设置、广告拦截或 Beacon 尚未上报而低于实际访问量。
- Buttondown 有效订阅人数按仍处于订阅列表中的类型统计；未确认、已退订、被屏蔽或不可投递的地址不计入。新增订阅按当前有效状态并依据创建时间统计过去 7 天新增。
