# Daily source audit — 2026-11-16

- 本日复核 **8 条**来源/候选：auto_approved_official=1（既有候选复核）、auto_approved_third_party=2、needs_review=3、irrelevant_candidate=2。
- **无新增生产来源**；无删除、停用或生产抓取方式变更。
- 周度覆盖 2026-W47：**46/46** 完成，0 失败/受限/抽取错误；15 条正文哈希变化。
- 重要内容漏报：Teatro Massimo 官方页面出现 **1 个 Basso 合唱团岗位**，截止 2026-12-04 12:00、试唱 2026-12-19 10:00；当前 `data/opportunities.json` 未收录。本次只记录为待人工核验候选，未自动发布。
- 周度发现工作流 run 43837798178 因 `data/sources.json` 未加入 git add 而在 rebase 时失败；修复分支已补齐暂存路径并增加回归测试。

详细证据与逐项处置见 [source-auto-review-2026-11-16.md](source-auto-review-2026-11-16.md)。
