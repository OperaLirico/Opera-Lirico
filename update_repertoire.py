#!/usr/bin/env python3
"""Do not bulk-import random LiederNet records into the public repertoire.

The previous sitemap sampler selected arbitrary texts from many languages and
settings. This inflated the public catalogue with obscure works while missing
standard teaching repertoire such as Amarilli and Nina. New public entries are
now curated explicitly with verified title, composer/attribution, category and
source. The historical automatic imports are retained in
data/repertoire_archive.json and are not loaded by the website.
"""

def main() -> None:
    print(
        "Automatic random repertoire import is paused. "
        "Add only reviewed, priority-ranked core repertoire to data/repertoire.json."
    )


if __name__ == "__main__":
    main()
