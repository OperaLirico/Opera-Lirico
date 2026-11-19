# OperaLab. — Taste Skill redesign plan

- Date: 2026-11-19
- Skill: \`design-taste-frontend\` 2.5.1
- Upstream: \`Leonxlnx/taste-skill\`, pinned commit \`f6b76575f949707b4e3c37cd86cb44b0b98643e8\` (MIT)
- Page kind: software / software
- Product: a Chinese-language European classical-vocal opportunity and learning information platform
- Audience: Chinese vocal students and singers considering study or professional development in Europe
- Primary action: view open auditions and competitions
- Brand constraints: retain OperaLab forest-green identity; use neutral surfaces and one green accent; no violet, no invented statistics, no stock imagery.

## Design decisions

1. The homepage hero is a full-screen split: concise category-first copy and a live HTML navigation panel that links to real sections. It is not a generic dashboard or a static fake screenshot.
2. The first-screen proof is the existing live count of currently open audition/competition records; it is sourced from the existing application renderer.
3. Opportunity cards and the learning-resource list keep existing application IDs and \`data-open\` actions. Data loading, search, filtering and newsletter behavior remain in existing scripts.
4. The information-review section uses one restrained word-highlight moment. The statement remains fully readable without JavaScript and under reduced motion.
5. Interior learning pages keep their existing real 3D anatomy embeds, source credits, SVG learning interactions and page scripts. This change adjusts presentation only; it does not replace anatomical assets or alter scientific claims.
6. The masterclass page keeps its official-record filter and source links, and now also hides past events when no explicit end date is recorded by falling back to the start date.

## Motion and accessibility

- One-time hero entrance; no scroll reveal or parallax.
- Card hover lift is 2px; controls retain keyboard focus states.
- The word-highlight moment reverses as the reader scrolls upward and becomes static under reduced motion.
- Existing \`aria-live\`, form controls, IDs and action handlers are preserved.
- Responsive targets: 1440, 1024, 768 and 390 CSS pixels.

## Validation status

- Source/markup preservation checks: passed during branch construction for the principal panel IDs and anatomy interaction targets.
- Pages deployment path filters now include the new Taste assets, repertoire archive/candidates, conservatory supplements, voice structures and the voice-lab page; triggers were not broadened beyond relevant public files.
- JavaScript syntax, source-quality tests and website-copy checks: passed on PR #129.
- Taste Skill's upstream browser gate and visual screenshots at all four widths: pending. The repository contains the Chinese method card but not the full upstream checker/assets. Do not describe the redesign as visually verified until those checks have run.
- The masterclass expiry filter and Pages path changes are covered by passing PR CI, but the live page has not yet been browser-verified.
