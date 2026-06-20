# Manifest v3 — full field reference

The manifest is `manifest.json` next to the entrypoint. Below is every field ScriptShell reads.
Required fields have no default; everything else is optional with the default shown.

## Table of contents
- Top-level fields
- runtime
- input
- output (+ nameTemplate tokens)
- args (types, options, dependsOn, validation)
- argGroups
- execution (+ command tokens)
- progress
- platform
- capabilities / llm / trust / registry
- Full examples

## Top-level fields
| Field | Type | Required | Notes |
|---|---|---|---|
| `$schema` | string | no | `"https://scriptshell.dev/schema/manifest-v3.json"` |
| `id` | string | **yes** | unique slug, e.g. `csv-merger`; usually the folder name |
| `name` | string | **yes** | display name |
| `version` | string | **yes** | semver, e.g. `1.0.0` |
| `description` | string | **yes** | one line |
| `author` | object | no | `{ "name", "url"?, "email"? }` |
| `license`, `readme`, `icon`, `repository` | string | no | metadata |
| `tags` | string[] | no | free-text tags |
| `capabilities` | object | no | `{ actions[], domains[], keywords[] }` — powers search |
| `llm` | object | no | `{ toolDescription?, usageHint?, examplePrompts[] }` for agents |
| `trust` | object | no | `{ permissions[], network, systemCommands[], checksum? }` |
| `runtime` | object | **yes** | see below |
| `input` | object | **yes** | see below |
| `output` | object | **yes** | see below |
| `args` | array | no | form fields |
| `argGroups` | array | no | grouping/collapsing of args |
| `execution` | object | **yes** | command + timeout + env |
| `progress` | object | no | progress parsing (`percent` regex or `structured` sentinel) |
| `stages` | array | no | pipeline steps shown as a list; `[{ id, label, weight? }]` |
| `platform` | object | no | `{ os[], arch[] }` gating |
| `registry` | object | no | registry metadata (category, featured, …) |

## runtime
```json
"runtime": {
  "engine": "python",            // python | node | deno | ruby | bash
  "minVersion": "3.8",           // optional
  "entrypoint": "script.py",     // file in the script folder
  "dependencies": {              // optional
    "manager": "pip",            // pip | npm | bundler | …
    "file": "requirements.txt",  // dependency manifest in the folder
    "isolated": true             // default true — install into an isolated env (venv etc.)
  }
}
```

## input
```json
"input": {
  "mode": "multiple",            // none | single | multiple | directory
  "minFiles": 1,                 // default 1
  "maxFiles": 500,               // default 1000
  "accept": [".csv", ".tsv"],    // default ["*"] (any). Lowercase extensions with dot.
  "maxSizeMB": 50,               // optional per-file cap
  "description": "…",            // optional
  "dragDropLabel": "Drop CSV files here"  // optional UI hint
}
```
- `single` → exactly one file. `multiple` → minFiles..maxFiles. `directory` → one folder.
  `none` → no input files.

## output
```json
"output": {
  "mode": "file",                // none | file | files | directory
  "nameTemplate": "merged_{{timestamp}}.csv",
  "extensions": [".csv"],        // optional, advisory
  "preview": { "type": "table", "maxRows": 100, "maxSizeMB": 5 },
  "schema": { "type": "…", "description": "…" }  // optional, for structured output
}
```
- ScriptShell resolves `nameTemplate` → the full output path → passes it as `{{output}}`.
  Your script must write exactly there. For `directory` mode, `{{output}}` is a folder you create
  and fill.
- **nameTemplate tokens (resolved at run time):** `{{timestamp}}` (YYYYMMDD_HHMMSS),
  `{{date}}` (YYYY-MM-DD), `{{input_name}}` (first input stem), `{{input_ext}}`,
  `{{script_id}}`, `{{script_name}}`.
- `preview.type`: `table` | `json` | `image` | `markdown` | `text` | … (drives the result viewer).

