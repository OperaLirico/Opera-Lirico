# OperaLab visual refresh, media and newsletter launch plan

Date: 2026-11-24

## Product outcome

Move OperaLab from a collection of useful sections toward a coherent, public-facing platform for Chinese-speaking classical singers: easy to navigate, visually calm and editorial, reliable on mobile, and useful enough to return to.

The three parallel workstreams are:

1. **Experience and design** — clarify the homepage hierarchy, unify navigation and visual tokens, reduce the current stylesheet override stack only after regression checks, and make mobile navigation/cards easy to scan. Keep the existing forest-green / warm-neutral identity, real data counts, source links, and reduced-motion/accessibility behavior. Do not add invented metrics or decorative stock imagery.
2. **Content media** — add optional, rights-aware image fields to masterclass and opportunity records. Masterclasses use event posters; theatre / conservatory / organizer records can use institution imagery. Images must be HTTPS, carry alt text and source-page metadata, and render only when rights status is `official_provided`, `permission_granted`, or `public_domain`. Unknown or link-only assets remain official source links, not embedded images.
3. **Newsletter and launch** — preserve the existing Buttondown + Cloudflare Worker subscription path and double opt-in. Recheck the live endpoint and subscriber/draft state, preview a current segmented draft in Buttondown, then send manually after editorial review. The scheduled workflow remains draft-only; do not enable unattended sends.

## Current evidence and boundaries

- Homepage has six distinct section entry points; current navigation and panel IDs are wired through `index.html` and `app.js`.
- Masterclasses are loaded from `data/masterclasses.json` and displayed only when official, verified, published, and still current.
- The existing Taste redesign record (2026-11-19) documents unfinished browser finish-gate findings on Home, Masterclasses, and the learning pages. Responsive smoke checks and full visual acceptance are different gates.
- This branch adds optional poster/institution image fields and display support; it does not add or fabricate poster assets. Existing data remains valid and cards without cleared images remain text-first.
- Newsletter verification documented on 2026-11-15: the signup Worker wrote an unactivated Buttondown subscriber with voice metadata, double-opt-in confirmation was returned, and a weekly segmented private draft was created. The scheduled workflow creates drafts only. This evidence must be refreshed before the next live send.
- Live REA browser capture was not available in the current working session. Do not label the visual decisions as REA-verified until the connected REA browser is restored and reference sites are captured with URLs, viewport sizes, and interaction evidence.

## Design research and implementation sequence

1. Reconnect the live REA browser and capture a small, purposeful reference set: a strong editorial cultural homepage, a theatre/opera institution directory, a masterclass/event listing with poster-led cards, and a digital score/library reader.
2. Extract patterns rather than copy screenshots: information hierarchy, card anatomy, typography scale, image ratios, navigation behavior, mobile breakpoints, keyboard focus, and reduced-motion handling.
3. Apply one shared design system to Home, Opportunities, Academy, Masterclasses, Repertoire, and Voice Lab. Preserve each section's distinct content purpose.
4. Run responsive browser checks at 1440, 1024, 768, 390, and 320 CSS px; separately review the Taste finish gate and manual visual behavior.
5. Only after the PR passes and the owner approves, merge and deploy.

## Release gates

- No merge or production deployment from this branch without explicit approval.
- No public image without documented rights status and source.
- No newsletter send before a current Buttondown preview and human approval.
- No claim of REA research, browser QA, or successful deployment unless the corresponding run or capture exists.
