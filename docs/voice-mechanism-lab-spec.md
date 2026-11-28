# Voice Mechanism Lab — anatomical truth contract

Status: research/design specification; not yet an implemented or validated simulation.

## Product goal

Build the first interactive mechanism study inside `voice-anatomy.html`: **how the arytenoid cartilages and intrinsic laryngeal muscles alter true vocal-fold position**. This is a focused first figure, not a full-body 3D anatomy atlas.

The module must teach the real anatomy and distinguish:
1. the anatomical reference (real sourced model / atlas geometry),
2. the explanatory mechanism figure (Anatomy skill output), and
3. the physiological interpretation (evidence-based text and state logic).

Never let the explanatory figure replace or distort the anatomical reference.

## Non-negotiable truth rules

- No freehand human anatomy presented as anatomically accurate.
- Do not infer muscle origins, insertions, cartilage contours, joint axes, dimensions, or tissue thickness from visual guesswork.
- Every depicted anatomical structure must be traceable to a named source or licensed anatomical model.
- Label a view as superior, posterior, lateral, or sagittal. Do not silently mix orientations.
- Distinguish the true vocal folds from the vestibular folds.
- Distinguish the arytenoid vocal process (vocal ligament attachment) from the muscular process (intrinsic muscle attachment).
- A muscle activation control is an explanatory state, not a clinical measurement of muscle force or EMG.
- Do not show an exact vocal-fold vibration waveform, frequency, amplitude, or tissue deformation unless a validated model and measured parameters are available.
- If a mechanism is simplified, visibly label it “机制示意 / not to scale”; never call it a biomechanical simulation.
- Preserve source credits, model licence, and links to the original asset.

## First figure size and Anatomy skill role

**Size: Figure (one mechanism, 40–80 purposeful parts).**

The Anatomy skill is suitable for a crafted interactive *mechanism explainer* (an instrument-like cutaway with controls, linkages, and a live readout). It is **not** an anatomy atlas generator: its own documentation says it draws machines/instruments rather than people or exact maps, and its 3D turning mode is beta.

Therefore:
- Use verified anatomical references / a licensed anatomical mesh for cartilage, vocal folds, and muscle locations.
- Use Anatomy for the explanatory apparatus, linkage/force-vector presentation, precise labels, and state-driven readout—not to invent cartilage or muscle morphology.
- Keep the Anatomy figure and real anatomical model visually adjacent and clearly labelled as different kinds of representation.
- Do not use the skill's beta 3D renderer for production-critical biological tissue deformation. First prototype a single rigid-body movement (arytenoid rotation) and validate it against the reference anatomy.

## Anatomical scope of the first figure

### Structures

- Cricoid cartilage and cricoarytenoid articular region.
- Right and left arytenoid cartilages.
- Vocal processes and muscular processes (separately identified).
- True vocal folds / vocal ligaments extending anteriorly from the vocal processes.
- Thyroid cartilage anterior attachment landmark.
- Lateral cricoarytenoid (LCA).
- Posterior cricoarytenoid (PCA).
- Interarytenoid muscle (transverse component; identify oblique component only if a source model supports it).
- Thyroarytenoid (TA), with vocalis noted as its medial component/region where the chosen reference supports that distinction.
- Cricothyroid (CT) as a separate lengthening/tension mechanism in a later panel, not conflated with arytenoid rotation.

### Verified functional relationships for the first release

- PCA is the sole intrinsic laryngeal muscle responsible for vocal-fold abduction; it rotates the arytenoid laterally.
- LCA adducts the vocal folds through medial rotation of the arytenoid.
- Interarytenoid activity brings the arytenoids together and contributes to posterior glottic closure.
- TA adducts/approximates the fold and changes vocal-fold tension/stiffness; do not reduce it to a universal “relaxer”.
- CT lengthens and tenses the vocal folds; pitch is not a one-muscle control and must not be represented as a direct linear slider.
- Arytenoid movement occurs at the cricoarytenoid articulation and includes rotation and gliding; avoid drawing a simple door hinge unless explicitly labelled as a simplified projection.

### Vocal-fold tissue layers (second detail view)

Use the commonly described five-layer arrangement, deep to superficial:
1. thyroarytenoid muscle,
2. deep lamina propria,
3. intermediate lamina propria,
4. superficial lamina propria,
5. epithelium.

The deep and intermediate lamina propria contribute to the vocal ligament. The superficial lamina propria is the compliant superficial layer important to mucosal-wave behaviour. Do not animate these layers as independent strings or imply that a simple slider captures their viscoelastic behaviour.

