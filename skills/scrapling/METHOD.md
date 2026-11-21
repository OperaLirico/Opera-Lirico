# scrapling 方法卡

上游 SKILL.md 6.4KB + references 约 25KB。要用的部分如下。

## 一、先问三句，再动手

1. 这个站我有权抓吗（公开公告页 = 有；登录后、付费内容 = 没有）。
2. robots.txt 与 ToS 怎么说。
3. 目标页是静态 HTML，还是要 JS 渲染。

三句答完，Fetcher 基本就定了；答不出来先用 Fetcher 试，403/空壳再升 StealthyFetcher。

## 二、CLI 先跑，别一上来写脚本

```bash
scrapling extract get "URL" out.md --ai-targeted
scrapling extract fetch "URL" out.md --ai-targeted --network-idle
scrapling extract stealthy-fetch "URL" out.md --ai-targeted --solve-cloudflare
```

`--ai-targeted` 会把正文清洗成适合模型读的形状（剥导航、剥脚本），省 token 也少被页面里的注入文本带偏。复杂登录、多页流程、结构化多字段才写 Python。

## 三、报错怎么查

| 现象 | 先看 |
|---|---|
| 403 / 挑战页 | `references/troubleshooting.md` → 升级 StealthyFetcher |
| 拿到空壳 | 页面是 SPA，换 DynamicFetcher |
| 选择器抓空 | 自适应重定位；或 `references/site-patterns.md` 看有没有记录 |
| 装不上 / 版本旧 | `references/maintenance.md` |
| 需要登录态 | `references/cookie-vault.md`，真实值只进 `.local.md` |

## 四、超时单位会咬人

- `Fetcher` / `FetcherSession`：**秒**（`timeout=30`）
- `StealthyFetcher` / `DynamicFetcher`：**毫秒**（`timeout=60000`）

写脚本时混用这两个单位，症状是「看起来卡住」而不是报错。

## 五、经验必须沉淀，分两处

- 通用站点类型（例如「意大利剧院公告都挂在 /bandi 下、分页在 JS 里」）→ 去敏后写进 `references/site-patterns.md`。
- 私有 / 登录态细节 → 只写 `references/site-patterns.local.md`，不提交。

这一步不做，下次还得从头试。

## 六、和现有流程的接法

- `daily-scrape`：源站抓空时先用 CLI quick path 复现，再决定换 Fetcher 还是改选择器。
- `pdf-bando-extraction`：先拿到 PDF 直链，再交给它解析；不要在 Scrapling 里解析 PDF。
- `official-source-verification`：抓回来的字段仍要回官方页二次核对，抓取成功不等于内容可信。
