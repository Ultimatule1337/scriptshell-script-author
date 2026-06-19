# scriptshell-script-author

A Claude Code **plugin** that ships the `scriptshell-script-author` **skill** — it teaches any
model to author or adapt scripts for the [ScriptShell](https://github.com/Ultimatule1337/scriptshell)
desktop app: produce a manifest v3 (`manifest.json`) + entrypoint, validate it with the
`scriptshell` CLI / MCP, use the registry (search/install/run), and publish new scripts.

## What's inside
```
skills/scriptshell-script-author/
  SKILL.md                 # the skill (loaded when it triggers)
  references/
    manifest.md            # full manifest v3 field reference + examples
    engines.md             # per-engine command/env/deps + entrypoint skeletons
    registry.md            # packaging, index.json schema, capabilities taxonomy
  examples/
    csv-merger.manifest.json
    csv-merger.script.py
.claude-plugin/
  plugin.json              # plugin manifest
  marketplace.json         # marketplace listing (this repo lists itself)
```

## Install (Claude Code)
This repo is both a plugin and a single-plugin marketplace, so you can add it directly:

```
/plugin marketplace add Ultimatule1337/scriptshell-script-author
/plugin install scriptshell-script-author@scriptshell
```

> Plugin/marketplace manifest fields can evolve — if install fails, check the current Claude Code
> plugin docs and adjust `.claude-plugin/plugin.json` / `marketplace.json` accordingly.

**Fallback (no plugin/marketplace):** copy `skills/scriptshell-script-author/` into your
`~/.claude/skills/` (or a project's `.claude/skills/`).

## When it triggers
Whenever you ask Claude to make a script runnable in ScriptShell, write/edit a ScriptShell
`manifest.json`, adapt an existing Python/Node/Bash/Ruby/Deno script to ScriptShell, validate or
scaffold a manifest, or work with the `scriptshell` CLI / scriptshell-mcp tools.

## Related
- ScriptShell app: https://github.com/Ultimatule1337/scriptshell
- ScriptShell registry: https://github.com/Ultimatule1337/scriptshell-registry (the skill's
  `references/registry.md` documents the publishing format).

## License
MIT — see [LICENSE](LICENSE).
