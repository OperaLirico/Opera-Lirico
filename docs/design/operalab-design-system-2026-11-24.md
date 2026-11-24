# OperaLab — REA-Led Website Design Reverse Engineering

- Date: 2026-11-24
- Research owner: ERA Research Lab
- Product: OperaLab
- Status: research and design specification only; no production code changed or deployed

## 1. Goal

Create a distinct, coherent digital product for Chinese-speaking singers and vocal students who need to discover European opera opportunities, conservatory admissions, competitions, masterclasses, repertoire, and vocal-science learning resources.

The objective is not to imitate award-winning websites. It is to combine proven patterns into an OperaLab-specific system: **an editorial research desk for the performing voice** — authoritative like an academic resource, practical like an opportunity database, and expressive like an opera publication.

## 2. Scope and method

### Targets inspected

Public pages and available textual structure were reviewed for:
- Operabase — performing-arts entity graph, discovery and professional search.
- YAP Tracker — audition, competition, young-artist, training, masterclass, and grant taxonomy.
- Musicalchairs — discipline-based vacancies and concise listing metadata.
- Royal College of Music — course and vocal audition information architecture.
- Juilliard — application timeline, required materials, repertoire and audition stages.
- Royal Opera House — learning and participation audiences.
- Metropolitan Opera Learning Library — educational content taxonomy and formats.
- Bachtrack — event discovery and editorial/review archive.
- Mobbin and One Page Love — shipped UI patterns and section-level design references.

### Execution limitation

The active REA MCP tool catalog was not exposed in this session. This report therefore uses the REA research method with public-page inspection and source-level inspection; it does **not** claim runtime browser capture, REA Evidence IDs, HAR capture, interaction replay, or exhaustive mobile inspection. Pages that block automated access remain marked unknown. A future connected REA session should capture key workflows interactively before implementation.

### Product source inspected

OperaLab's current repository README, homepage HTML, primary CSS, and linked design layers were reviewed. The current homepage loads multiple overlapping stylesheets, including base styles, taste-home, theme-wine, several fix layers, opera-clean, motion, and site-system. This is a maintainability risk: the same visual decisions can be overridden in different places.

## 3. Findings: observed / inferred / unknown

### Observed

- Operabase separates public discovery from professional tools and connects performances, artists, organizations, works, places, and dates. Its public surface exposes large searchable entity categories and location/date/genre filters.
- Operabase's help material documents multi-field filtering and drill-down from performance result to cast, crew, dates, and venue.
- YAP Tracker publishes distinct opportunity classes rather than treating every item as one generic audition: competitions, young-artist programs, resident programs, mainstage, training, masterclasses, chorus, grants, and more.
- Musicalchairs groups jobs by instrument/voice category and exposes post date, closing date, location, eligibility/program detail, and application links.
- Royal College of Music organizes study and audition information around faculty, course level, audition method, requirements, dates, and admissions support.
- Juilliard's voice application pages distinguish application materials, deadlines, prescreening, repertoire requirements, audition stages, and decisions.
- Royal Opera House separates learning audiences and pathways such as young people, adults, schools, and community.
- The Met Learning Library groups educational resources by format and task: educator guides, illustrated synopses, arrangements, lesson plans, quizzes, and institutional learning access.
- Bachtrack combines event discovery with a large review/editorial archive and filters across event types and dates.
- Mobbin focuses on real shipped app/site screens and flows; One Page Love organizes complete sites, page sections, typefaces, and templates.
- OperaLab currently has multiple overlapping CSS layers. The current page is not starting from a clean single-source design system.

### Inferred

- OperaLab should model opportunities as structured records with type-specific fields, not a single generic card template.
- A singer needs a workflow that connects discovery → eligibility → repertoire/materials → deadline → official source, rather than just a feed of announcements.
- A school's admissions information should be presented as a normalized checklist while preserving the institution's original wording and official link.
- Masterclasses should be searchable by teacher, institution, city/country, dates, repertoire/voice type, price/fee status, and application deadline when those facts are published.
- Repertoire pages should connect work → composer → character/voice type → source text → score/source rights → learning notes, while clearly separating curated content from unreviewed candidates.
- The visual system should use a calm editorial foundation and reserve dramatic imagery/motion for high-value storytelling pages. Dense opportunity pages should remain quiet and scannable.
- The CSS overlap should be resolved by consolidating tokens and component ownership, not by appending another emergency stylesheet.

