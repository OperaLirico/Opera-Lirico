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
