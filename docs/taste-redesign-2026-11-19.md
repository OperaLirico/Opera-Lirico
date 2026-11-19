# OperaLab. — Taste Skill redesign plan

- Date: 2026-11-19
- Skill: \`design-taste-frontend\` 2.5.1
- Upstream: \`Leonxlnx/taste-skill\`, pinned commit \`f6b76575f949707b4e3c37cd86cb44b0b98643e8\` (MIT)
- Page kind: software / software
- Product: a Chinese-language European classical-vocal opportunity and learning information platform
- Audience: Chinese vocal students and singers considering study or professional development in Europe
- Primary action: view current open vocal opportunities
- Brand constraints: retain OperaLab forest-green identity; use neutral surfaces and one green accent; no violet, no invented statistics, no stock imagery.

## Design decisions

1. The homepage hero is a full-screen split: concise category-first copy and a live HTML navigation panel that links to real sections. It is not a generic dashboard or a static fake screenshot.
2. The first-screen proof is the existing live count of currently open vocal opportunities; it is sourced from the existing application renderer and is not a hard-coded marketing metric.
3. Opportunity cards and the learning-resource list keep existing application IDs and \`data-open\` actions. Data loading, search, filtering and newsletter behavior remain in existing scripts.
4. Each of the five redesigned pages uses one restrained, text-led word-highlight moment from the pinned Taste runtime. Statements remain readable without JavaScript and under reduced motion.
5. Interior learning pages keep their existing real 3D anatomy embeds, source credits, SVG learning interactions and page scripts. Hero copy, model navigation and source sections are reorganized without replacing anatomical assets or altering scientific claims. The Voice Lab also gains a visible search label, semantic main landmark and larger touch targets.
6. The masterclass page keeps its official-record filter and source links, hides past events when no explicit end date is recorded by falling back to the start date, and removes street numbers/postcodes from public display while preserving the raw source record.

## Motion and accessibility

- One-time hero entrance on all five redesigned pages; no generic scroll reveal or parallax.
- Card hover lift is 2px; controls retain keyboard focus states.
- The word-highlight moment reverses as the reader scrolls upward and becomes static under reduced motion.
- Existing \`aria-live\`, form controls, IDs and action handlers are preserved.
- Responsive targets: 1440, 1024, 768, 390 and 320 CSS pixels.

## Validation status

- Source/markup preservation checks: passed during branch construction for the principal panel IDs and anatomy interaction targets.
- Pages deployment path filters now include the Taste moment runtime, repertoire archive/candidates, conservatory supplements, voice structures and the voice-lab page; event types, schedules and permissions are unchanged.
- JavaScript syntax and source-quality tests: passed on the latest checked branch snapshot. Website-copy check and full Taste browser gate are still running for the newest UI changes.
- CI fetches the full Taste checker from the pinned upstream commit using the repository sync script; the full checker is not copied wholesale into the project. Five-page browser checks at the required widths are in progress. Do not describe the redesign as visually verified until they pass.
- The masterclass expiry filter and Pages path changes are covered by source-quality tests. Live production deployment and manual browser review remain pending.
