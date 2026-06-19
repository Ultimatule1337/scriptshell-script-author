---
name: scriptshell-script-author
description: >-
  Author or adapt a script so the ScriptShell desktop app can run it — produce a manifest v3
  (manifest.json) plus an entrypoint, validate it, and optionally publish it to a ScriptShell
  registry. Use this whenever the user mentions ScriptShell, asks to "make a script runnable in
  ScriptShell", "package/convert my script for ScriptShell", create or edit a ScriptShell
  manifest.json, add a tool to the ScriptShell library or registry, or adapt an existing
  Python / Node / Deno / Ruby / Bash script into ScriptShell's drop-files-and-run format. Also
  use when validating or scaffolding a ScriptShell manifest, or when working with the
  `scriptshell` CLI or the scriptshell-mcp tools (search_scripts, run_script, validate_manifest,
  scaffold_script). Prefer this skill even if the user doesn't say "manifest" — any request to
  turn a file-processing script into a no-code ScriptShell tool belongs here.
---

# ScriptShell Script Author

ScriptShell is a cross-platform desktop GUI: the user drops files, picks a script, fills an
auto-generated form, and runs it. A "script" that ScriptShell can run is **a folder containing
`manifest.json` + an entrypoint** (e.g. `script.py`). The manifest declares the runtime, the
inputs it accepts, the output it produces, the form fields (args), and the command line to run.
ScriptShell renders the form, resolves the command, executes it, streams logs/progress, and
previews the result.

Your job with this skill: take a task (or an existing raw script) and produce a **valid manifest
v3 + a matching entrypoint** that follows ScriptShell's contract, then validate it, and — if the
user wants — package and publish it to a registry.

## Workflow

1. **Clarify the task** — what files go in (one? many? a folder?), what comes out (one file? a
   directory? in-place?), and what options the user should control (the form fields/args).
2. **Pick the engine** — python, node, deno, ruby, or bash. Match the user's existing script or
   the easiest fit. See `references/engines.md`.
3. **Write the entrypoint** — a normal CLI program that reads `--flags`, processes input files,
   writes the output path it's given, prints progress to stdout and logs to stderr, and exits 0
   on success / non-zero on failure. Skeletons per engine in `references/engines.md`.
4. **Write `manifest.json`** — declare runtime, input, output, args, and the `execution.command`
   template that wires the args/paths to your CLI. Full field reference: `references/manifest.md`.
5. **Validate** — `scriptshell validate path/to/manifest.json` (CLI) or the MCP `validate_manifest`
   tool. Fix every reported error. You can also bootstrap a draft with `scriptshell scaffold` /
   MCP `scaffold_script`.
6. **Test** — install the folder (`scriptshell install <folder>`) and run it
   (`scriptshell run <id> -i <files> --arg key=value`), or run it in the desktop app.
7. **Publish (optional)** — package and add it to a registry. See `references/registry.md`.

Keep the entrypoint and manifest in **one folder**; the folder name usually matches the manifest
`id`. When packaged for a registry the zip must contain `manifest.json` + entrypoint **at the
archive root** (no nested folder).

## The execution model (how your command actually runs)

ScriptShell renders `execution.command` as a **Handlebars template**, splits it into a real
argv (respecting quotes), and runs `program args…`. Path tokens are auto-quoted, so paths with
spaces are safe. Available tokens:

| Token | Expands to |
|---|---|
| `{{runtime}}` | the resolved interpreter path (python/node/…); for `bash` it's the shell |
| `{{entrypoint}}` | absolute path to your entrypoint file |
| `{{input}}` | the **first** input file (quoted) |
| `{{inputFiles}}` | **all** input files, each quoted, space-joined |
| `{{output}}` | the resolved output path (quoted) |
| `{{tempDir}}` | a per-run temp directory (quoted) |
| `{{args.<id>}}` | the value of arg `<id>` from the form |

Handlebars conditionals work, e.g. `{{#if args.verbose}}--verbose{{/if}}`. ScriptShell also injects
env vars: `SCRIPTSHELL=1`, `SCRIPTSHELL_VERSION`, `SCRIPTSHELL_INPUT_COUNT`, plus any
`execution.env`. `execution.workingDir` may be `script` (default), `input`, `output`, or `temp`.

**Typical command:**
`"{{runtime}} {{entrypoint}} --input {{inputFiles}} --output {{output}} --mode {{args.mode}}"`

## Input / output model

- `input.mode`: `none` | `single` | `multiple` | `directory`. Constrain with `minFiles`,
  `maxFiles`, `accept` (e.g. `[".csv", ".tsv"]`, or `["*"]` for anything), `maxSizeMB`.
