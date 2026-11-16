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

## REA reverse engineering

The OperaLab-specific REA workflow is maintained at `.agents/skills/rea-reverse-engineering/SKILL.md`. It guides authorized research of external app/site behavior, evidence capture, reconstruction planning, and verification.

The project skill is based on the official REA project at https://github.com/morluto/rea. Local MCP registration is separate; see `.agents/skills/rea-reverse-engineering/references/mcp-setup.md`.


## REA Research Lab

The reusable, cross-project research method is maintained at `.agents/skills/rea-research-lab/SKILL.md`. It defines the Research → Evidence → Architecture → Development → Quality → Stewardship workflow and supports authorized research across web, app, JavaScript/Electron, native, Android, runtime, network, firmware, and package targets.

Operating guide and templates: `docs/rea-research-lab/`. The daily upstream watch checks official GitHub release, npm package, and Skill metadata drift; it does not update the user's local MCP runtime.