### Unknown

- Exact interactive behavior of every filter, search suggestion, modal, sticky element, and mobile navigation.
- The full DOM, runtime component structure, breakpoint behavior, loading states, and network contracts of the external references.
- Whether any external page's observed design is implemented with a reusable design system or one-off code.
- The full set of current OperaLab routes and page-specific style dependencies beyond the reviewed files.
- Real mobile screenshots and keyboard/screen-reader behavior for the selected reference sites.

## 4. Reference-to-pattern mapping

| Reference | Study for | Pattern worth adapting | Do not copy |
|---|---|---|---|
| Operabase | Global structured performing-arts discovery | Connected entities, filters, artist/work/institution cross-links | Its scale and professional casting features are not OperaLab's current scope |
| YAP Tracker | Audition and training taxonomy | Opportunity categories, counts, category-specific search | Paid account wall or its exact taxonomy without user validation |
| Musicalchairs | Job listing clarity | Discipline, location, posted/closing dates, concise eligibility, official action | Dense legacy layout or unverified listing data |
| Royal College of Music | Conservatory admissions | Course → faculty → audition requirements → dates → contact | UK-specific application rules as universal rules |
| Juilliard | Application checklist | Deadline timeline, materials checklist, repertoire requirements, audition stages | Institution-specific rules and proprietary text |
| Royal Opera House | Learning journeys | Audience segmentation and pathway-based resource discovery | Large institution navigation complexity |
| Met Learning Library | Educational library | Content formats, curated guides, lesson plans, illustrated learning | Copying content, illustrations, or lesson plans |
| Bachtrack | Editorial archive | Editorial discovery, event/date filters, review metadata | Review tone/content and broad event scope |
| Mobbin | Product interaction patterns | Real flows, states, mobile controls | Paid/private screen captures or proprietary UI assets |
| One Page Love | Section-level visual comparison | Hero, FAQ, navigation, timeline, CTA and footer pattern library | Templates/assets without license review |

## 5. Additional websites worth reverse-engineering

Priority is based on OperaLab user value, not visual novelty.

### P0 — inspect first

1. **Operabase** — https://www.operabase.com/en  
   Inspect: search facets, entity relationships, artist profile, work profile, institution profile, performance detail, public/pro split.  
   Output: OperaLab entity and cross-link model.

2. **YAP Tracker** — https://www.yaptracker.com/  
   Inspect: opportunity categories, listing card, detail page, saved/search behavior if publicly visible, European opportunities, masterclass/training taxonomy.  
   Output: opportunity classification and filter model.

3. **Musicalchairs** — https://www.musicalchairs.info/  
   Inspect: voice-type/instrument categories, closing-date visibility, listing details, related opportunities, RSS/feed and source attribution.  
   Output: concise audition/opportunity list and deadline model. Automated page access returned a bot-protection page; do not bypass it. Use public search results and manually accessible pages only.

4. **Royal College of Music** — https://www.rcm.ac.uk/  
   Inspect: vocal faculty/course navigation, audition requirements, deadlines, audition methods, international applicant information.  
   Output: conservatory record and admissions checklist.

5. **Juilliard** — https://www.juilliard.edu/  
   Inspect: voice-specific application, prescreening, repertoire requirements, interview/audition stages, decision timeline.  
   Output: normalized admissions requirement schema; keep school-specific requirements separate.

### P1 — inspect after P0

6. **Metropolitan Opera Learning Library** — https://www.metopera.org/learn/  
   Inspect: educational resource taxonomy, opera synopsis, educator guide, lesson plan, learning modules.  
   Output: future OperaLab learning-resource architecture.

