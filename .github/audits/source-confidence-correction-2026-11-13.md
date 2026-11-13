# 官方来源置信度门槛纠正 — 2026-11-13

- 时间：2026-11-13T11:34:22+01:00（Europe/Rome）
- 触发原因：按“只有 high-confidence 官方来源才可标记 auto_approved_official”的硬规则复核最新来源清单。
- 纠正对象：source-12（Ente Lirico Italiano - Premio E.L.I.）、source-15（Concorso Francesco Morlacchi）。
- 两条记录均保持相关性为 relevant、置信度为 medium，但将 `publisher_status` 从 `official` 改为 `unverified`，将 `auto_review_status` 改为 `needs_review`。这不是判定其为假来源，而是现有证据不足以支撑“官方身份已高置信度确认”。
- 不删除来源、不改变生产抓取启用状态、不影响机会库发布记录。

## 证据与原因

| source_id | 已确认的内容 | 缺少的证据 | 处置 |
|---|---|---|---|
| source-12 | 比赛页面含歌剧歌手比赛规则、声部、报名信息；页脚有 Ente Lirico Italiano ETS 名称、地址、电话和税号。 | 目前证据主要来自同一站点自述/页脚，尚未形成独立机构目录或外部官方交叉证明。 | `needs_review` / `unverified` / medium |
| source-15 | 比赛页面自述由 Associazione Musicale Internazionale La La La 主办、Grande Lirica Umbria APS 协办，并提供联系邮箱。 | 主办方身份尚缺独立机构目录或可核验的外部官方交叉证据。 | `needs_review` / `unverified` / medium |

## 修正后的 44 条登记来源分类

- auto_approved_official：24
- auto_approved_third_party：5
- needs_review：5
- irrelevant_candidate：9
- duplicate_candidate：1
- 合计：44

两个候选来源另行统计，不计入上述 44 条登记来源；它们仍未自动激活到生产抓取。

## 后续

如能从主办协会/机构的独立官网、政府/协会登记目录或官方社交账号取得直接证据，再重新评估。下一次周度覆盖扫描将把本次来源元数据作为当前分类输入；此前周度 checkpoint 保留为历史记录，不手动改写。


## 后续复核 — source-12（同日）

在查看该机构官方主站后，source-12 的身份直接证据已补足：主站介绍 E.L.I. 的机构使命与声乐活动，主站导航列出 Premio E.L.I.，官方联系/Newsletter 页面列出 E.L.I. - Ente Lirico Italiano ETS 的地址、电话和税号。因此 source-12 从 `needs_review` 恢复为 `auto_approved_official`，置信度 high。

证据：
- [机构官方主站](https://www.enteliricoitaliano.it/) — 机构介绍、声乐活动与联系方式
- [Premio E.L.I. 官方栏目](https://www.enteliricoitaliano.it/premioeli/)
- [Premio E.L.I. 2026 官方公告](https://www.enteliricoitaliano.it/premioeli/bando-concorso-2026/)
- [官方联系/Newsletter 页面](https://www.enteliricoitaliano.it/newsletter/) — ETS 名称、地址、电话及税号

source-15 仍保持 `needs_review` / `unverified` / medium；第三方目录对比赛信息的转载不能替代主办协会的独立官方身份依据。

**当前 44 条登记来源分类**：auto_approved_official=25、auto_approved_third_party=5、needs_review=4、irrelevant_candidate=9、duplicate_candidate=1。
