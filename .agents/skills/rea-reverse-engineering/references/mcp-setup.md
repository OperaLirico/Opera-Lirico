# REA MCP setup for OperaLab

This guide connects the official REA MCP server to the local coding agent. The OperaLab-specific workflow lives at `.agents/skills/rea-reverse-engineering/SKILL.md`; keep that project skill alongside REA's upstream `reverse-engineer-anything` skill.

## Official sources

- Repository: https://github.com/morluto/rea
- Installation guide: https://github.com/morluto/rea/blob/main/docs/getting-started/installation.md
- Official package: `rea-agents`
- MCP Registry identifier: `io.github.morluto/rea`
- MCP runtime contracts: https://github.com/morluto/rea/blob/main/docs/reference/mcp-contracts.md
- Connection and recovery guide: https://github.com/morluto/rea/blob/main/.agents/skills/reverse-engineer-anything/references/connection-and-recovery.md

## MCP tool contracts and readiness

The upstream [MCP runtime contracts](https://github.com/morluto/rea/blob/main/docs/reference/mcp-contracts.md) explain Evidence result semantics and retained references. The live MCP `tools/list` response is the canonical source for complete tool input/output schemas; this guide and a release note do not prove that a particular tool is loaded in the active session. Always use the actual advertised tool names and schemas.

For native or artifact workflows, if the connected catalog advertises `binary_session`, call it with `{}` before choosing an operation and inspect `result.tool_availability` and client requirements. This is a task-scoped capability check, not a generic check that browser-only REA workflows need.

## Recommended Codex installation: official plugin

Use the official Codex plugin route when working in Codex CLI:

```bash
codex plugin marketplace add morluto/rea
codex plugin add rea@rea
codex plugin list
```

Then restart/reconnect Codex and verify that its live tool list contains the `rea` MCP server and its tools. The official plugin bundles the upstream REA skill and MCP server. It does not install native analysis engines such as Ghidra, IDA, Hopper, JADX, Binwalk, or Unblob.

Do not also register a second REA server with `rea setup` in the same Codex profile. Choose the plugin route or the direct setup route below, not both, to avoid duplicate MCP servers.

If Codex is not the CLI build or plugin commands are unavailable, use the client configuration method documented by the current upstream installation guide. Do not assume a CLI plugin command is available in every Codex surface.

## Alternative: direct MCP registration

Prerequisites: a supported Node.js runtime and npm. Current upstream documentation lists Node.js 22.x (>=22.23.4), 24.x (>=24.22.1), or 26.12.1+.

From a trusted directory outside the OperaLab repository, preview the scoped Codex setup:

```bash
npx -y rea-agents@latest setup --client codex --skill=false --dry-run --json
```

Review the proposed destination and changes. If they target the intended Codex profile, apply the same scoped setup:

```bash
npx -y rea-agents@latest setup --client codex --skill=false
```

The `--skill=false` flag avoids installing a second copy of workflow instructions because OperaLab already has its own project-specific skill. Do not use `--all-detected` for this project-specific setup.

For direct setup-owned registrations, the doctor command can check the local registration and prerequisites:

```bash
npx -y rea-agents@latest doctor --client codex --json
```

Important: `doctor` does not prove that the currently running agent session has loaded the tools. Restart/reconnect Codex and confirm the live tool catalog. Plugin-owned state is not visible to `rea doctor --client codex`; use `codex plugin list` and the live MCP tool list for the plugin route.

## Other agents and skill-only installation

For another agent, follow the official setup guide and select only the actual client in use. Do not guess a client identifier or manually edit a global configuration file without first reading the current client configuration guide.

To install only upstream instructions without MCP registration:

```bash
npx skills add morluto/rea --skill reverse-engineer-anything
```

This does not register the MCP server or install analysis engines.

## Updating an existing REA installation

Use the update path that matches how REA was installed; do not mix installation owners.

- Global npm/bun CLI: run `rea update`, then follow the setup command printed by the updater to refresh the agent registration and bundled skill.
- npx-based setup: run `npx -y rea-agents@latest setup`, review the proposed configuration changes, and apply only the intended client changes.
- Codex Marketplace plugin: update the plugin through the supported Codex plugin/marketplace flow; do not also create a second setup-owned REA registration.
- After updating, restart/reconnect the agent and verify the live tool catalog. A successful package update or GitHub Skill commit alone does not prove that the active MCP session loaded the new tools.
- Keep backups and preserve unrelated MCP servers, approval settings, and execution boundaries. Do not run setup repeatedly as a daily check; first compare the installed/upstream versions and repair only an observed mismatch.

For this project, the daily maintenance review checks upstream releases and documentation. It can update the GitHub project Skill, but it cannot remotely update the user's local Codex runtime or restart the local agent.

## Provider requirements

- Static JavaScript/Electron analysis and passive capture inspection can work without a native decompiler.
- Native decompilation and some Android/firmware workflows require separately installed providers or tools.
- REA setup does not automatically install or upgrade Node.js, npm, Java, Ghidra, IDA, JADX, Hopper, Binwalk, or Unblob.
- Install optional providers only when the selected task requires them and after reviewing the installation plan.
- REA analyzes targets locally, but investigation results are returned to the connected agent; consider the model provider's data policy before analyzing confidential material.

## Recovery

1. If REA tools are missing in the active session, determine whether the plugin or setup-owned MCP registration exists.
2. If a plugin is installed but tools are absent, inspect the plugin launch error and restart/reconnect the client.
3. If a setup-owned registration is aligned but the current session has no tools, restart/reconnect the agent.
4. If setup or launch failed, read the current official connection/recovery guide and use the exact remediation for the observed error.
5. Do not repeatedly run setup, install unrelated providers, disable the client's sandbox, or broaden permissions as a generic fix.
6. Keep client configuration backups and preserve unrelated MCP servers and approval settings.

## Current project integration status

- Project skill: committed under `.agents/skills/rea-reverse-engineering/`.
- Official MCP/plugin setup: documented here; local installation must be performed in the user's Codex environment.
- MCP runtime verification: pending until the local agent is restarted and its live tool catalog is checked.