## Anatomy figure parts list (target: 40–80)

The skill's part list is a visual-design checklist, not a claim that these are 40–80 anatomical structures.

### Instrument / frame (12)
1. base plate
2. four feet
3. left frame upright
4. right frame upright
5. upper crossbar
6. lower crossbar
7. rear mounting plate
8. left bearing seat
9. right bearing seat
10. front reference rail
11. engraved view-orientation plate
12. scale / legend strip

### Anatomical reference mounts (10)
13. cricoid reference cradle
14. left arytenoid reference mount
15. right arytenoid reference mount
16. left articular-axis marker
17. right articular-axis marker
18. left vocal-process pointer
19. right vocal-process pointer
20. left muscular-process pointer
21. right muscular-process pointer
22. anterior vocal-ligament anchor marker

### Mechanism and force display (16)
23. left LCA force-link (schematic)
24. right LCA force-link (schematic)
25. left PCA force-link (schematic)
26. right PCA force-link (schematic)
27. transverse interarytenoid bridge (schematic)
28. left TA force-link (schematic)
29. right TA force-link (schematic)
30. left arytenoid rotation indicator
31. right arytenoid rotation indicator
32. left arytenoid glide indicator
33. right arytenoid glide indicator
34. left vocal-fold position indicator
35. right vocal-fold position indicator
36. posterior glottic-gap indicator
37. anterior glottic-gap indicator
38. airflow direction indicator

### Controls and readout (12)
39. PCA / abduction control
40. LCA / adduction control
41. interarytenoid / posterior closure control
42. TA / fold body control
43. neutral reference control
44. reset control
45. state title plate
46. live action readout
47. “not to scale” marker
48. view-orientation label
49. evidence / source plate
50. simplification / uncertainty note

Parts 23–29 are explicitly explanatory force links, not anatomical muscle models. Their geometry must not be mistaken for muscle belly shape or fiber architecture.

## Interaction states

The first version should use named, discrete states rather than an unvalidated continuous force slider:

- **Neutral reference:** source model at its documented neutral/resting pose.
- **Abduction (PCA):** show lateral rotation of the arytenoids and widening of the glottic opening. The explanatory link indicates PCA action; it does not claim measured force.
- **Adduction (LCA):** show medial rotation and approximation of the vocal folds.
- **Posterior closure (interarytenoid):** show approximation of the arytenoid bodies / posterior glottic region. Do not imply that this alone determines complete membranous-fold closure.
- **Combined phonatory approximation:** show coordinated adductor state, with a note that real phonation uses graded co-activation and fine neuromuscular control.
- **Reset:** return to the sourced reference pose.

Every state must include: what moves, which anatomical structure is responsible, the direction of movement, what the diagram simplifies, and a source link.

## Later figure: vocal-fold layers and tension

Do not merge this into the first mechanism. It is a separate follow-on figure:
- sourced cross-sectional tissue model;
- five layers labelled from deep to superficial;
- TA/vocalis and CT effects described separately;
- no simulated mucosal wave until a validated continuum / fluid-structure interaction model is available;
- any illustrative wave animation must be explicitly marked conceptual and must not be used to infer a singer's vocal health or technique.

## Sources to use and cross-check

1. NCBI Bookshelf — Anatomy, Head and Neck: Laryngeal Muscles:
   https://www.ncbi.nlm.nih.gov/books/NBK545265/
   Muscle actions, origins/insertions, and innervation.
2. NCBI Bookshelf — Anatomy, Head and Neck: Larynx:
   https://www.ncbi.nlm.nih.gov/books/NBK538202/
   Laryngeal regions and true/vestibular fold anatomy.
3. NCBI Bookshelf — Anatomy, Head and Neck: Larynx Vocal Cords:
   https://www.ncbi.nlm.nih.gov/books/NBK535342/
   Vocal-fold tissue layers.
4. NCBI Bookshelf — Anatomy, Head and Neck: Arytenoid Cartilage:
   https://www.ncbi.nlm.nih.gov/sites/books/NBK513252/
   Arytenoid processes, cricoarytenoid joint movement, and muscle attachments.
5. Anatomy skill, pinned in this repository at `.agents/skills/anatomy`:
   https://github.com/wheresryan22/anatomy
   MIT-licensed explanatory-figure toolkit; 3D turning mode is beta and is not a biological simulation.

## Acceptance checklist

