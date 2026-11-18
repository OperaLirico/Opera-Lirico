# OperaLab. Voice Anatomy — Resource Audit (2026-11)

Status: research draft; no assets copied into the public site yet.
Scope: lawful reuse, technical suitability, visual comfort, and implementation path for the voice-anatomy teaching area.

## Executive decision

Use a three-layer resource strategy:
1. **Primary self-hostable 3D assets:** University of Dundee / BodyParts3D models whose individual Sketchfab pages explicitly grant a compatible Creative Commons licence.
2. **Reference-only commercial atlas:** Complete Anatomy for anatomical cross-checking and interaction-design research. Do not extract its models, screenshots, videos, or other content for the public OperaLab site without written permission.
3. **Real vocal-fold motion:** use selected, rights-cleared high-speed video/laryngoscopy clips or datasets. Treat clinical datasets as research material first; do not assume a dataset licence authorizes republishing patient video on a public website.

This audit does not authorize deletion of existing pages. Replace and verify the new experience first, then retire duplicate or misleading legacy sections.

## Candidate asset register

| ID | Asset | Evidence / rights | Intended use | Decision |
|---|---|---|---|---|
| A01 | Dundee — Anatomy of the Larynx | Sketchfab page states CC BY-SA 4.0; derivative of BodyParts3D, whose source attribution is CC BY-SA 2.1 Japan. Credit University of Dundee and BodyParts3D / Database Center for Life Science; adaptations must retain compatible share-alike terms. 34.7k triangles / 17.4k vertices. | Main laryngeal cartilage / structure model; downloadable source candidate. | **Approved in principle**, verify downloaded archive, exact file format, object separation, attribution, and any embedded texture credits before bundling. |
| A02 | Dundee — Larynx with Muscles and Ligaments | Dundee confirms this was created for ENT teaching. A rights notice on a separate teaching site credits the Dundee model under CC BY-NC-SA 4.0; because the Sketchfab model's own licence badge could not be directly inspected in this session, treat the asset conservatively as non-commercial pending confirmation from the original rights holder. | Strong anatomical reference for laryngeal muscles and ligaments. | **Reference only for now**; no commercial self-hosting or modification until written clarification / compatible licence is obtained. |
| A03 | Dundee — Pharynx and Floor of Mouth | Individual page states CC BY-NC-SA 4.0. Model was made using CT data and sculpting; anatomical content approved by an anatomist. | Pharynx / tongue-base spatial reference. | **Do not bundle into a commercial/publicly monetized site** without separate permission; may be linked as an external reference. |
| A04 | Complete Anatomy (Elsevier) | Official terms grant limited personal, non-commercial use; content may not be copied, modified, distributed, reverse-engineered, or made available to multiple users. Commercial/public use of images and videos requires permission. | Research anatomy, compare spatial relationships, study UI/teaching patterns. | **Reference only**. No model extraction, scraping, screenshot harvesting, or republishing. Request a written licence if specific media are needed. |
| A05 | GIRAFE high-speed videoendoscopy dataset | 65 recordings from 50 patients, captured at 4,000 fps; 15 healthy controls, 26 with diagnosed voice disorders, 24 unknown health status. CC BY-NC 4.0. | Scientific study of true vocal-fold vibration, onset/offset, mucosal wave and derived playbacks. | **Research-only / non-commercial restriction**. Do not republish raw patient clips on OperaLab without additional permission and privacy review. |
| A06 | Simultaneous high-speed video laryngoscopy and acoustic/aerodynamic recordings during vocal onset (2024) | Article is CC BY 4.0. The experiment recorded six healthy volunteers (three men, three women) at 2,000 fps, with synchronized acoustic/aerodynamic measurements. The article page provides image montages and states that underlying data are available by contacting the author; it does **not** provide an openly downloadable raw-video package on the article page. | Strong scientific evidence for explaining vocal onset and the relationship between vocal-fold movement, loudness, airflow and pressure. | **Use article and CC BY figures with attribution**; contact author for raw clips and written confirmation of reuse rights before embedding video. Do not describe this paper as an already-downloadable video library. |
| A07 | BAGLS / BAGLS-VF | Public research dataset; BAGLS-VF provides 59,250 frames and segmentation masks. Current dataset record states CC BY-NC-SA 4.0. | Technical research / segmentation reference, not a default public-facing media library. | **Non-commercial only** unless permission is obtained. |
| A08 | Sergei Nekludau — Larynx anatomy 3D model | Sketchfab lists CC BY. Creator says the model was made from anatomical illustrations; 43.6k triangles / 21.8k vertices. This is a creator-built teaching model, not a scanned specimen or an anatomist-validated specimen reconstruction based on the available description. | Possible secondary model for comparison and interaction prototyping. | **Candidate only**; inspect geometry, mesh labels, accuracy and source references before any teaching use. Credit creator and retain CC BY attribution. |

## Important licensing distinction

- **Downloadable** does not mean **unrestricted**.
- A model may be embedded by its host platform while the same model is not licensed for self-hosting or modification.
- A research dataset may be open to download but restricted from commercial reuse.
- For patient-derived video, additionally check the paper's ethics, anonymization, consent scope, and dataset-specific terms.
- Complete Anatomy should be treated as a paid learning/reference product, not as a source of assets to extract.
- A Creative Commons licence does not certify anatomical accuracy. Rights clearance and medical validation are separate checks.

## Technical implementation recommendation

### 1. 3D asset pipeline

