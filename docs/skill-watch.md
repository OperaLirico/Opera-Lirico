# Skill 上游巡检记录

基线建立于 2026-11-19。此后每个周一由定时任务追加一行；只有在检测到上游新提交时才写入。

| 日期 | 仓库 | 新 commit | 变化摘要 | 是否已同步 |
|---|---|---|---|---|
| 2026-11-19 | 基线 | 见 `skill-watch.json` | 六个仓库的当前 HEAD 已记录 | — |

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
