# 来源自动审核日报 — 2026-11-16

- 审核时间：2026-11-16T13:04:58+01:00（Europe/Rome）
- 本批复核：8 条（6 条既有待观察/候选来源 + 2 条从失败的周度发现任务日志恢复的临时候选）
- 分类：auto_approved_official=1；auto_approved_third_party=2；needs_review=3；irrelevant_candidate=2；duplicate_candidate=0；unavailable_temporary=0；retired_candidate=0。
- 本日没有新增可直接启用的生产来源；既有来源状态未做晋升/删除/停用；所有候选 production_activation 继续为 false。
- 周度覆盖：2026-W47 完成 46/46，0 抓取失败、0 受限、0 抽取错误；15 条规范化正文哈希变化（变化不等于新机会）。

## 逐项复核

| 条目 | 结论 | 置信度 | 本次依据与处置 |
|---|---|---|---|
| candidate-1 — Provinispettacolo Musica | auto_approved_third_party（保持） | high | [音乐分类页](https://www.provinispettacolo.it/casting/musica/)明确覆盖 cantante/musicisti；[投稿说明](https://www.provinispettacolo.it/proponi-casting/)说明公告来自外部投稿并提示并非所有公告都可靠。仅作为第三方发现入口，单条机会必须回到主办方核实。 |
| candidate-2 — Teatro Lirico Sperimentale di Spoleto | auto_approved_official（保持候选状态） | high | 官方[招标公告目录](https://www.tls-belli.it/bandi_e_avvisi/)直接链接至[声乐比赛页面](https://www.tls-belli.it/concorso-di-canto-2026/)，页面说明面向青年歌剧歌手，日期为 2027-02-16 至 2027-02-20；但 bando 尚未发布，页面标题元数据写 80°、正文写 81ª。继续保留 pending_manual_review，不创建机会、不启用生产抓取。 |
| source-97 — Winterwerft Open Call | needs_review（保持） | medium | [官方 Open Call](https://winterwerft.de/opencall/)为跨领域戏剧/表演项目，页面包含音乐人但无歌剧、声乐或歌手专属条件；截止日 2026-11-08 已过。网页研究工具返回 403，但同日仓库抓取快照为 HTTP 200，因此不标记暂时不可用。 |
| source-98 — Fondazione Campania dei Festival | needs_review（保持） | medium | [基金会官方项目页](https://contact.fondazionecampaniadeifestival.it/partecipa-al-festival/)提供艺术项目/音乐类别，但对象是项目或团队，不是个人歌手试唱；申请截止 2026-11-15 16:00 已过。保留为可能的项目申报来源，不创建个人歌手机会。 |
| source-121 — Robin Hood casting | auto_approved_third_party（保持） | medium | [第三方公告](https://www.provinispettacolo.it/casting-robin-hood-prima-della-leggenda-piemonte/)列出 soprano、tenore、baritono、basso 等角色，页面标注截止 2026-11-16（未写具体时刻）；仍未找到制作方一手公告。作为第三方线索保留，不作为官方机会发布；截止日期为今天，是否仍可报名无法确认。 |
| source-123 — Torino Fringe: Fringe in Progress 2027 | needs_review（保持） | medium | [官方项目页](https://www.tofringe.it/partecipa/fringe-in-progress-selezione-per-progetti-in-crescita-torino-fringe-festival-2027/)面向 under-35 专业个人艺术家/公司，截止 2026-11-20，接受广泛表演艺术项目；未写明声乐/歌剧条件。继续观察，不当作单人歌手 audition。 |
| discovery-log-only — Orchestra Sinfonica Siciliana | irrelevant_candidate（不入队） | high | [官方招募页](https://orchestrasinfonicasiciliana.it/it/audizioni/bando-audizioni-eventuali-assunzioni-tempo-determinato-orchestra-lanno-2027)是 2027 年乐团器乐岗位，列出的岗位为乐器声部，没有歌唱职位。该项只从失败任务日志恢复，本次未写入候选库。 |
| discovery-log-only — Grand Théâtre de Genève Ballet | irrelevant_candidate（不入队） | high | [官方 audition 页面](https://www.gtg.ch/danseuses-danseurs-ballet-gtg-saison2027-2028)招募芭蕾舞者，非歌手/合唱团岗位。该项只从失败任务日志恢复，本次未写入候选库。 |

## 机会内容漏报：需要单独人工核验

本周全量覆盖中，**source-3 Teatro Massimo** 的正文哈希发生变化。检查其[官方 Audizioni 页面](https://www.teatromassimo.it/audizioni/)后发现一条当前机会库没有对应记录的公告：

- **Selezione pubblica per 1 Artista del coro – Basso**，Palermo。
- 官方 bando：[PDF](https://www.teatromassimo.it/wp-content/uploads/2026/11/BandoSelezione_1Basso_TM_2026.pdf)。
- 报名截止：**2026-12-04 12:00（Europe/Rome）**，通过 Teatro Massimo 官网在线表单提交。
- 试唱：**2026-12-19 10:00（Europe/Rome）**。
- 招聘：1 个 Basso 合唱团岗位，拟全职、无固定期限合同；最低 18 岁，非欧盟申请人须持有允许在意大利全职无固定期限工作的居留许可，并须具备足够意大利语能力和中学学历。
- 官方 PDF 未见报名费说明。
- **差异：**当前 `data/opportunities.json` 有 2 Contralti 记录，但没有这条 Basso 记录。这是一个已确认的官方公告漏报候选，不代表已通过项目人工发布审核。本日报不修改机会数据，也不自动发布。

## 周度发现工作流故障

2026-11-16 的 Weekly source discovery 第三次尝试（run 43837798178）在提交后执行 rebase 时失败：`grow_sources.py` 会重写合并快照 `data/sources.json`，但工作流的 `git add` 漏掉了该文件，导致工作区仍有未暂存变更。失败日志中恢复出的两条候选经本次核验均为器乐/芭蕾，无声乐价值。修复分支将把 `data/sources.json` 纳入暂存清单，并增加回归测试；本次没有重新触发全量发现任务。

## 风险与后续

1. source-121 仍缺制作方一手公告；截止日为今天，未确认具体时刻，不得公开发布。
2. source-123 截止 2026-11-20，但与个人歌手试唱不等价。
3. Spoleto 2027 页面仍无 bando，80°/81ª 标题冲突未解决。
4. Teatro Massimo Basso 是当前机会库漏报候选，需独立人工核验后才可进入机会数据。
5. 没有来源被删除或停用；没有候选被自动晋升为生产来源；没有机会被自动发布。