- `output.mode`: `none` | `file` | `files` | `directory`. For `file`/`directory`, set
  `nameTemplate` — ScriptShell computes the output path and passes it as `{{output}}`. Your
  script must write exactly there.
- **`nameTemplate` tokens (resolved at run time):** `{{timestamp}}`, `{{date}}`, `{{input_name}}`
  (first input's stem), `{{input_ext}}`, `{{script_id}}`, `{{script_name}}`. Use `{{timestamp}}`
  for batch outputs so names don't collide, e.g. `"merged_{{timestamp}}.csv"`.

## Progress & logging conventions

- **Progress:** print lines `PROGRESS:<n>` (0–100) to **stdout**; declare it in the manifest:
  `"progress": { "type": "percent", "pattern": "^PROGRESS:(\\d+)$" }`. Flush after each line.
- **Logs:** write human-readable messages to **stderr** (or stdout lines that don't match the
  progress pattern) — they stream into the ScriptShell log panel.
- **Exit code:** `0` = success; non-zero = failure (the last log line becomes the error message).
- On Windows, avoid relying on a trailing `\r`; ScriptShell trims it before progress parsing, but
  keep progress lines exactly `PROGRESS:NN`.

## Validate & scaffold (don't hand-wave the contract)

- `scriptshell validate manifest.json` — parses against the v3 contract and lists field errors.
  Always run it before declaring done. (MCP equivalent: `validate_manifest`.)
- `scriptshell scaffold` / MCP `scaffold_script` — generate a starter manifest + entrypoint from a
  short description (engine, name, input/output, args). Use it to bootstrap, then refine.

## Using an existing registry (search / install / run)

If the user wants to **find or reuse** scripts rather than author one, use the registry via MCP or
CLI instead of writing from scratch:

- MCP tools: `search_scripts` (query/action/domain/file_extensions), `get_script_details`,
  `install_script`, `run_script`, `list_installed_scripts`.
- CLI: `scriptshell search <q> [--action <a>] [--domain <d>]`, `scriptshell info <id>`,
  `scriptshell install <id|zip|folder|git>`, `scriptshell run <id> -i <files> --arg k=v`.

Search by **capability** (`action` + `domain`, e.g. action=`merge` domain=`csv`) when the user
describes intent rather than a name.

## Publishing to a registry

A ScriptShell registry is a static index (`index.json`) + zip packages. To publish your script:
package the folder (zip with `manifest.json` at the root) and add an `index.json` entry with its
`capabilities` (actions/domains/keywords). Full packaging format, the `index.json` schema, and the
capabilities taxonomy are in `references/registry.md`.

## Minimal end-to-end example

A single-file JSON prettifier (`json-prettify/`):

`manifest.json`
```json
{
  "$schema": "https://scriptshell.dev/schema/manifest-v3.json",
  "id": "json-prettify", "name": "JSON Prettify", "version": "1.0.0",
  "description": "Pretty-print a JSON file",
  "capabilities": { "actions": ["format"], "domains": ["json"], "keywords": ["prettify json"] },
  "runtime": { "engine": "python", "minVersion": "3.8", "entrypoint": "script.py" },
  "input": { "mode": "single", "accept": [".json"] },
  "output": { "mode": "file", "nameTemplate": "{{input_name}}_pretty.json", "preview": { "type": "json" } },
  "args": [ { "id": "indent", "type": "number", "label": "Indent", "default": 2, "min": 1, "max": 8 } ],
  "execution": { "command": "{{runtime}} {{entrypoint}} --input {{input}} --output {{output}} --indent {{args.indent}}", "timeout": 60 },
  "progress": { "type": "percent", "pattern": "^PROGRESS:(\\d+)$" }
}
```

`script.py`
```python
#!/usr/bin/env python3
import argparse, json, sys
p = argparse.ArgumentParser()
p.add_argument("--input", required=True); p.add_argument("--output", required=True)
p.add_argument("--indent", type=int, default=2)
a = p.parse_args()
print("Reading input…", file=sys.stderr)
with open(a.input, encoding="utf-8") as f: data = json.load(f)
print("PROGRESS:50", flush=True)
with open(a.output, "w", encoding="utf-8") as f: json.dump(data, f, indent=a.indent, ensure_ascii=False)
print("PROGRESS:100", flush=True)
print("Done.", file=sys.stderr)
```

A complete, real multi-file example (CSV merger) is in `examples/csv-merger.manifest.json` +
`examples/csv-merger.script.py`.

## References (read when you need depth)
- `references/manifest.md` — every manifest v3 field, arg types, validation, argGroups, progress,
  platform, trust, capabilities, llm — with two full example manifests.
- `references/engines.md` — per-engine command/env/dependencies + entrypoint skeletons.
- `references/registry.md` — packaging, `index.json` schema, capabilities taxonomy, publishing.
