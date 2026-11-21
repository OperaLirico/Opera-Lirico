# OperaLab. 数据质量与自动化交互审计

- 审计日期：2026-11-19
- 范围：公开数据、采集候选、曲库、音乐学院、大师班、来源注册表、GitHub Actions 与 Pages 发布链路
- 基准分支：\`main\`（审计时 HEAD：\`339e3fcc3e71fa81b65746da4fcc69d289b5fd9a\`）
- 原则：只记录已观察到的事实；不把候选视为已核验内容；不因工作流数量多就直接删除历史工作流。

## 1. 数据快照

| 数据域 | 当前记录 | 观察结果 |
|---|---:|---|
| 招募与比赛 | 7 | 最新机会质量审计将7条均标为 published / verified / official，未发现重复标题；2条截止日在7天内，7条在30天内 |
| 大师班 | 11 | 11条均为 published / verified / official；记录最近核验时间集中在11月12–13日 |
| 大师班候选 | 4 | 2条待人工审核、2条已拒绝，均未发布 |
| 音乐学院 | 65 | 57条抓取状态 ok，6条 error，2条 http_error |
| 音乐学院中文摘要 | 65个键 | 文件更新时间为11月10日；状态中有10条待核实、8条读不到、5条已截止、4条未公布 |
| 曲库精选 | 16 | 8条歌剧咏叹调、2条古典咏叹调、6条艺术歌曲 |
| 曲库归档 | 464 | 425条艺术歌曲、31条咏叹调/歌剧选段、8条歌剧选段；23种语言；8条缺少标题、1条缺少作曲家 |
| 曲库自动发现候选 | 65 | 全部来自意大利 Wikisource，全部是整场歌剧文本候选，尚非独立咏叹调 |
| 来源候选 | 2 | 两条仍处于人工审核队列 |

精确数据来源：主分支 \`data/*.json\`；招募与比赛另有 \`.github/audits/opportunity-quality-latest.md\`。归档与候选记录数量不是“已核验曲目数”。

## 2. 需要优先处理的数据问题

### P0 — LiederNet 曲库文本的版权状态没有逐条记录

- 464条归档中，456条的文本来源标记为 **LiederNet 原文**，8条为 Wikisource。
- 464条归档记录均没有 \`licenseNote\` 或等效的逐条权利状态字段。
- 当前页面将归档文本纳入本地搜索和阅读；因此不能仅凭原文页面可访问，就推定所有文本都可以复制并公开再分发。
- LiederNet 官方版权说明称其数据库及网页集合受版权保护；许多文本在加拿大和美国属于公有领域，但版权文本未经许可不得复制。其服务条款也要求访客遵守所在地版权法，并禁止未经明确书面许可再分发受版权保护内容。
- 已抽查到明确风险案例：\`TextId=295391\` 的作品由 Shelton L. Becton 创作，页面标示为1999年发表；\`TextId=72070\` 页面明确提示部分内容不属于公有领域，并标明 David Paley 的德语译文版权年份。当前归档包含相应文本。

官方来源：
- LiederNet Copyright Notice：https://www.lieder.net/lieder/copyright.html
- LiederNet Terms of Service：https://www.lieder.net/lieder/register.html
- LiederNet TextId 295391：https://www.lieder.net/lieder/get_text.html?TextId=295391
- LiederNet TextId 72070：https://www.lieder.net/lieder/get_text.html?TextId=72070
- LiederNet Introduction：https://www.lieder.net/lieder/intro.html

**建议：** 保留作品名称、作曲家、语言、来源链接等可用于发现的元数据；对没有逐条公有领域证据或许可证明的全文，先不要继续公开复制。后续建立 \`rights_status\`、\`rights_evidence\`、\`rights_checked_at\` 字段，并逐条审核。由于这会改变曲库的全文阅读和歌词搜索能力，本审计不直接删除或改写现有歌词数据，需先确认处理策略。

### P1 — 归档中有8条缺少作品标题

8条记录的 \`title\` 为空；部分来源页有可恢复的文本标题或具体声乐作品名。搜索时这些记录可能无法通过作品名称命中。另有1条缺少作曲家。

**建议：** 以来源页为依据回填标题，并区分诗歌标题、作曲家为该文本创作的歌曲标题，以及套曲/作品集出处；不能简单把首句一律当作正式曲名。

### P1 — 大师班已结束项目的过滤条件曾有缺口

- 当前11条已发布大师班中，有一条开始日期为2026-11-16。
- 页面原过滤逻辑只检查 \`end_at\` 和申请截止日期；当 \`end_at\` 缺失时，已经过去的 \`start_at\` 仍可能被显示。
- 已在 Taste 页面改版 PR #129 中修复：优先用 \`end_at\`，没有 \`end_at\` 时回退到 \`start_at\` 判断是否已结束；申请截止日期仍单独检查。

### P1 — 音乐学院抓取失败和中文摘要更新不同步

- 65条院校记录中，8条抓取状态不是成功（6 error、2 http_error）。
- 65个中文摘要键的更新时间为11月10日，比11月19日的院校抓取快照旧9天。
- 摘要状态里有10条待核实、8条读不到、5条已截止、4条未公布。

**建议：** 不要将抓取失败记录误标为“无招生”；保留最后成功抓取时间、错误原因和官方页面链接；中文摘要只在原始页面有实质变化时更新，并明确标注“待核实/读不到/已截止”。

### P2 — 数据文件的顶层更新时间可能与逐条核验时间不一致

- \`data/opportunities.json\` 顶层更新时间为11月12日；但11月19日的质量报告已对7条记录做了质量检查。
- \`data/masterclasses.json\` 顶层更新时间为11月13日；发布记录最近核验时间为11月12–13日。
- \`data/repertoire_archive.json\` 和精选曲库生成时间为11月10日；候选文件则更新至11月19日。

**建议：** 区分 \`generated_at\`、\`last_source_scan_at\`、单条记录 \`checked_at\`，避免把“文件重新生成”误当作“所有来源重新核验”。

## 3. 来源发现现状

- 11月16日的来源覆盖报告记录了44条注册来源和2条候选来源。
- 报告中有13条来源需要复核、分类或排除。
- \`data/sources_extra.json\` 在11月19日有更新；\`data/source_candidates.json\` 的顶层更新时间仍为11月12日。

**建议：** 先处理来源质量和分类，再增加来源数量。每个来源应保留官方/第三方属性、适用数据类型、访问策略、最近成功时间、失败原因和人工复核状态。

## 4. 自动化交互与重复发布风险

- 仓库共有63个 GitHub Actions workflow 文件。
- 其中29个文件名属于 anatomy / larynx / voice-lab / quiz 相关实验或页面工作流；另有6个 cycle 日志工作流。
- \`self-heal.yml\` 每30分钟运行一次，最多对安全名单中的失败工作流自动重跑两次，每轮最多重跑4个任务。这是有上限的，但必须纳入工作流依赖图，避免将真正的代码/数据错误当作瞬时网络故障反复重跑。
- \`daily-scrape-and-publish.yml\` 自己有 Pages 发布 job；当它提交 \`data/conservatori.json\` 时，\`pages-deploy.yml\` 的 push 路径也会触发另一条 Pages 发布。两者使用相同 concurrency group，能串行化，但不会自动去重。
- 每日采集中的曲库候选收集 job 与 deploy job 在 build 之后并行运行；候选文件可能在 build 生成 Pages artifact 之后才提交。原 \`pages-deploy.yml\` 也没有监听 \`data/repertoire_candidates.json\` 和 \`data/repertoire_archive.json\`，可能造成候选/归档更新未及时进入线上页面。
- 这个部署文件遗漏还包括 \`voice-lab.html\`、\`data/voice-structures.json\`、院校中文补充数据，以及新 Taste CSS/JS 资源。

**已在 PR #129 做的低风险修复：** 扩展现有 Pages workflow 的 path filter，加入曲库归档/候选、院校补充数据、voice-lab、voice structures 和 Taste 资源。没有新增 workflow，也没有改变事件类型、权限或定时策略；只扩展了现有 path filters。

**后续建议：** 先画出每个 workflow 的触发条件、读写文件、提交行为、部署行为和依赖关系；再决定是否合并重复部署。不要直接删除29个 anatomy 相关工作流或6个历史 cycle 日志。

## 5. 当前 PR 与验证状态

| PR | 内容 | 状态 |
|---|---|---|
| #127 | REA 上游 Skill v63 同步 | 待审核，未合并 |
| #128 | KV 备份文件生命周期、上传重试、下载解密验证；固定6个旧 workflow 的 checkout SHA | Source quality tests 通过；实际 workflow_dispatch 备份/恢复运行仍待验证 |
| #129 | Taste 页面重设计、大师班过期过滤、Pages 路径覆盖修复 | Source quality tests 与 website-copy/syntax check 通过；真实浏览器截图与四种视口验收未完成 |

## 6. 推荐执行顺序

1. 完成 PR #128 的审查；合并后执行一次手动 KV 备份，并确认 artifact 下载、解密和 key count 校验成功。
2. 完成 PR #129 的测试和真实浏览器验收；不以静态 CI 代替视觉验收。
3. 决定曲库版权处理策略：保留标题/作曲家/来源链接，还是对无逐条许可证据的全文先做下架/隔离。
4. 修复8条无标题归档记录，并为正式曲目增加逐条来源与权利证据。
5. 刷新大师班和音乐学院来源状态；将抓取失败、过期和未公布明确区分。
6. 绘制63个工作流依赖图，再制定去重方案；在完成映射前不删除历史工作流。

本报告是审计记录，不代表所有问题已修复。

## 5. Workflow responsibility map (reviewed 2026-11-19)

### Observed execution graph

```text
Daily source refresh (06:15 UTC / workflow_dispatch / selected push paths)
  └─ build
      ├─ unit tests
      ├─ scrape_sources.py
      ├─ grow_sources.py
      ├─ run_conservatori.py
      ├─ mirror_pdfs.py + PDF integrity audit
      ├─ opportunity quality audit
      ├─ commit source snapshots to main (when changed)
      └─ upload Pages artifact from this checkout
           ├─ repertoire-collection (needs build; commits candidate queue to main)
           └─ deploy (needs build; deploys artifact created before candidate collection)

