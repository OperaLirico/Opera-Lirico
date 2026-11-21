# 开源技能整合（2026-11-21）

## 已收进仓库

| 目录 | 上游 | 许可证 | 固定提交 | 收的是什么 |
|---|---|---|---|---|
| `skills/impeccable` | pbakaus/impeccable 4.10.0 | Apache-2.0 | b49177d | 评审层：critique / audit / polish / bolder |
| `skills/scrapling` | Cedriccmh/claude-code-skill-scrapling | MIT | 85dd89f | 抓取决策树、CLI quick path、站点经验沉淀 |
| `skills/marketingskills` | coreyhaines31/marketingskills | MIT | 5b2b400 | seo-audit / schema / cro / emails（从 50+ 里挑） |
| `skills/web-quality` | addyosmani/agent-skills | MIT | 8c99fa3 | 可达性 / 性能 / DevTools 检查（从 26 里挑） |

每个目录三件：`README.md`（是什么、边界、许可义务）、`METHOD.md`（中文方法卡，读完就能用）、`sync.sh`（按固定提交拉 `upstream/`，不提交）。

## 只登记巡检、不落盘的

`blader/humanizer`（去 AI 腔）、`cloudflare/security-audit-skill`（Worker 与表单体检）、`tt-a1i/archify`（管线出图）。理由：低频、或只在一个具体任务里用一次，落盘只增维护量。

## 这几件事为什么值得做

1. **评审口径**：taste 只给 FAIL 数和闸门，逼着为过闸改结构。impeccable 先把页面归到 Persuade / Operate / Read，再按那套标准评——首页是 Operate，不该拿落地页教条打分。这是对「别为了通过而通过」的机制性回答。
2. **抓取稳定**：Scrapling 的 Fetcher 分级 + 自适应重定位，正对剧院站改版后选择器失效的老问题。守卫条款（不绕付费墙、robots 先行、cookie 不入库）和我们既有边界一致。
3. **能被搜到**：`seo-audit` 的优先级顺序指出真的短板——机会只在首页卡片上，没有独立 URL，页面层优化无从谈起。`schema` 的 `Event` 标记对截止日期驱动的条目最值钱。
4. **检查可编程**：`browser-testing-with-devtools` 替掉「截图看一眼」，taste 那轮两类错误（`@media` 整块失效、来源行被切掉）都能当场抓到。

## 没做的事

- 没改线上任何页面、样式、脚本。
- 没把上游 `upstream/` 提交进仓库（体积与维护成本都不划算）。
- 没动站点文案。`clarify` / `cro` 会提文案建议，只列问题，不代替撰写。

## 下一步（按顺序）

1. `sync.sh` 拉一次 impeccable，跑 `critique` 与 `audit` 审首页，把结论和 taste 那 36 条 FAIL 并排对照。
2. 用 `schema` 给开放招募区加 `Event` JSON-LD；先用 headless 渲染核验标记真的出现在 DOM 里。
3. 修 `.github/workflows/pages-deploy.yml` 的路径白名单（`hero-calls.*`、`theme-wine.css`、`taste-fix.css` 缺失导致纯样式提交不触发构建）。