7. **Royal Opera House Learning & Participation** — https://www.rbo.org.uk/learning  
   Inspect: audience-specific pathways, learning platform entry, emerging talent, adult and community routes.  
   Output: learning pathways and audience segmentation.

8. **Bachtrack** — https://bachtrack.com/  
   Inspect: event search, date/location filters, review archive, editorial landing pages, language selection.  
   Output: editorial/news layer distinct from opportunities database.

9. **IMSLP / Petrucci Music Library** — https://imslp.org/  
   Inspect: work/composer/edition metadata, score source attribution, file/edition distinctions, rights notices.  
   Output: repertoire source and rights metadata. Do not copy score files; link to authoritative source and respect territory-specific rights.

### P2 — design and interaction reference libraries

10. **Awwwards** — https://www.awwwards.com/  
    Use to discover expressive visual storytelling and interaction ideas; treat award status as inspiration, not proof of usability.

11. **CSS Design Awards** — https://www.cssdesignawards.com/  
    Compare visual design, usability, and innovation as separate dimensions.

12. **The FWA** — https://thefwa.com/  
    Discover experimental digital experiences; selectively study storytelling and motion.

13. **SiteInspire** — https://www.siteinspire.com/  
    Search by typographic, editorial, minimal, art, and museum categories.

14. **One Page Love** — https://onepagelove.com/  
    Study individual page sections and typefaces; useful for comparing patterns side by side.

15. **Mobbin** — https://mobbin.com/  
    Study real product screens and end-to-end mobile/web flows. Use public previews or a properly licensed account; do not extract gated content.

## 6. Original OperaLab design direction

### Product identity

**OperaLab — The European Vocal Arts Research Desk**

Chinese positioning: 面向中文声乐学习者的欧洲声乐机会、院校申请与专业学习资料平台。

Brand qualities:
- Editorial, not corporate SaaS.
- Scholarly, not academic bureaucracy.
- Warm and human, not ornate or theatrical kitsch.
- Evidence-led, not generic AI content.
- Calm for daily research; expressive for music and anatomy storytelling.

### Visual system

- Foundation: warm ivory / parchment surface, deep wine ink, muted rosewood, restrained antique brass.
- Typography: a readable sans-serif for Chinese interface and dense data; a restrained editorial serif for selected display headings and long-form cultural content. Avoid applying a decorative serif to every label.
- Layout: consistent 12-column desktop grid, one-column mobile reading flow, clear max-width, predictable spacing scale.
- Imagery: real performance photography, institution imagery, licensed score/archival material, and accurate anatomical visuals. No generic geometric placeholders for anatomy.
- Motion: short, purposeful transitions for navigation, filtering, panel opening, and visual storytelling. Respect reduced-motion settings. No perpetual floating or scroll-jacking.
- Density: opportunity and admissions pages prioritize scanability over oversized hero sections.

### Information architecture

1. **Discover** — open auditions, competitions, programs, deadlines.
2. **Conservatories** — institution directory, course, voice faculty, audition requirements.
3. **Opera studios & academies** — young artist programs, opera studio, residency and training.
4. **Masterclasses** — teacher, institution, place, dates, fee, application.
5. **Repertoire** — curated arias and art songs, composer, language, voice type, text and score sources.
6. **Voice science** — anatomy, phonation, resonance and practical learning modules.
7. **Research notes / editorial** — explainers, application guides, source-backed articles.

Keep the top-level navigation short. Do not create a new top-level category unless it represents a distinct user task.

### Reusable page templates

- Opportunity list + filter panel + result count + deadline status.
- Opportunity detail + eligibility + required materials + timeline + official source.
- Institution profile + courses + voice faculty + admissions routes.
- Audition requirement checklist + original source wording + verified date.
- Masterclass listing + teacher/institution + schedule + fee + application.
- Repertoire detail + work/character/voice type + language + text/score source + rights note.
- Learning module + visual explanation + references + related topics.

### Data trust rules

