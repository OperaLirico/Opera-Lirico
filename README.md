# 声乐机会 Italia

一个面向手机的意大利声乐机会网页应用（PWA）。它每天用 Scrapling 读取 15 个公开来源页面，展示来源状态与公告相关原文片段，并保留主办方链接。经过人工确认的机会单独显示在顶部；来源文字自动抓取不等于机会仍开放。

## 每天自动更新

`.github/workflows/daily-scrape-and-publish.yml` 在每天 06:15 UTC 启动抓取并发布网页；可在 GitHub Actions 页面手动运行。GitHub Actions 运行，因此不依赖个人 Mac 开机。UTC 时间遇夏令时切换不变，意大利当地显示时间随季节相差一小时。

## 发布到 GitHub Pages

1. 将本项目放入一个 GitHub 仓库，保留 `outputs/vocal_opportunities_app` 路径。
2. 在仓库 Settings → Pages → Build and deployment 中，将 Source 选为 **GitHub Actions**。
3. 推送工作流后，在 Actions 中运行 **Daily scrape and publish**；成功后会生成公开网页链接。
4. PWA 必须经 HTTPS 打开才能安装，GitHub Pages 会提供 HTTPS。

仓库发布为 Public 时网页和源码都能被任何人查看。页面不收集访客个人信息。

## 添加到手机主屏幕

- iPhone：用 Safari 打开公开网页，点“分享”图标，再点“添加到主屏幕”。
- Android：用 Chrome 打开公开网页，点“安装应用”提示，或菜单中的“安装应用/添加到主屏幕”。

安装后会以独立窗口显示，并缓存页面外壳；打开联网后重新载入最新抓取数据。

## 数据边界

- 每日读取官网当前公开页面，不绕过登录、验证码或付费限制。
- 页面结构变化、PDF 或第三方报名表可能无法自动解析；页面链接保留给用户复核。
- 自动匹配只用于显示公告原文线索，不自动断定报名是否有效，也不声称覆盖全部机会。
- 机会资格、截止时间和费用以主办方原始公告为准。