## args (form fields)
Each arg renders a control and is available in the command as `{{args.<id>}}`.
```json
{
  "id": "delimiter",            // required; used as {{args.delimiter}}
  "type": "select",             // string|number|boolean|select|textarea|file
  "label": "Delimiter",         // required; shown in the form
  "description": "…",           // optional helper text
  "default": ",",               // optional default value
  "required": true,             // default false
  "group": "advanced",          // optional; must match an argGroups id
  "placeholder": "…",           // string/number/textarea
  "llmHint": "…",               // hint for agents filling the form
  "options": [                   // for select
    { "value": ",", "label": "Comma (,)" },
    { "value": ";", "label": "Semicolon (;)" }
  ],
  "min": 1, "max": 100, "step": 1, "slider": true,   // number
  "rows": 6,                     // textarea
  "accept": [".csv"],            // file-type arg
  "dependsOn": { "arg": "mode", "value": "prettify", "operator": "eq" }, // show only when…
  "validation": { "pattern": "^\\d+$", "message": "digits only", "minLength": 1, "maxLength": 20 }
}
```
- **arg `type`s:** `string`, `number` (supports min/max/step/slider), `boolean`,
  `select` (needs `options`), `textarea` (supports `rows`), `file`.
- **Booleans in commands:** pass them through (e.g. `--sort-keys {{args.sort_keys}}` → `true`/`false`)
  and parse the string in your script, OR gate a flag with Handlebars:
  `{{#if args.sort_keys}}--sort-keys{{/if}}`.
- `dependsOn.operator`: `eq` (default) and similar — hides the field unless the condition holds.

## argGroups
```json
"argGroups": [
  { "id": "dimensions", "label": "Dimensions", "collapsed": false },
  { "id": "advanced",   "label": "Advanced",   "collapsed": true }
]
```
Args reference a group via `"group": "<id>"`.

## execution
```json
"execution": {
  "command": "{{runtime}} {{entrypoint}} --input {{inputFiles}} --output {{output}} --delimiter {{args.delimiter}}",
  "timeout": 300,            // seconds; 0 = use app default
  "workingDir": "script",   // script | input | output | temp
  "env": { "PYTHONUNBUFFERED": "1" }
}
```
Command tokens: `{{runtime}}`, `{{entrypoint}}`, `{{input}}` (first file), `{{inputFiles}}` (all),
`{{output}}`, `{{tempDir}}`, `{{args.<id>}}`. Handlebars conditionals/blocks are supported. Paths
are auto-quoted; don't add your own quotes around tokens.

## progress
Two modes.

**`percent` (simple regex):**
```json
"progress": { "type": "percent", "pattern": "^PROGRESS:(\\d+)$" }
```
The regex must have one capture group with the percent. Your script prints `PROGRESS:NN` to stdout.

**`structured` (sentinel — for multi-step scripts):**
```json
"progress": { "type": "structured" }
```
Your script emits JSON sentinel lines on stdout, each prefixed with `@@scriptshell `:
```
@@scriptshell {"progress": 42}
@@scriptshell {"stage": "resize", "progress": 10, "message": "image 3/10"}
@@scriptshell {"stage": "resize", "status": "done"}
@@scriptshell {"message": "warming up", "indeterminate": true}
```
Fields (all optional): `progress` (0–100), `stage` (a `stages[].id`), `status` (`start`|`done`),
`message`, `indeterminate`. Non-sentinel stdout lines stream to the log panel.

## stages
Optional. Declares the pipeline steps so the app renders a step list and computes overall progress
from per-stage weights. Pair with `progress.type = "structured"` and emit `stage`/`status` events.
```json
"stages": [
  { "id": "load",   "label": "Loading",  "weight": 1 },
  { "id": "resize", "label": "Resizing", "weight": 3 },
  { "id": "save",   "label": "Saving",   "weight": 1 }
]
```
`weight` defaults to `1`. Overall percent = weighted sum of completed stages + the current stage's
progress fraction.

## platform
```json
"platform": { "os": ["windows", "macos", "linux"], "arch": ["x64", "arm64"] }
```
Empty/absent = all platforms. ScriptShell hides/marks incompatible scripts.

## capabilities / llm / trust / registry
- `capabilities`: `{ "actions": [...], "domains": [...], "keywords": [...] }` — drives search and
  MCP capability matching. Use the taxonomy in `registry.md`.