For each approved downloadable model:
1. Download through the official platform's provided download control and authenticated account where required.
2. Preserve the original archive unchanged in a local source-assets folder.
3. Record the model URL, author, source institution, licence URL, download date, archive checksum, file names, and any required attribution.
4. Inspect formats and dependencies. Prefer glTF / GLB for web delivery when the supplied licence and archive permit conversion; retain original files for provenance.
5. Optimize a separate web copy only after checking mesh integrity, normals, textures, object names, scale, and anatomical completeness.
6. Add visible credits and a licence notice adjacent to the viewer and in a central ASSET-CREDITS.md file.

Do not commit large raw archives until repository size and hosting strategy have been reviewed. If an asset is large, use a suitable versioned asset host or Git LFS only after confirming the project's hosting constraints.

### 2. Learning experience

Build one coherent Voice Anatomy learning area rather than two overlapping pages:
- **Orientation:** whole-body / head-and-neck context. Use a legally embeddable model or original labelled diagrams; Complete Anatomy remains a research reference unless permission is granted.
- **Laryngeal structure:** licensed Dundee model, with toggles for cartilages, intrinsic muscles, ligaments and vocal folds only where the source mesh supports those separations.
- **Phonation in motion:** user-initiated real high-speed video, with a plain-language explanation and source/rights label. No autoplay.
- **Breathing and vocal tract:** separate, clearly labelled explanatory modules; do not imply that one 3D model simulates physiology.

Every visual must be labelled accurately as one of:
- anatomical 3D model;
- real clinical endoscopic recording;
- derived scientific visualization / segmentation;
- explanatory schematic.

Never present a schematic animation as real tissue motion or a static anatomical model as a live physiological simulation.

### 3. Comfort and accessibility

- No autoplay and no surprise motion.
- Use a calm poster frame and an explicit Play control.
- Provide a hide clinical footage option and keep clinical clips collapsed by default.
- Avoid pathology footage in the default learning path; separate healthy-function examples from clinical examples.
- Add captions / text explanations and keyboard-accessible controls.
- Keep the default visual treatment clean, non-graphic, and consistent with OperaLab.'s editorial design.

## Immediate next actions

1. Download A01 through Sketchfab's official download flow; inspect the archive locally and record its exact format and checksum. Sketchfab's Download API requires user authentication; do not bypass it.
2. If A01's mesh structure is insufficient, compare it with A08 after obtaining the official downloadable file and checking the creator's source/accuracy information.
3. Request written confirmation from Dundee / the model rights holder for the exact licence of **Larynx with Muscles and Ligaments**. Do not assume commercial reuse is permitted.
4. Contact the author of the 2024 vocal-onset study for raw high-speed video and written permission for public website display. The paper's CC BY licence covers the article and its covered contents, but the raw recordings are not provided as a downloadable data package on the article page.
5. Identify a small number of healthy-function high-speed clips with explicit public display rights. GIRAFE is useful evidence and research data, but its CC BY-NC licence is not suitable for assuming commercial public reuse.
6. Build the new consolidated anatomy page on a feature branch. Only after functional, anatomical, licence, mobile, and comfort checks pass should legacy duplicate/low-quality sections be removed.

## Sources

- Dundee, Anatomy of the Larynx (CC BY-SA 4.0): https://sketchfab.com/3d-models/anatomy-of-the-larynx-a00bc73a303c46248db6a13a88b23404
- Dundee TILT model collection (includes Larynx with Muscles and Ligaments): https://sketchfab.com/tilt/models
- Dundee project description for the larynx muscles / ligaments model: https://www.dundee.ac.uk/tilt/medical-illustration/parapharyngeal-space
- Independent attribution record identifying CC BY-NC-SA 4.0 for the Dundee larynx model: https://masterclass.morgavi.fr/mentions-legales
- Dundee, Pharynx and Floor of Mouth (CC BY-NC-SA 4.0): https://sketchfab.com/3d-models/pharynx-and-floor-of-mouth-b262c70bf9bd49c2a5428581b754f24b
- Sketchfab Download API licensing / authentication guidance: https://sketchfab.com/developers/download-api/guidelines
- Complete Anatomy Terms of Use: https://3d4medical.com/terms
- Complete Anatomy use of imagery and videos: https://3d4medical.com/use-of-imagery-videos
- GIRAFE dataset paper (CC BY-NC 4.0; 4,000 fps; 65 recordings): https://pmc.ncbi.nlm.nih.gov/articles/PMC11872128/
- Vocal onset high-speed laryngoscopy study (2024, CC BY 4.0; six healthy volunteers; 2,000 fps; underlying data by author request): https://pmc.ncbi.nlm.nih.gov/articles/PMC11048587/
- Sergei Nekludau, Larynx anatomy 3D model (CC BY; based on illustrations): https://sketchfab.com/3d-models/larynx-anatomy-3d-model-c2ffa5fc50ad4302baf58c2f9d49b9d4
- BAGLS-VF dataset record (CC BY-NC-SA 4.0): https://zenodo.org/records/18980436

## Audit limitations

- Sketchfab pages were discoverable through public search, but direct page opening returned access denial in this research session. The A01 public search result exposes its model metadata and licence; actual download still requires the platform's official authenticated flow.
- No binary model file was downloaded in this step. The repository currently contains this research record only; it does not yet contain a new 3D asset or a deployed page.
- A medical professional should review anatomical labelling and explanatory claims before publication.