Push to main (pages-deploy path filter)
  └─ independent Pages deploy workflow

Weekly source discovery (Monday 06:30 UTC)
  ├─ grow_conservatori.py
  ├─ grow_sources.py --discover
  └─ commits source registry and candidate outputs to main

System health check (daily 09:00 UTC)
  └─ tests + read-only endpoint/data validation

Self-heal (every 30 minutes)
  └─ scans failed scheduled runs in a six-hour window
     └─ retries an allowlist, max two retries / max four reruns per sweep
```

### Confirmed design risks

1. **Two owners of Pages deployment.** Daily source refresh uploads and deploys a Pages artifact itself, while the separate Pages workflow also deploys after qualifying pushes. This creates two deployment paths and makes it harder to reason about which commit is live.
2. **Artifact is created too early.** The Pages artifact is uploaded in `build`; `repertoire-collection` runs after `build` and can commit `data/repertoire_candidates.json`, while `deploy` also depends only on `build`. The daily deployment can therefore publish an artifact that predates the candidate commit.
3. **The collection job is allowed to run after a failed build.** Its `if: always() && (needs.build.result == 'success' || needs.build.result == 'failure')` is explicit behavior. It may be useful for candidate collection resilience, but the deploy graph must not assume it has completed.
4. **Self-heal retries workflow-level failures by name.** The allowlist and retry caps are sensible guardrails, but a deterministic test/data failure can be retried like a transient network issue. Reports should distinguish failure classes before adding more workflows to the allowlist.
5. **Source discovery and daily refresh both write source registries.** They are separate schedules and use different concurrency groups. Both rebase/push to main, so they can race at the Git level even though they fetch/rebase before pushing.

### Recommended target architecture (not yet applied)

- Make `pages-deploy.yml` the **only** workflow that creates and deploys the Pages artifact.
- Remove the Pages artifact upload and deploy job from `daily-scrape-and-publish.yml`; keep that workflow responsible for source refresh and data commits only.
- Expand the Pages path filter to include every public runtime dependency, including `data/repertoire_candidates.json`, `data/repertoire_archive.json`, `voice-lab.html`, `data/voice-structures.json`, `data/conservatori_manual.json`, `data/conservatori_zh.json`, `taste-home.css`, `taste-interior.css`, `taste-home.js`, and `assets/moments/**`.
- Keep the daily collector as a separate job, but ensure a candidate commit naturally triggers the single Pages workflow through the path filter.
- Give source-registry writers one shared concurrency group (or serialize them behind one reusable refresh workflow) before adding more writers.
- Keep self-heal limited to transient/infrastructure failures; do not automatically retry deterministic validation failures without classification.

### Change boundary

This is an evidence-based recommendation only. No workflow has been deleted, merged, or retargeted in this audit PR. Apply the deployment ownership change in a separate implementation PR with a workflow test that asserts one Pages deploy per source refresh and confirms the deployed artifact contains the latest candidate file.
