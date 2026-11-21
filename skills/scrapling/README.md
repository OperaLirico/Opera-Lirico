# skills/scrapling

上游技能：`Cedriccmh/claude-code-skill-scrapling`（MIT）　版本：随上游
固定提交：`85dd89f5f85a6326712c516bc82f84c2ceb28c19`（2026-06-18）
底层库：`D4Vinci/Scrapling`（BSD-3-Clause）
来源：https://github.com/Cedriccmh/claude-code-skill-scrapling

## 它是什么

把 Scrapling 的抓取能力做成一套可执行的决策流程：判断目标站点属于哪一类 → 选 Fetcher → 出脚本 → 跑 → 沉淀站点经验。

关键在 Fetcher 分级，不是「一律上浏览器」：

| 目标 | Fetcher | 代价 |
|---|---|---|
| 已有 HTML 只需解析 | Selector | 无网络 |
| 静态页、无反爬 | Fetcher（curl_cffi） | 最快 |
| 需表单登录 | FetcherSession | 保会话 |
| 有 Cloudflare / WAF | StealthyFetcher（Camoufox） | 最慢 |
| SPA 需 JS | DynamicFetcher（Playwright） | 慢 |

另有自适应解析：页面改版后元素选择器能自动重定位——这正对着我们每天抓剧院公告最容易断的地方。

## 这个仓库里有什么

- `METHOD.md`　方法卡（中文）：决策树、CLI 三条命令、守卫条款、经验怎么沉淀
- `sync.sh`　按固定提交拉全量到 `upstream/`

没有：`upstream/`（含 references/templates，需要时现拉）、Python 依赖（`pip install "scrapling[fetchers]"` + `scrapling install` 由使用方自行执行）。

## 什么时候用

- `daily-scrape` 的某个来源突然抓空 / 403 / 只拿到壳
- 新剧院、新音乐学院、新比赛报名站要接进来
- 公告在 PDF 里，需要先定位再交给 `pdf-bando-extraction`

## 边界（和站点既有约束一致）

技能自带守卫条款，和我们的规矩对得上：只抓有授权的公开内容；**不绕付费墙、验证码、登录限制**；大规模爬之前先看 robots.txt / ToS 并降并发；真实 cookie 只写 `.local.md`、不入库。IMSLP 那条 15 秒同意关卡属于访问控制，不得绕，只存元数据与链接。
