# REA MCP setup for OperaLab

This guide is for the local coding-agent environment used to work on this repository. The project skill lives at `.agents/skills/rea-reverse-engineering/SKILL.md`; it does not itself install or connect the REA MCP server.

## Official sources

- Repository: https://github.com/morluto/rea
- Installation guide: https://github.com/morluto/rea/blob/main/docs/getting-started/installation.md
- Client configuration: https://github.com/morluto/rea/blob/main/docs/getting-started/client-configuration.md
- Official package: `rea-agents`

## Recommended Codex setup

Prerequisites: Node.js and npm are already installed, and Codex is installed locally.

From a trusted directory outside the OperaLab repository, run:

```bash
npx -y rea-agents@latest setup --client codex --skill=false
```

Why `--skill=false`: OperaLab already carries its own project-specific skill. This command is intended to register the official REA MCP server without replacing or duplicating the project's tailored instructions.

The setup process previews the exact configuration paths and proposed changes. Review the plan and approve it only if it targets the intended Codex profile. Do not use `--all-detected` for this project-specific setup.

Then restart/reconnect Codex and check the registration:

```bash
npx -y rea-agents@latest doctor --client codex --json
```

A successful doctor result checks local registration and prerequisites; it does not prove that the currently running agent session has loaded the tools. Confirm that the live agent tool list includes the REA server and its operations.

## If the project uses another agent

Use the official setup guide and select only the actual client in use. Do not guess the client identifier or manually edit a global configuration file without first reading the current client configuration guide.

For skill-only installation (instructions without MCP registration), the upstream documented command is:

```bash
npx skills add morluto/rea --skill reverse-engineer-anything
```

This is not a substitute for MCP setup.

## Provider requirements

- Static JavaScript/Electron analysis and passive capture inspection can work without a native decompiler.
- Native decompilation and some Android/firmware workflows require separately installed providers or tools.
- REA setup does not automatically install or upgrade Node.js, npm, Java, Ghidra, IDA, JADX, Hopper, Binwalk, or Unblob.
- Install optional providers only when the selected task requires them and after reviewing the installation plan.

## Recovery

1. If REA tools are missing in the active session, first determine whether the setup-owned MCP registration exists.
2. If registration is aligned but the current session has no tools, restart/reconnect the agent.
3. If setup or launch failed, read the current official connection/recovery guide and use the exact remediation for the observed error.
4. Do not repeatedly run setup, install unrelated providers, disable the client's sandbox, or broaden permissions as a generic fix.
5. Keep client configuration backups and preserve unrelated MCP servers and approval settings.

## Current project integration status

- Project skill: committed under `.agents/skills/rea-reverse-engineering/`.
- MCP setup: documented here, but local client registration must be run on the user's machine. A GitHub repository write cannot modify the local Codex/Claude/Cursor configuration or restart the local agent.
- MCP runtime verification: pending until the local agent is restarted and its live tool catalog is checked.
