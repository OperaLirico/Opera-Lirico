# Anatomy learning-loop v1

Date: 2026-11-20
Scope: `larynx-mechanism.html`

## What changed

- Added a persistent local-plate fallback below the third-party Sketchfab viewer. The UBC and Dundee models remain the primary anatomical references; the fallback explicitly labels the two local illustrations as teaching line drawings, not specimen-grade 3D models.
- Added a searchable Chinese/English/abbreviation glossary for ten core laryngeal structures and muscle groups.
- Added a three-question, client-side knowledge check covering PCA abduction, interarytenoid posterior closure, and CT-related vocal-fold length/tension.
- Kept the existing mechanism controls and static-model disclaimer. No fabricated joint animation, force values, tissue deformation, or vocal-fold vibration simulation was introduced.
- No new runtime dependency, backend, analytics collection, or paid service.

## Existing foundation retained

- UBC Medicine / HIVE human larynx specimen model, embedded from its original Sketchfab page.
- University of Dundee laryngeal muscles/cartilages/ligaments model, embedded from its original Sketchfab page.
- Locally stored superior-view and intrinsic-muscle teaching plates.
- Existing five mechanism descriptions (PCA, LCA, IA, TA, CT), evidence links, and provenance notes.

## Validation

The repository's existing `.github/workflows/check-site-copy.yml` runs on pull requests that change `larynx-mechanism.html`. Its page validation checks required model and mechanism controls and runs `node --check` against every inline script on both anatomy pages. The result must be reviewed before merge.

## Known limitations / next phase

- The third-party iframe cannot be reliably inspected for internal load failure because it is cross-origin. The fallback is therefore always available as a clearly labelled alternative rather than a false automatic error detector.
- The local line drawings are orientation and structure-recognition aids, not a substitute for the institutional 3D models.
- The muscle line drawing does not yet have clickable region overlays. Add these only after each region boundary is manually reviewed against the source anatomy; guessed polygons would create false precision.
- A true moving laryngeal model requires a separately sourced, licensed, and anatomically reviewed rig with documented attachment points and motion axes. Do not animate the existing static meshes as if their movement were validated.
- Next sensible scope: review a real human vocal-fold vibration/phonation dataset or licensed animation, then add a separate labelled physiology layer without conflating it with static anatomical truth.