- Separate verified/current, awaiting review, expired, and inaccessible source states.
- Never present a scraped excerpt as proof that applications are still open.
- Show the original official source and last checked date.
- Preserve source wording for deadlines and repertoire requirements.
- Make unknown fields explicit rather than guessing.
- Keep unreviewed repertoire candidates out of the public library.

## 7. Existing codebase implications

The homepage currently links multiple CSS layers that overlap in token and component responsibility. Before a full redesign:
1. Inventory all stylesheet selectors and route ownership.
2. Capture desktop/mobile baselines for each route.
3. Define one canonical token file and component ownership.
4. Move page-specific styles into page-scoped files.
5. Remove obsolete override layers only after visual regression checks.
6. Keep motion in one motion layer with reduced-motion support.
7. Test every page route, not only the homepage.

Do not start by deleting CSS files. Some files may contain fixes required by secondary pages.

## 8. Implementation sequence

### Slice 1 — design-system foundation
- Establish canonical tokens, type scale, spacing, radii, shadows, breakpoints, and motion rules.
- Consolidate navigation, buttons, links, cards, metadata rows, status labels, and page headers.
- Acceptance: no duplicate conflicting global token owners; desktop and mobile screenshots remain stable or improve.

### Slice 2 — opportunity discovery
- Rebuild one list and one detail page using the new tokens and existing data contracts.
- Add clear deadline, location, voice type, opportunity category, eligibility, source and verification status.
- Acceptance: a user can find a relevant listing and reach its official source with fewer ambiguous steps.

### Slice 3 — conservatory and masterclass
- Normalize institution/course and masterclass structures.
- Add filter and checklist patterns without losing source-specific nuance.
- Acceptance: source requirements remain visible and all dates/fees have provenance.

### Slice 4 — repertoire and voice science
- Give repertoire pages an editorial reading experience.
- Give anatomy/voice-science pages richer visual storytelling while maintaining anatomical accuracy and source notes.
- Acceptance: mobile reading, image/model accessibility, and reduced-motion all pass.

### Slice 5 — browser QA and release
- Capture all key flows and states.
- Run mobile, keyboard, reduced-motion, empty/loading/error and source-link checks.
- Deploy only after review and explicit approval.

## 9. Decision

**Adopt:** structured opportunity taxonomy, institution/course/audition hierarchy, explicit deadlines and source provenance, editorial learning taxonomy, section-level design research, and a single canonical design system.

**Adapt:** visual storytelling, high-impact hero layouts, motion, and rich media for pages where they improve understanding.

**Defer:** 3D navigation, full-screen cinematic scroll experiences, complex GSAP timelines, and a full CSS framework migration.

**Reject:** copying external logos, page copy, imagery, proprietary code, or gated product screens; adding motion that slows search and reading; treating an award-winning visual as proof of good UX.

## 10. Sources and evidence

Public sources reviewed on 2026-11-24:

- Operabase public discovery and entities: https://www.operabase.com/en
- Operabase search/help: https://help.operabase.com/knowledge/en/performances-tickets
- YAP Tracker publishing taxonomy: https://www.yaptracker.com/what-we-publish
- Musicalchairs vacancies and categories: https://www.musicalchairs.info/jobs.php
- Musicalchairs mission: https://www.musicalchairs.info/about/
- Royal College of Music vocal audition requirements: https://www.rcm.ac.uk/vocal/auditionrequirements/
- Royal College of Music applications: https://www.rcm.ac.uk/apply/
- Juilliard College Voice audition requirements: https://www.juilliard.edu/arm/music/college/voice/bachelor-music
- Royal Opera House Learning: https://www.rbo.org.uk/learning
- Metropolitan Opera Learning Library: https://www.metopera.org/learn/education/learning-library/
- Bachtrack reviews and event discovery: https://bachtrack.com/find-reviews
- Mobbin reference library: https://mobbin.com/
- One Page Love website/section library: https://onepagelove.com/
- SiteInspire categories: https://www.siteinspire.com/websites/category/galleries-and-museums
- FWA awards archive: https://thefwa.com/

All external pages are reference material. No external assets, source code, proprietary copy, gated content, or private data were copied into OperaLab.
