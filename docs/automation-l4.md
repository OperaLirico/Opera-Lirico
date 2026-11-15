# Automation level L4 — 无人值守闭环

本文档记录 2026-11-15 把整条流水线从 L3 推到 L4 的改动、验证方式和保留的人工闸门。
判断标准是"没有人在场时，系统还能不能自己把活干完、自己发现自己坏了"。

## 一、层级定义（本项目口径）

| 级别 | 含义 | 判据 |
| --- | --- | --- |
| L1 | 手动 | 每一步都要人触发 |
| L2 | 脚本化 | 命令可复现，仍需人跑 |
| L3 | 定时 + 审计 | 定时触发、有测试与告警，坏了要人查 |
| L4 | 无人值守闭环 | 定时产出 + 自动审核 + 失败自愈 + 数据看门狗，人只处理被升级的例外 |

## 二、L4 的四根支柱

### 1. 定时生产（原已具备）

| 时间 (UTC) | Workflow | 产出 |
| --- | --- | --- |
| 02:17 | KV backup | 内容草稿 KV 快照 |
| 06:15 | Daily source refresh | 源站抓取与数据更新 |
| 06:45 | Discover masterclasses | 大师班候选 |
| 07:15 | Generate social content drafts | 社交文案草稿入队 |
| 09:00 | System health check | 19 项健康检查 + 全量单测 |
| 10:00 | Workflow failure digest | 24h 失败汇总 issue |
| 10:30 | Project agent daily review | 项目日报 |
| 每周一 06:30 / 08:00 / 08:30 | 源发现 / 邮件草稿 / 覆盖率 | 周更物料 |
| 每月 1 日 09:00 | PDF signature audit | 签名审计 |

### 2. 自动审核（`auto-review-queue.yml` + `content_engine/auto_review.py`）

每 6 小时跑一次，把"全部人工过一遍"改成"机器先判、人只判例外"。

自动通过必须同时满足：标题完整、正文 120–900 字、来源为 HTTPS 且域名在仓库官方来源清单内、无绝对化违规表述、分类存在、与已通过内容不重复、草稿入库超过 60 分钟、单轮上限 8 条。
任一条不满足则保持 `pending_review`，并把原因写进 `record.review`，人打开后台就能看到机器为什么不敢签。

判定结果只写 `approved`，**不会自动发布到任何平台**；"发布"这一步仍然手上操作，因为对外投递不可撤回。

### 3. 失败自愈（`self-heal.yml`，改 `system-health-check.yml`、`deploy-ops-dashboard.yml`）

- `system-health-check.yml`：测试套件与健康检查各自失败后 45 秒重试一次，单次网络抖动不再把当天判成红的。
- `self-heal.yml`：每 30 分钟扫描最近 6 小时的失败 run，只对白名单内的生产任务重跑，单个 run 最多重跑 2 次，一轮最多 4 个，避免风暴。
- `deploy-ops-dashboard.yml`：部署失败时自动 `wrangler rollback` 回上一版本，避免坏版本留在线上。

### 4. 数据看门狗（`analytics-watchdog.yml` + `analytics_watchdog.py`）

每天两次（09:45 / 21:45 UTC）验证：

- GraphQL 能返回数据（siteTag 用站点 id，不是 beacon token）
- 7 天窗口内数据不是空的，且最近 48 小时不是断流
- 最新日期没有冻结（超过 48 小时无新数据即判失败）
- 运营后台 `/api/health` 仍为 ok

任一项不成立 → 该 run 失败 → 进 failure digest，必要时被 self-heal 重跑。

## 三、刻意保留的人工闸门

| 环节 | 为什么不做全自动 |
| --- | --- |
| 社交平台发布 | 对外投递不可撤回，误发成本高于一人点击 |
| 邮件发送 | 直接触达订阅者，且当前只有草稿链路；自动发信需要单独授权与退订合规检查 |
| 大师班候选核实 | 需要判断"官方页面证据是否支持这条信息"，规则无法穷举 |
| 数据删除/重构 | 不可逆，且历史上没有自动删除的需求 |

这四项保留人工，不等于停在 L3：L4 的定义是"人只处理例外"，而不是"人不存在"。

## 四、跑起来怎么验证

1. Actions 里手动 `Run workflow` 触发 `Analytics watchdog`，应返回 7 天浏览/访问数字并 exit 0。
2. 手动触发 `Auto-review content queue`，看 step summary 的 approved / escalated 计数；后台队列里被升级的条目应带机器给的理由。
3. 手动触发 `Self-heal failed automations`，摘要显示 "Nothing to heal" 或列出重跑记录。
4. 故意让一次 `System health check` 失败（例如改动一个断言），观察 30 分钟内是否被自动重跑。

## 五、回滚与调参