- [ ] The anatomical reference model has a named author/institution, source URL, licence, and view orientation.
- [ ] Each muscle attachment and action shown is supported by a source.
- [ ] Left/right orientation is consistent across model, labels, and controls.
- [ ] Vocal process and muscular process are not confused.
- [ ] PCA abduction and LCA adduction are shown in opposing, anatomically consistent directions.
- [ ] Interarytenoid action is shown at the posterior arytenoid region, not as a membranous-fold actuator.
- [ ] No unsupported dimensions, force values, muscle activation percentages, pitch values, or vibration frequencies are displayed.
- [ ] The figure is labelled as a mechanism schematic and not a clinical or validated biomechanical simulation.
- [ ] Anatomy skill build, geometry audit, line check, desktop capture, mobile capture, and reduced-motion check all pass in an environment that can execute the skill.
- [ ] The actual deployed page is visually checked before calling the work complete.

## Implementation note

The Anatomy skill requires a working coding-agent environment with the submodule initialized, Node.js 20.10+, and Chrome/Chromium for its build and verification scripts. GitHub file-editing operations alone cannot execute the skill or its geometry/browser audits. Do not claim the skill was run until those commands have actually completed and their output has been reviewed.


## Critical visual-fidelity requirement (user-approved)

The user explicitly requires that organs must not be represented by abstract geometric primitives. A learner must be able to recognize the actual anatomical structure. “1:1” means faithful anatomical morphology, topology, spatial relationships, and relative proportions against a documented anatomical reference; it does not mean claiming life-size physical dimensions unless the source provides calibrated measurements.

### Required representation

- Use anatomically faithful, sourced organ meshes, segmented medical imaging, plastinated-specimen photography, or atlas plates.
- Use realistic anatomical surface form and correct neighboring structures. Do not replace the tongue with an ellipsoid, lungs with balloons, larynx with boxes/cylinders, or vocal folds with two generic curved lines.
- Provide correct view orientation and, where helpful, multiple views: anterior, posterior, lateral, superior, inferior, and midsagittal/coronal/axial section.
- For internal structures that are hidden in an external view, use a documented cutaway, transparent overlay, exploded layer view, or a separate anatomical plate. Do not imply that a cutaway is the intact external surface.
- If a source is a photograph or atlas plate rather than a 3D mesh, retain it as a high-fidelity 2D view and layer clickable labels/regions over it. A truthful 2D anatomical plate is better than an invented 3D organ.
- Interactive hotspots must be anchored to the real anatomical reference. Do not use decorative approximate coordinates that point to the wrong structure.
- Do not claim “1:1 exact dimensions” unless the source has calibrated scale data. State whether the view is true scale, proportional, or schematic.

### Asset acceptance

For every anatomical asset, record:
- author / institution / model title;
- source URL and retrieval/version date;
- licence and permitted use (including commercial redistribution and derivative works);
- anatomy coverage and missing structures;
- view orientation and coordinate convention;
- scale metadata, if any;
- whether it is a segmented scan, atlas reconstruction, plastinated specimen, or artist-built mesh;
- known inaccuracies or simplifications.

Reject any asset with unclear provenance/licence, misleading anatomy, or no usable view/orientation metadata. Prefer open, redistributable assets with clear attribution and licences. Embedding an externally hosted viewer is not a substitute for securing a stable source, usage rights, and a reliable experience.

### Anatomy skill boundary

The official Anatomy project describes itself as an isometric technical-figure toolkit. Its primitives are its own illustrated geometry; its beta 3D mode reprojects/re-shades those primitives. It is not a medical mesh pipeline and must never be used to generate the organ surfaces themselves. Use it only for separate explanatory apparatus, labels, force indicators, and readouts surrounding or annotating the sourced anatomical reference.

Official capability references:
- https://github.com/wheresryan22/anatomy
- https://github.com/wheresryan22/anatomy/blob/main/SKILL.md

### Revised acceptance gate

- [ ] Every organ shown is recognizably and anatomically faithful to a cited reference asset.
- [ ] No abstract primitive is used as a substitute for an organ or tissue.
- [ ] Every interactive label/hotspot maps to the correct visible structure.
- [ ] Cutaway/transparent/exploded views are explicitly identified as such.
- [ ] Scale claims match the source metadata; otherwise say “proportional reference”.
- [ ] Asset licence permits the intended use and is recorded.
- [ ] If no acceptable 3D mesh exists, use a real anatomical plate/specimen image rather than fabricate geometry.
