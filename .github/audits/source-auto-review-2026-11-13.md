# 来源自动审核日报 — 2026-11-13

- 审核时间：2026-11-13T11:34:22+01:00（Europe/Rome）
- 本批范围：sources_extra.json 中 9 条尚未完成证据化审核的 legacy 条目（source-100、114、115、117、118、120、121、123、124）
- 页面访问：9/9 当日抓取快照均为 HTTP 200；本次未重复下载页面，使用当日快照并以官方页面/发布方说明作证据交叉核对
- 自动审核分类：auto_approved_official=0；auto_approved_third_party=1；needs_review=1；irrelevant_candidate=7；duplicate_candidate=0；unavailable_temporary=0；retired_candidate=0
- 本次只更新审核元数据；不删除来源、不改变生产抓取启用状态、不发布机会。

## 逐项结论

| source_id | 来源 | 自动结论 | 置信度 | 依据与处置 |
|---|---|---|---|---|
| source-100 | Elfo Puccini — Lavora con noi | irrelevant_candidate | high | 官方页当前只有演员（且注明暂无试镜计划）、场务和票务岗位；无声乐职位。 [官方页面](https://www.elfo.org/chi-siamo/lavora-con-noi.htm) |
| source-114 | CollettivO CineticO | irrelevant_candidate | high | 官方 open call 招聘发行、联合制作与战略发展岗位，不是演唱/舞台声乐岗位。 [官方页面](https://www.collettivocinetico.it/energia-cinetica) |
| source-115 | Fondazione Aida | irrelevant_candidate | high | 官方招聘内容为杂务、音响灯光技术、推广及演员岗位，没有歌手岗位。 [招聘页](https://www.fondazioneaida.it/lavora-con-noi/) · [机构主页](https://www.fondazioneaida.it/) |
| source-117 | AttoriCasting — Napule è | irrelevant_candidate | high | 第三方平台身份可核实，但该条公告只招演员并要求口音/表演，不含歌唱岗位。 [公告](https://www.attoricasting.it/casting-teatro/audizioni-attori-e-attrici-per-la-commedia-brillante-napule-e/91421/) · [平台介绍](https://www.attoricasting.it/chi-siamo/) |
| source-118 | Teatro Franco Parenti | irrelevant_candidate | high | 官方页只接受一般性自荐简历，没有具体岗位或歌唱试镜。 [官方页面](https://teatrofrancoparenti.it/lavora-con-noi/) |
| source-120 | Orchestra della Toscana — Primo Oboe | irrelevant_candidate | high | 官方公告是第一双簧管器乐岗位，非声乐招聘。 [公告](https://www.orchestradellatoscana.it/concorsi-2026-primo-oboe/) · [官方招募目录](https://www.orchestradellatoscana.it/elenco-bandi/) |
| source-121 | Provinispettacolo — Robin Hood | auto_approved_third_party | medium | 第三方平台运营身份明确；公告列有 tenore、soprano、baritono、basso 等声部角色，页面声称报名截止 **2026-11-16**。但尚无制作方一手公告，**仅作为第三方线索保留，不进入公开机会库**。 [第三方公告](https://www.provinispettacolo.it/casting-robin-hood-prima-della-leggenda-piemonte/) · [平台运营/条款说明](https://artisti.provinispettacolo.it/privacy-policy/) |
| source-123 | Torino Fringe Festival — Fringe in Progress 2027 | needs_review | medium | 官方项目接受 under-35 专业个人艺术家/公司、任何表演艺术类型，截止 **2026-11-20**；可能适用于歌剧/声乐项目，但没有声乐特定要求，暂不按歌手试唱机会发布。 [官方项目页](https://www.tofringe.it/partecipa/fringe-in-progress-selezione-per-progetti-in-crescita-torino-fringe-festival-2027/) · [官方参与入口](https://www.tofringe.it/partecipa/) |
| source-124 | Accademia Nazionale di Santa Cecilia — Selezione per Strumentisti | irrelevant_candidate | high | 官方公告只列竖琴、长笛/短笛等器乐岗位，没有声乐职位。 [官方公告](https://santacecilia.it/bandi/selezione-per-strumentisti-2027/) · [官方招募目录](https://santacecilia.it/bandi/) |

## 重要待跟进

1. **source-121 的 Robin Hood 歌唱选角**：第三方公告列出多个声部，截止日期声称为 2026-11-16（距今 3 天）。尚未找到制作方官方公告或可独立确认的制作主体；不得据此公开发布。下一步只寻找制作方/场馆/主办活动的一手页面，不向未核实邮箱发送个人材料。
2. **source-123 的 Fringe in Progress**：截止 2026-11-20，但属于专业艺术项目孵化/工作进展展示，不是单人歌手 audition。可继续观察是否有明确声乐/歌剧项目适配信息。
3. 本批没有可确认的重复、临时不可访问或退役来源；没有删除或停用任何记录。

## 覆盖与限制

- 本批处理 9/9 条剩余 legacy 未完成条目；source-96/97/98/99/101/102 已在 2026-11-12 的证据化报告中处理，不重复计数。
- 44 条合并登记来源的上一份周度覆盖报告为 2026-W46、46/46（另含 2 条候选）；它是可访问性基线，不代表本日重新扫描全部来源。
- 本次使用 2026-11-13 当日抓取结果确认页面 HTTP 200，并用官方页面或平台身份说明核对内容；本批没有重新审查每个域名的 robots.txt/服务条款，也没有进行额外抓取。
- 所有记录的 `production_activation` 保持 false；第三方来源不被标为官方。SHA-256/HTTP 200 均不构成发布方数字签名或机会真实性证明。
