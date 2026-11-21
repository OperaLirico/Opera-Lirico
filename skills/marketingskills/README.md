# skills/marketingskills

上游：`coreyhaines31/marketingskills`（MIT，© Corey Haines）
固定提交：`5b2b400eec1e7e1cec76245a715d0b0d4fd2a9c1`（2026-11-20）
来源：https://github.com/coreyhaines31/marketingskills

## 收了哪几个，为什么只收这几个

上游共 50 多个技能。整包收进来是噪音，只用得上四个：

| 技能 | 对本站的用处 |
|---|---|
| `seo-audit` | 抓取/收录体检、标题与描述、内链、Core Web Vitals、索引问题 |
| `schema` | JSON-LD：为每条开放招募加 `Event`，为站点加 `Organization` + `WebSite`，列表页加 `BreadcrumbList` |
| `cro` | 订阅转化：表单字段、首屏行动点、减少选择成本 |
| `emails` | 周报邮件：主题行、序列、退订口径 |

其余（ads、aso、cold-email、paywalls、pricing、influencer、sms…）与这个站无关，不收。

## 这个仓库里有什么

- `METHOD.md`　方法卡（中文）：SEO 的优先级顺序、schema 的两个坑、CRO 的检查起点
- `sync.sh`　按固定提交拉全量到 `upstream/`，只读这四个子目录

## 两个必须知道的坑

1. **静态抓页面看不到 JSON-LD**：`curl` / `web_fetch` 会剥掉 `<script>`，很多插件是 JS 注入的。查 schema 必须渲染后跑 `document.querySelectorAll('script[type="application/ld+json"]')`——我们本来就有 headless Chrome，这条路走得通。
2. **schema.org 语法合法 ≠ Google 给富结果**：上 `Event` 之前先查 Google 当前支持的富结果类型，别写了个不出现的标记。

## 边界

CRO 会提示改文案。本站文案不归我改，我最多把问题列出来，改不改由你做。
