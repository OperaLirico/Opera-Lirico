# 来源自动审核与机会数据复核日报

- 审核时间：2026-11-12T11:49:52+01:00（Europe/Rome）
- 仓库：`OperaLirico/Opera-Lirico`
- 本批来源审核：8 条（`sources_extra.json` 中 6 条 legacy + `source_candidates.json` 中 2 条候选）
- 审核方式：逐页核对官方机构导航/发布方说明/实际内容；第三方线索不作为官方公告证据。
- 未删除任何来源，未更改生产抓取启用状态，未发布新机会。

## 一、来源自动审核报告

### 本日审核数量与分类

| 分类 | 数量 | 说明 |
|---|---:|---|
| auto_approved_official | 1 | candidate-2 复核后仍为高置信度官方来源；本日未新增官方来源 |
| auto_approved_third_party | 2 | candidate-1 复核保留；source 101 新完成第三方来源审核 |
| needs_review | 2 | source 97、98，保留待核实 |
| duplicate_candidate | 1 | source 102 的具体公告与 candidate-1 重复；不删除独立来源域名 |
| irrelevant_candidate | 2 | source 96、99，只标记排除建议 |
| unavailable_temporary | 0 | 本批无暂时不可访问项 |
| retired_candidate | 0 | 无足够跨时间证据提出退役建议 |

### 官方来源复核