- 部署回滚：`wrangler rollback --config ops-dashboard/wrangler.generated.toml --yes`（部署失败时流水线自动执行，见 `deploy-ops-dashboard.yml` 末尾的 `if: failure()` 步骤）
- 回滚演练：提交信息里带 `[rollback-drill]` 时，`deploy-ops-dashboard.yml` 会在部署与密钥上传之后再跑一个必然失败的步骤，触发自动回滚；只在第一次尝试触发，被 self-heal 重跑时自动跳过
- 自动审核收得太紧/太松：改 `content_engine/auto_review.py` 里的 `MAX_APPROVALS`、`MIN_AGE_MINUTES`、`BANNED_CLAIMS` 与长度阈值，环境变量 `AUTO_REVIEW_MAX_APPROVALS`、`AUTO_REVIEW_MIN_AGE_MINUTES` 可覆盖前两项。
- 看门狗阈值：`analytics_watchdog.py` 里 `pv7 >= 30` 与 48 小时冻结判据；站点流量还小的时候不要调低，否则正常的零访问会被当成故障。
- 自愈范围：`self-heal.yml` 的 `SAFE` 白名单，加新定时任务时记得加进去。

## 六、已知边界

- Cloudflare `sum { visits }` 与 `count` 在早期数据里几乎相等，口径仍需观察，看门狗会以 warning 形式记录 `visits > pageviews`。
- Workers Observability 未开启，Worker 内部异常只能通过接口表现推断；如需根因日志要先在 Cloudflare 打开日志。
- `newsletterUrl` 仍指向旧的 Buttondown 用户名，刊名与站点品牌尚未统一，属内容侧待办，不阻塞 L4。订阅入口已改为站内表单（见 `docs/newsletter-segmentation.md`），`newsletterUrl` 现在只作后台链接使用。

## 七、验证记录（2026-11-15 实测）

| 检查 | 结果 |
| --- | --- |
| Analytics watchdog 手动触发 | 成功；6 天有效数据，7 天浏览 68 / 访问 53，最近 48h 浏览 9 |
| Auto-review content queue 手动触发 | 成功；自动通过 8 条（本轮上限），升级人工 9 条；后台队列 17 条 → 8 条「已审核，待手动发布」+ 9 条待审 |
| Self-heal 手动触发 | 发现 2 个失败 run（System health check #29 / #30），各重跑一次，两次均转为成功 |
| System health check | 转绿。根因是两个过期测试断言：曲库归档必须按需载入、失败汇总只看关键 workflow |
| Deploy dashboard | 成功；Worker 已支持 `record.review` 字段，自动审核的理由会存在草稿记录上 |

**已补测**：`wrangler rollback` 原先只有代码、从未触发，2026-11-15 用 `[rollback-drill]` 演练实测通过，见下节。

**仍保留人工**：邮件真正发往订阅者（当前只有草稿），社交平台发布，大师班候选核实。

## 八、回滚演练（2026-11-15 实测）

做法：在部署与密钥上传都成功之后，插入一个必然失败的步骤（只在提交信息含 `[rollback-drill]` 时触发），让流水线走到 `if: failure()` 的回滚分支。

结果：

- 演练 run（commit `5a895b6`）里「Rollback drill」失败，紧接着「Roll back the Worker when a deploy fails」执行成功，日志中没有出现 "Rollback failed"。
- Cloudflare 版本列表：本次部署产生的新版本 `a7c5e9f5` 停在 Ready、不接管流量；活跃版本退回它之前的 `0c5fe80e`（100% 流量）。也就是说自动回滚真的把流量换回了上一版本。
- 回滚后线上探活正常：`/api/health` 返回 `{"ok":true,"service":"opera-lirico-ops"}`，后台首页 HTTP 200。

边界：`wrangler rollback` 只对「新版本已上传、但后续步骤失败」有用；失败若发生在部署之前（没有生成 `wrangler.generated.toml`），脚本会直接跳过并说明原因，因为那时没有可回滚的版本。

### 演练留下的那条红 run（按设计）

演练 run `43736732435`（Deploy dashboard #57）会一直停在 failure，因为它就是"故意失败"的那一条：

- 第 1 次尝试：drill 步骤失败 → 自动回滚成功。
- 第 2、3 次尝试：self-heal 各重跑一次（当时那条 run 用的还是旧版工作流文件，里面没有 `github.run_attempt == 1` 这道守卫，所以又失败、又回滚一次）。
- 到 attempt 3 后 self-heal 主动放弃，摘要写的是 "gave up on Deploy private operations dashboard #57: attempt 3 already"，不再重跑。

这顺带验证了重试上限确实把次数卡死在 3 次尝试。主分支现在带 `run_attempt == 1` 守卫，以后再做演练，被 self-heal 重跑的那一次会跳过 drill 并直接转绿，不会再留红。

生产始终没受影响：每次回滚后 `/api/health` 都是 `{"ok":true,...}`，后台首页 200。
