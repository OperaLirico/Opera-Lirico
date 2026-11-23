# Skill 上游巡检记录

基线建立于 2026-11-19。此后每个周一由定时任务追加一行；只有在检测到上游新提交时才写入。

| 日期 | 仓库 | 新 commit | 变化摘要 | 是否已同步 |
|---|---|---|---|---|
| 2026-11-19 | 基线 | 见 `skill-watch.json` | 六个仓库的当前 HEAD 已记录 | — |
| 2026-11-23 | `Leonxlnx/taste-skill` | `6c0b5c78` | 仅 README 增一行赞助者头像，SKILL.md 与 scripts 未变 | 不需要，保持现有 vendored 版本 |
| 2026-11-23 | `JuliusBrussee/caveman` | `b89752f6` | 245 个文件：engine/proxy/packages 与 caveman-compress 的 SKILL.md、compress.py、validate.py，压缩行为有实质改动 | 未同步（本仓库未引入该技能） |
| 2026-11-23 | `vercel-labs/agent-skills` | `5a37a632` | 只改 `skills/web-design-guidelines`：1.0.0→1.1.0，规则改为内置快照（附 SHA-256）；我们采用的三个技能未动 | 不需要 |

本周结论：6 个仓库里 3 个有新提交，均不需要同步，未发现 LICENSE 变更。

## 巡检范围

1. `Leonxlnx/taste-skill`（MIT，网页设计技能，已入库到 `skills/taste-skill/`）
2. `JuliusBrussee/caveman`（Apache-2.0，token 压缩，装法为本地代理）
3. `greensock/gsap-skills`（MIT，官方动效技能）
4. `hypit-ai/hypit`（NOASSERTION，爆款视频复刻）
5. `openai/skills`（playwright 等 curated 技能，仓库已标 deprecated）
6. `vercel-labs/agent-skills`（`npx skills` CLI，上面的安装命令依赖它）

## 判断口径

- 只改 README / 文档：记录，不必同步。
- 改了 `SKILL.md`：看是否影响我们已引用的方法（提示词触发、检查清单、门槛）。
- 改了 `scripts/` 或 `references/`：影响执行结果，需重跑 `sync.sh` 或重新安装。
- 改了 `LICENSE`：必须重新审阅，尤其 `hypit-ai/hypit` 这类非标准许可。