- **candidate-2 — Teatro Lirico Sperimentale di Spoleto**：仍为 `auto_approved_official`、high confidence。官方 `Bandi e avvisi` 页面直接链接到 81ª edizione 专页；专页说明比赛日期为 2027-02-16 至 2027-02-20，并写明章程及更多信息稍后公布。当前没有报名截止日期、资格、费用、申请入口或官方 PDF，因此仍只是来源候选，不创建机会记录。
  - 证据：[官方公告目录](https://www.tls-belli.it/bandi_e_avvisi/) · [81ª edizione 专页](https://www.tls-belli.it/concorso-di-canto-2026/)
- **source 96 — INDA / Filottete**：官方页面明确写明试演仅面向男性演员；不是歌唱岗位，标记 `irrelevant_candidate`、high confidence。
  - 证据：[INDA 官方公告](https://www.indafondazione.org/bando-audizioni-per-filottete/)
- **source 99 — Teatro Trianon Viviani**：官方公告寻找 Pulcinella 角色演员，要求那不勒斯语表演能力，没有歌唱岗位；标记 `irrelevant_candidate`、high confidence。
  - 证据：[Trianon 官方公告](https://www.teatrotrianon.org/audizioni-per-la-produzione-pulcinella-ovvero-una-cosa-che-somiglia-al-mondo/)

本日**没有新晋升的官方来源**；candidate-2 是对既有高置信度判断的复核，不代表新机会已发布。

### 第三方来源保留

- **candidate-1 — Provinispettacolo Musica**：仍为 `auto_approved_third_party`、high confidence，只作线索发现。第三方页面称 Opera e Lirica 歌唱家试演申请截止 2026-11-13、试演 2026-11-17；Opera e Lirica 官方 Job Position 页面目前展示的是 Social Media Content Creator 招聘，并未发布这场歌唱试演。Roma Turismo 可确认机构及其官网，但不能确认该试演。**不能将这条线索写入机会库或标为官方。**
  - 证据：[第三方音乐栏目](https://www.provinispettacolo.it/casting/musica/) · [Opera e Lirica 官方招聘页](https://www.opera-lirica.com/en/content/11-job-position) · [Roma Turismo 机构页](https://www.turismoroma.it/it/luoghi/opera-e-lirica)
- **source 101 — Musical.it Audizioni**：本日完成 `auto_approved_third_party`、medium confidence。该站是音乐剧试演信息门户，明确接收制作方/学校提交公告，也声明不对公告内容承担责任。可作为音乐剧方向的发现渠道，不应与歌剧院官方招募混为一类；每条机会仍须回到制作方原始公告核验。
  - 证据：[Musical.it Audizioni](https://www.musical.it/audizioni/)

### 待核实、重复及排除建议

- **source 97 — Winterwerft**：`needs_review`、medium confidence。开放征集包含 musicians，但属于跨领域戏剧/表演艺术项目，没有明确声乐或歌剧要求；本轮申请已于 2026-11-08 截止。保留待观察，不生成当前机会。
  - 证据：[Winterwerft Open Call](https://winterwerft.de/opencall/)
- **source 98 — Fondazione Campania dei Festival**：`needs_review`、medium confidence。官方 2027 Campania Teatro Festival 项目提案表包含 Musica 类别，截止 2026-11-15 16:00；但它面向艺术项目/团体提案，并非个人歌唱家试演。暂不作为个人声乐机会发布。
  - 证据：[官方 Partecipa al Festival 表单](https://contact.fondazionecampaniadeifestival.it/partecipa-al-festival/)
- **source 102 — Casting e Provini**：`duplicate_candidate`、high confidence。它转载的 Opera e Lirica 2026-11-17 试演，与 candidate-1 的具体公告为同一条线索。重复范围仅为该公告；该网站域名本身是独立第三方来源，**不删除、不停用**，只避免同一机会重复入库。
  - 证据：[Casting e Provini 公告](https://www.castingeprovini.com/audizioni-cantanti-lirici-professori-dorchestra-roma/) · [Provinispettacolo 公告](https://www.provinispettacolo.it/audizioni-opera-lirica-roma-cantanti-professori-orchestra/)
- 本批没有 `unavailable_temporary` 或 `retired_candidate`。

### 审核覆盖与批次进度

- `data/sources.json` 合并清单：44 条（29 条生产核心来源 + 15 条 legacy 监控来源）；`sources_extra.json` 是这 15 条的注册明细，不重复计数。
- `data/source_candidates.json`：2 条候选，本日 2/2 复核。
- `sources_extra.json` 中本批审计 6/15 条 legacy，剩余 9 条；这些 legacy 项被周度覆盖扫描监控，但不属于 29 条生产核心抓取来源。
- 最近周度全量扫描：46/46（44 条合并登记来源 + 2 条候选），0 失败、0 剩余。此结果是可访问性/正文变化基线，不证明没有漏报。
- P2 抓取策略评估：15/44 已完成，29/44 仍为 `baseline_only`。第三批 5/5 页面已采集并归档；未证明替代引擎优于现有 Scrapling，因此生产抓取策略没有切换。
- 月度机构覆盖率复核：本次未执行；当前仓库检查点中未找到可验证的本月复核记录，不宣称已完成。
- 本日异常关注：Opera e Lirica 试演仍缺主办方一手公告；Campania 音乐项目提案截止日临近但不是个人试演。

## 二、机会数据质量

- 当前公开机会：7
- 7 天内截止：0
- 30 天内截止：7
- 已过期但仍公开：0
- 缺申请链接：0
- 缺官方 PDF：0
- 待核实 / 非官方公开记录：0
- 日期时区错误：0
- 超过 7 天未核验：0
- 重复 ID：0
- 前端发布门槛违规：0

自动质量快照生成于 `2026-11-12T08:39:03+01:00`。本日 11:49 对 7 条公开机会逐条重新打开官方公告/官方 PDF；未发现截止时间或报名状态变化，已将每条记录的 `checked_at`、`last_verified_at` 更新至本次核验时间，并追加官方证据。

### 7 条机会逐项复核

| 机会 | 报名截止（Europe/Rome） | 本日结果 |
|---|---|---|
| Teatro Carlo Felice — Coro Tenori | 2026-11-23 23:59 | 官方网页与 PDF 一致；试唱 2026-11-28 14:00 |
| AsLiCo 78° Concorso 2027 | 2026-11-25 18:00 | 官方 PDF 确认；报名费 €70；A/B 两个年龄门槛不同 |
| Francesco Morlacchi 2026 | 2026-11-30 23:59 | 官方网页确认；18–35 岁；报名费 €80 |
| Teatro Massimo — 2 Contralti | 2026-12-04 12:00 | 截止日确认；网页写 12 月 19 日 10:00，PDF 写 12 月 20 日 10:00；结构化试唱日期继续留空 |
| Teatro Carlo Felice — Coro Bassi | 2026-12-07 23:59 | 官方网页与 PDF 一致；试唱 2026-12-15 09:00 |
| Teatro Carlo Felice — Coro Baritoni | 2026-12-07 23:59 | 官方网页与 PDF 一致；试唱 2026-12-16 14:00 |
| Teatro Carlo Felice — Accademia 2027 | 2026-12-10 23:59 | 官方 PDF 确认；申请及课程免费；出生日期门槛为 1997-01-01 起 |

本日没有改写任何报名截止日、资格条件或试唱日期；Teatro Massimo 的冲突仍需主办方澄清。7 条记录均保留官方申请入口和官方 PDF。

## 三、本次代码与数据变更

- `grow_sources.py`：证据化审核记录现在会在后续来源刷新中完整保留；只有尚未完成证据化审核的 legacy 条目继续使用启发式筛查。
- `tests/test_source_quality.py`：新增测试，验证证据化状态/证据不会被下一次刷新覆盖，同时未审核条目仍会接受启发式筛查。
- `data/sources_extra.json` 与合并的 `data/sources.json`：本批 6 条 legacy 记录新增来源身份、相关性、证据 URL、核验时间、置信度及处置说明；不删除、不启用。
- `data/source_candidates.json`：2 条候选补充本日复核证据。
- `data/opportunities.json`：7 条公开机会更新核验时间并追加官方证据；没有改动报名或试唱日期。
- 本报告保存在 `.github/audits/`，不进入网站公开页面。

## 四、下一步

1. 下一批继续审计剩余 9 条 legacy 来源，优先处理仍可能含声乐岗位的条目。
2. 下一轮 P2 从尚未评估的高价值官方来源中选择 5 条，不重复已完成的 15 条。
3. 继续观察 Teatro Massimo 网页/PDF 的日期冲突；未获得官方更正前保持结构化日期为空。
4. 对 Opera e Lirica 2026-11-17 试演继续寻找主办方一手公告；没有一手证据则不发布。
