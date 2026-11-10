# P2/P4 source and extraction pilot

- Generated: 2026-11-10T18:11:22+01:00 (Europe/Rome)
- Pages captured: 5/5
- Advertised feeds checked: 2
- Feeds with vocal/audition entries: 0
- Production strategy changes: none
- Parser comparisons use identical HTML bytes.
- Metrics are coverage proxies, not accuracy scores; raw HTML is uploaded as a 30-day artifact.

## Teatro alla Scala

- URL: https://www.teatroallascala.org/it/il-teatro/lavora-con-noi/concorsi-e-audizioni-coro.html
- Fetch: ok; HTTP 200
- Snapshot: 29603 bytes; SHA-256 28793f609149db7ddfb7aec8cf738cda7cbe25ca85397c14cbae71255c41e59e
- robots.txt: ok HTTP 200
- Sitemap: https://www.teatroallascala.org/sitemap.xml — ok HTTP 200; type=sitemapindex; locs=2; vocal/audition URL matches=0
- DOM: 92 links; 20 relevant labels; 77 list items; 7 headings; 0 tables
- scrapling: 3454 chars; signals=4/6; relevant labels retained=3/3; runtime=0.0009s
- lxml_full_text: 4757 chars; signals=4/6; relevant labels retained=3/3; runtime=0.0008s
- trafilatura_plain: 1818 chars; signals=4/6; relevant labels retained=2/3; runtime=0.0094s
- trafilatura_markdown: 1855 chars; links=1; relevant links=1; runtime=0.0069s
- Recommendation: manual_review_required

## Concorso Francesco Morlacchi

- URL: https://www.concorsomorlacchi.it/
- Fetch: ok; HTTP 200
- Snapshot: 34805 bytes; SHA-256 c954dd570d97dc8a9a3b90c9420f91dc02046373c233aa1edf1e5ada4497037b
- robots.txt: http_error HTTP 404
- Sitemap: https://www.concorsomorlacchi.it/sitemap.xml — http_error HTTP 404; type=unavailable; locs=0; vocal/audition URL matches=0
- Sitemap: https://www.concorsomorlacchi.it/wp-sitemap.xml — http_error HTTP 404; type=unavailable; locs=0; vocal/audition URL matches=0
- Sitemap: https://www.concorsomorlacchi.it/sitemap_index.xml — http_error HTTP 404; type=unavailable; locs=0; vocal/audition URL matches=0
- DOM: 28 links; 28 relevant labels; 61 list items; 34 headings; 0 tables
- scrapling: 17733 chars; signals=6/6; relevant labels retained=8/8; runtime=0.0013s
- lxml_full_text: 17658 chars; signals=6/6; relevant labels retained=8/8; runtime=0.0009s
- trafilatura_plain: 12162 chars; signals=6/6; relevant labels retained=0/8; runtime=0.0094s
- trafilatura_markdown: 12253 chars; links=0; relevant links=0; runtime=0.0101s
- Recommendation: manual_review_required

## Teatro Carlo Felice

- URL: https://carlofelice.it/audizioni-e-concorsi/
- Fetch: ok; HTTP 200
- Snapshot: 398561 bytes; SHA-256 eec660fb26e701dbe308caab213be95f3af58650d23533743137b16d649b25a3
- robots.txt: ok HTTP 200
- Sitemap: https://www.carlofelice.it/sitemap.xml — ok HTTP 200; type=sitemapindex; locs=7; vocal/audition URL matches=0
- Feed: https://www.carlofelice.it/comments/feed/ — ok HTTP 200; entries=0; relevant entries=0
- Feed: https://www.carlofelice.it/feed/ — ok HTTP 200; entries=0; relevant entries=0
- Explicit public API links: https://www.carlofelice.it/wp-json/
- DOM: 465 links; 387 relevant labels; 173 list items; 1 headings; 0 tables
- scrapling: 52378 chars; signals=6/6; relevant labels retained=7/7; runtime=0.0118s
- lxml_full_text: 68502 chars; signals=6/6; relevant labels retained=7/7; runtime=0.0094s
- trafilatura_plain: 58971 chars; signals=6/6; relevant labels retained=1/7; runtime=0.1684s
- trafilatura_markdown: 60954 chars; links=187; relevant links=1; runtime=0.1844s
- Recommendation: manual_review_required

## Teatro Massimo

- URL: https://www.teatromassimo.it/audizioni/
- Fetch: ok; HTTP 200
- Snapshot: 135749 bytes; SHA-256 576e8eb4e393d3a24e4e0a41a059ad0e846a76408d71c42a4103e3ffc2486731
- robots.txt: ok HTTP 200
- Sitemap: https://www.teatromassimo.it/sitemap_index.xml — ok HTTP 200; type=sitemapindex; locs=25; vocal/audition URL matches=0
- DOM: 121 links; 30 relevant labels; 85 list items; 10 headings; 0 tables
- scrapling: 3728 chars; signals=4/6; relevant labels retained=1/1; runtime=0.0022s
- lxml_full_text: 31754 chars; signals=4/6; relevant labels retained=1/1; runtime=0.0016s
- trafilatura_plain: 906 chars; signals=4/6; relevant labels retained=0/1; runtime=0.0165s
- trafilatura_markdown: 911 chars; links=1; relevant links=0; runtime=0.0158s
- Recommendation: manual_review_required

## AsLiCo

- URL: https://aslico.org/edizione-in-corso/
- Fetch: ok; HTTP 200
- Snapshot: 376149 bytes; SHA-256 887e530634bdd3ed62b5cee4ed5d65dd67a2155955607b054325239ea72d1045
- robots.txt: ok HTTP 200
- Sitemap: https://aslico.org/sitemap_index.xml — ok HTTP 200; type=sitemapindex; locs=13; vocal/audition URL matches=0
- Explicit public API links: https://aslico.org/wp-json/
- DOM: 167 links; 11 relevant labels; 185 list items; 20 headings; 1 tables
- scrapling: 27005 chars; signals=6/6; relevant labels retained=9/9; runtime=0.0062s
- lxml_full_text: 168655 chars; signals=6/6; relevant labels retained=9/9; runtime=0.005s
- trafilatura_plain: 5421 chars; signals=6/6; relevant labels retained=1/9; runtime=0.0319s
- trafilatura_markdown: 5617 chars; links=0; relevant links=0; runtime=0.0329s
- Recommendation: manual_review_required

## Limitations

- robots.txt/sitemap availability does not prove relevant notices are present.
- Only page-advertised RSS/Atom and explicit public API links are inspected; no guessed API endpoint is queried.
- 403/429, login restrictions and unreadable robots policies are recorded and not bypassed.
- Parser counts and keyword signals are coverage proxies, not ground-truth accuracy.
- All parsers receive identical captured HTML bytes; no production policy is promoted automatically.
- Sitemap indexes are counted but nested child sitemaps are not recursively crawled in this pilot.
