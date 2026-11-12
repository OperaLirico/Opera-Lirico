# Per-source fetch strategy

## Current baseline

The production source registry currently contains 44 unique URLs in data/sources.json. The daily collector uses Scrapling for the fixed source list and the rotating legacy registry. data/source_fetch_policies.json records that as the current implementation, not as proof that Scrapling is optimal for every site.

Every source begins with strategy_status = baseline_only. No alternative is marked available until the exact official endpoint or feed is checked and tested.

## Assessment order

For each source, inspect in this order:

1. Official API or downloadable dataset.
2. RSS/Atom and sitemap.
3. Public JSON/XHR endpoint documented or visibly used by the official page.
4. Ordinary HTTP plus lxml/parsel for stable static HTML.
5. Existing Scrapling selector path for pages with changing markup.
6. Playwright only when required content is genuinely client-rendered and no permitted public endpoint exists.
7. curl_cffi only for a reproducible, permitted TLS/HTTP compatibility issue.

Do not introduce proxies, stealth, login sessions, CAPTCHA solving or access-control bypasses. A 403/429 or login wall is a monitoring blind spot, not an invitation to evade controls.

## Benchmark before switching

For a representative page snapshot, compare:
- field completeness: title, notice date, voice type, deadline, fee, age, eligibility, application link and PDF;
- extraction precision against first-party page evidence;
- runtime and request count;
- stability under small markup changes;
- dependency size and maintenance cost.

Keep the current method unless a repeatable test shows a clear improvement. Do not install all candidate libraries globally.

## Status

The policy registry is a coverage baseline only. As of 2026-11-12, **20/44 sources have evidence-backed P2 assessments and 24 remain `baseline_only`**. Production still uses Scrapling for every assessed source. Update each entry with exact evidence report, test date, discovery methods, chosen method and reason; do not treat an RSS/sitemap/API discovery signal as an approved opportunity.


## Redirect safety in the discovery pilot

The P2/P4 evaluation uses a same-host redirect handler. A cross-host redirect is not followed automatically: the destination host's robots.txt is checked first. If the destination robots policy is unavailable (except HTTP 404) or disallows the target path, the request stops and is recorded. A robots.txt redirect is followed only when the target remains a robots.txt path. The target policy file is fetched directly; redirects to non-robots paths, loops, or chains beyond the small cap require manual review. This is conservative and may create a review item for legitimate CDN or canonical-host redirects; it must not be weakened by silently following redirects.


## Structured link preservation

The production Scrapling collector also stores a bounded list of relevant first-party anchor targets separately from page text. Each record keeps the visible label and absolute URL. When more than 1,000 relevant links exist, it records the total and an explicit truncation flag instead of implying full coverage. Privacy, social, shop and other navigation noise is filtered. The last-good snapshot behavior preserves these links on a failed refresh.


## Batch 4 — 2026-11-12

Five additional official vocal-competition pages were evaluated on identical captured HTML:

- **source-12 Ente Lirico Italiano:** keep Scrapling; use the permitted sitemap as secondary discovery (7 vocal/audition URL matches). The advertised WordPress API root returned HTTP 403; no bypass or retry was attempted.
- **source-13 Tommaso Traetta Opera Festival:** keep Scrapling; the advertised RSS feed exposed 10 entries matching broad vocal/audition discovery signals. Common sitemap paths were unavailable; no guessed API routes were queried.
- **source-14 CLIP Portofino:** keep Scrapling and direct HTML links. The first five of 11 sitemap children yielded 722 URLs, but the three vocal-keyword matches were media/award images, not announcement pages.
- **source-21 Premio Fausto Ricci:** keep Scrapling HTML-only. robots.txt and sitemap paths returned 404; the official page itself exposed the application form and Italian/English regulation PDFs.
- **source-22 Concorso Maria Malibran:** keep Scrapling HTML-only. Its 20-page sitemap had no vocal URL hits; the official competition page directly exposed the Italian/English regulations PDFs.

Across this batch, Trafilatura did not preserve the relevant link labels/targets consistently enough to replace the existing structured Scrapling + href capture. lxml returned broader text on some pages, not a demonstrated accuracy improvement. No production fetch method changed. The RSS feed is discovery-only; every notice still needs first-party verification.
