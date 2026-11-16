# Project agent skills

## Anatomy

The Anatomy agent skill is pinned as a Git submodule at `.agents/skills/anatomy` from https://github.com/wheresryan22/anatomy.

Initialize it when cloning the project with:

```bash
git clone --recurse-submodules https://github.com/OperaLirico/Opera-Lirico.git
```

If the repository is already cloned:

```bash
git submodule update --init --recursive
```

The upstream skill is MIT-licensed. Its instructions and toolkit are maintained in the upstream repository; this project pins a specific upstream commit so updates can be reviewed deliberately.

## Modern Web Guidance

Google's Modern Web Guidance skill is vendored at `.agents/skills/modern-web-guidance/SKILL.md`. Consult it before HTML, CSS, responsive-layout, accessibility, performance, and client-side JavaScript changes. It uses the upstream CLI to search and retrieve current guidance; it adds no runtime dependency to the published site.

Upstream: https://github.com/GoogleChrome/modern-web-guidance  
License: Apache-2.0. Review upstream changes before refreshing the vendored skill.
