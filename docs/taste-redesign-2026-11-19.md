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


## Browser QA — first measured run (2026-11-19)

The pinned Taste 2.5.1 Chromium gate ran against all five pages at 1440, 1024, 768 and 390 CSS px (with additional 320px checks on touch controls). The first run did **not** pass:

- Home: 47 open gate findings, including 390/320px horizontal overflow, clipped newsletter consent text, a 29px refresh control, misaligned content edges, missing visual weight in several sections, and section/hero composition issues.
- Voice anatomy: 39 open findings, including model-frame focus visibility, low-contrast metadata, sparse sections, and layout/section-height issues.
- Masterclasses: 24 open findings, including hero-fold and section composition issues, card visual balance, and content layout.
- Voice Lab: 38 open findings, including control overlap, low contrast, first-screen navigation, section structure and alignment.
- Larynx mechanism: 65 open findings, including model focus visibility, card/section composition, text contrast, heading scale and hero layout.

The four-width consistency checks completed successfully as a separate check, but the upstream finish gate failed on all five pages. A successful viewport run is not equivalent to a passing design gate.

### Pass 2 changes

- Added a shared narrow-screen baseline for the interior pages: box sizing, overflow containment, flexible grid children, 44px minimum interactive targets, and responsive single-column layouts.
- Added homepage-specific safeguards for 390px and 320px widths, including newsletter wrapping, flexible resource rows and a 44px refresh target.
- These are targeted baseline corrections, not a claim that all Taste findings are resolved. Re-run the browser gate and review remaining page-specific findings before marking the redesign ready.


## Taste composition pass 3 — page-specific art direction

Applied a distinct hierarchy to each page rather than one generic skin:

- Home: section rhythm, content-edge alignment, focus visibility, restrained card variation and reduced-motion handling.
- Masterclasses: editorial programme header and information-led course cards.
- Voice anatomy: larger primary real-model viewport, stronger model/detail hierarchy and clearer breathing-lab grouping.
- Larynx mechanism: specimen/viewer-first layout with a secondary guided interpretation column and structured anatomy sections.
- Voice Lab: instrument-like research workspace with clear map/control/detail hierarchy, keyboard focus and mobile stacking.

No synthetic testimonials, invented programme counts, stock imagery presented as OperaLab evidence, or replacement anatomy illustrations were introduced. Existing interactive models and their source credits remain in place. This pass is design-system CSS only; it must pass the Taste browser finish gate before merge.
