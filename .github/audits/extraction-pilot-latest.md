# P2/P4 source and extraction pilot

- Generated: 2026-11-10T18:07:18+01:00 (Europe/Rome)
- Pages captured: 5/5
- Production strategy changes: none
- Parser comparisons use identical HTML bytes.
- Metrics are coverage proxies, not accuracy scores; raw HTML is uploaded as a 30-day artifact.

## Teatro alla Scala

- URL: https://www.teatroallascala.org/it/il-teatro/lavora-con-noi/concorsi-e-audizioni-coro.html
- Fetch: ok; HTTP 200
- Snapshot: 29603 bytes; SHA-256 70ad179ce7e12e1964abcf0fe086e0b7cb467c025c809309162e6a6a7addf4fc
- robots.txt: ok HTTP 200
- Sitemap: https://www.teatroallascala.org/sitemap.xml — ok HTTP 200, 2 loc
- scrapling: 3454 chars; signals 4/6; relevant link labels 11
- lxml_full_text: 4757 chars; signals 4/6; relevant link labels 11
- trafilatura: 1818 chars; signals 4/6; relevant link labels 11
- Recommendation: manual_review_required

## Concorso Francesco Morlacchi

- URL: https://www.concorsomorlacchi.it/
- Fetch: ok; HTTP 200
- Snapshot: 34805 bytes; SHA-256 c954dd570d97dc8a9a3b90c9420f91dc02046373c233aa1edf1e5ada4497037b
- robots.txt: http_error HTTP 404
- Sitemap: https://www.concorsomorlacchi.it/sitemap.xml — http_error HTTP 404, 0 loc
- Sitemap: https://www.concorsomorlacchi.it/wp-sitemap.xml — http_error HTTP 404, 0 loc
- scrapling: 17733 chars; signals 6/6; relevant link labels 10
- lxml_full_text: 17658 chars; signals 6/6; relevant link labels 10
- trafilatura: 12162 chars; signals 6/6; relevant link labels 10
- Recommendation: manual_review_required

## Teatro Carlo Felice

- URL: https://carlofelice.it/audizioni-e-concorsi/
- Fetch: ok; HTTP 200
- Snapshot: 398561 bytes; SHA-256 28938772c864520bdb7bf660127a5796fe3778ebf9ee61632f9fcd368e76bf50
- robots.txt: ok HTTP 200
- Sitemap: https://www.carlofelice.it/sitemap.xml — ok HTTP 200, 7 loc
- Feed: https://www.carlofelice.it/comments/feed/ — ok HTTP 200
- Feed: https://www.carlofelice.it/feed/ — ok HTTP 200
- scrapling: 52378 chars; signals 6/6; relevant link labels 9
- lxml_full_text: 68502 chars; signals 6/6; relevant link labels 9
- trafilatura: 58971 chars; signals 6/6; relevant link labels 9
- Recommendation: manual_review_required

## Teatro Massimo

- URL: https://www.teatromassimo.it/audizioni/
- Fetch: ok; HTTP 200
- Snapshot: 135774 bytes; SHA-256 1b0084e6ef504dfac638b0c432fb7743f35f32e6a873be419490dd199a182e91
- robots.txt: ok HTTP 200
- Sitemap: https://www.teatromassimo.it/sitemap_index.xml — ok HTTP 200, 25 loc
- scrapling: 3728 chars; signals 4/6; relevant link labels 2
- lxml_full_text: 31778 chars; signals 4/6; relevant link labels 2
- trafilatura: 906 chars; signals 4/6; relevant link labels 2
- Recommendation: manual_review_required

## AsLiCo

- URL: https://aslico.org/edizione-in-corso/
- Fetch: ok; HTTP 200
- Snapshot: 376149 bytes; SHA-256 887e530634bdd3ed62b5cee4ed5d65dd67a2155955607b054325239ea72d1045
- robots.txt: ok HTTP 200
- Sitemap: https://aslico.org/sitemap_index.xml — ok HTTP 200, 13 loc
- scrapling: 27005 chars; signals 6/6; relevant link labels 9
- lxml_full_text: 168655 chars; signals 6/6; relevant link labels 9
- trafilatura: 5421 chars; signals 6/6; relevant link labels 9
- Recommendation: manual_review_required

## Limitations

- robots.txt/sitemap availability does not prove relevant notices are present.
- Only advertised RSS/Atom feeds are checked.
- 403/429 are recorded, never bypassed.
- Parser counts and keyword signals are proxies, not ground-truth accuracy.
- All parsers receive identical captured HTML bytes; no production policy is promoted automatically.