- `llm`: `{ "toolDescription", "usageHint", "examplePrompts": [...] }` — improves how agents pick
  and fill the tool.
- `trust`: `{ "permissions": [...], "network": false, "systemCommands": [...], "checksum"? }` —
  declares what the script needs; ScriptShell asks the user to trust before first run.
- `registry`: `{ "category", "featured", "downloads", "rating", "ratingCount", "verified",
  "publishedAt", "updatedAt" }` — usually filled by the registry, not the author.

## Full examples

### JSON Formatter (single input → single file, dependent arg)
```json
{
  "$schema": "https://scriptshell.dev/schema/manifest-v3.json",
  "id": "json-formatter", "name": "JSON Formatter", "version": "1.0.0",
  "description": "Prettify, minify, or validate JSON files",
  "tags": ["json", "format", "validate"],
  "capabilities": { "actions": ["format","validate","transform"], "domains": ["json"], "keywords": ["prettify json","minify json"] },
  "runtime": { "engine": "python", "minVersion": "3.8", "entrypoint": "script.py" },
  "input": { "mode": "single", "accept": [".json"], "maxSizeMB": 100, "dragDropLabel": "Drop a JSON file" },
  "output": { "mode": "file", "nameTemplate": "{{input_name}}_formatted.json", "extensions": [".json"], "preview": { "type": "json" } },
  "args": [
    { "id": "mode", "type": "select", "label": "Mode", "default": "prettify", "required": true,
      "options": [ { "value": "prettify", "label": "Prettify" }, { "value": "minify", "label": "Minify" }, { "value": "validate", "label": "Validate only" } ] },
    { "id": "indent", "type": "number", "label": "Indent spaces", "default": 2, "min": 1, "max": 8, "dependsOn": { "arg": "mode", "value": "prettify" } },
    { "id": "sort_keys", "type": "boolean", "label": "Sort keys alphabetically", "default": false }
  ],
  "execution": { "command": "{{runtime}} {{entrypoint}} --input {{input}} --output {{output}} --mode {{args.mode}} --indent {{args.indent}} --sort-keys {{args.sort_keys}}", "timeout": 60, "workingDir": "script" },
  "progress": { "type": "percent", "pattern": "^PROGRESS:(\\d+)$" },
  "platform": { "os": ["windows", "macos"], "arch": ["x64", "arm64"] }
}
```

### Image Resizer (multiple inputs → directory, dependencies, argGroups, slider)
```json
{
  "$schema": "https://scriptshell.dev/schema/manifest-v3.json",
  "id": "image-resizer", "name": "Image Resizer", "version": "1.0.0",
  "description": "Resize images to specified dimensions with quality control",
  "capabilities": { "actions": ["resize","scale"], "domains": ["image"], "keywords": ["batch resize"] },
  "runtime": { "engine": "python", "minVersion": "3.9", "entrypoint": "script.py",
    "dependencies": { "manager": "pip", "file": "requirements.txt", "isolated": true } },
  "input": { "mode": "multiple", "minFiles": 1, "maxFiles": 500, "accept": [".jpg",".jpeg",".png",".webp"], "maxSizeMB": 50 },
  "output": { "mode": "directory", "nameTemplate": "resized_{{timestamp}}", "preview": { "type": "image" } },
  "args": [
    { "id": "width", "type": "number", "label": "Width (px)", "default": 1920, "min": 1, "max": 10000, "required": true, "group": "dimensions" },
    { "id": "quality", "type": "number", "label": "Quality", "default": 85, "min": 1, "max": 100, "slider": true, "group": "output" }
  ],
  "argGroups": [ { "id": "dimensions", "label": "Dimensions" }, { "id": "output", "label": "Output Settings" } ],
  "execution": { "command": "{{runtime}} {{entrypoint}} --input {{inputFiles}} --output {{output}} --width {{args.width}} --quality {{args.quality}}", "timeout": 600 },
  "progress": { "type": "percent", "pattern": "^PROGRESS:(\\d+)$" },
  "platform": { "os": ["windows", "macos"], "arch": ["x64", "arm64"] }
}
```
