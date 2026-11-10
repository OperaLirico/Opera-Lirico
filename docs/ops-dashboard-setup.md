# Opera Lirico 私有运营后台

后台运行在独立的 Cloudflare Worker，不部署到公开 GitHub Pages。页面需要密码登录；浏览器只接收统计汇总和邮件草稿标题，不接收订阅者邮箱或 API 密钥。

## 连接后可查看

- Cloudflare Web Analytics：过去 30 天页面浏览量、访问次数和每日趋势。
- Buttondown：当前有效订阅人数、过去 7 天新增人数、待审核草稿数量、标题和创建日期。
- 后台只读，不包含发送邮件、订阅者导出或删除操作。现有每周邮件流程仍然只创建草稿。

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

## 安全与数据边界

- 后台不在公开 GitHub Pages 中；只有知道地址且持有密码的人可查看。
- 会话 Cookie 使用 HttpOnly、Secure、SameSite=Strict，最长有效期 8 小时。
- 登录有基础失败次数限制；请使用强随机密码。
- Buttondown API 返回的邮箱字段只在 Worker 内存中用于计数，不会写日志、保存或返回给浏览器。
- 后台仅读取 Cloudflare RUM 数据和 Buttondown 订阅/草稿信息，不调用任何邮件发送接口。
- 如果 Cloudflare 统计暂时没有数据，可能需要等待 Beacon 收集并处理首批访问数据。

## 数据口径说明

Cloudflare 页面浏览量以 Web Analytics 的 RUM pageload 数据为准；它不等同于服务器请求量，也不代表独立真实访客。订阅人数只统计有效订阅类型；未确认、已退订、被屏蔽或不可投递的地址不计入有效订阅数。
