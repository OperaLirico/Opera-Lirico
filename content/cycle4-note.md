
## 第 4 轮 · 2026-11-18 · VocalGateway 来源 / 代码 / 素材审计

（延伸第 3 轮，全文见 `docs/vocal-gateway-source-audit.md`）

**信息来源三层**：主办方官方页面（每条机会一个 `officialUrl`，公开页出现约 30 个主办域名）→ 机构文件与政府口径（operaballet.nl 年报 PDF、ind.nl 移民局、netherlandsworldwide.nl）→ 辅助与存证（web.archive.org、casting42、bedandmarket、turkishairlines）。

**最值得学的一条**：证据不是链接而是记录——`id / officialUrl / cycleId / locator / excerpt / language / fetchedAt / reviewedAt / reviewerId / version` 十字段。

**代码格式**：opportunity→cycle→evidenceRefs 三层分离；字段级 `evidenceState` + `evidenceIds`；费用 `minorUnits` 整数 + `condition:"not_stated"`；截止 `localDate+localTime+ianaTimezone+utcInstant+precision:"date_only"`；评分带 `policyVersion`（`frozen-shared-scoring.v112d0` / `opportunity-career-tier.v10.5`）；`listingState`/`applicationState`/`evidenceState` 三态分离。CSS 只有 21 个令牌却有 442 个硬编码色（漂移）；无 `@font-face`，全站系统衬线栈；JSON-LD 仅 WebSite + BreadcrumbList，无 Event/JobPosting；hreflang 存在但渲染为 `hrefLang`。

**素材**：几乎零素材——1500×1500 logo PNG（345KB，全站共用作 OG）、384 宽 WebP 深底 logo（46KB）、180 apple-touch（22KB）、13 张报告页 WebP（98–185KB/张）。无摄影、无插画、无人物图、无 webfont。

**可借**：十字段证据、字段级状态、`not_stated` 枚举、口径版本化、三态分离、材料归一化、零字体请求的系统衬线栈。
**不借**：442 色漂移、方形共享 OG 图、图片式报告、无 CDN 且 `no-store`、粒度过细而装配失灵的 `costs.evidenceIds`（公开 payload 里退化为 React 路径字符串）。

**落地三件事**：① `research/evidence.json` 从 4 字段扩到带 `locator/excerpt/fetchedAt/reviewedAt`；② `voice-structures.json` 关键字段各自带 `evidenceState + last_checked`；③ 大师班页用 `materials` 归一化 + 准备复杂度。
