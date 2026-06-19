# Engines — command, env, dependencies, entrypoint skeletons

ScriptShell resolves `{{runtime}}` to the interpreter for the declared `runtime.engine`. Your
entrypoint is an ordinary CLI program. Common contract for every engine:
- Read inputs/options from `--flags` exactly as your `execution.command` passes them.
- Write the output to the path given as `{{output}}` (don't choose your own location).
- Print `PROGRESS:<n>` lines to **stdout**; print human logs to **stderr**.
- Exit `0` on success, non-zero on failure.
- Don't quote `{{...}}` tokens yourself — ScriptShell quotes path tokens already.

## python
- `runtime.engine: "python"`, `entrypoint: "script.py"`.
- Dependencies: `"dependencies": { "manager": "pip", "file": "requirements.txt", "isolated": true }`
  → ScriptShell installs them into an isolated venv. Keep deps minimal; prefer stdlib.
- Recommended `execution.env`: `{ "PYTHONUNBUFFERED": "1" }` so progress flushes promptly.
- Skeleton:
```python
#!/usr/bin/env python3
import argparse, sys, os

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", nargs="+", required=True)   # or a single --input
    p.add_argument("--output", required=True)
    # add one argument per manifest arg, matching the command template
    a = p.parse_args()

    files = a.input
    for i, fp in enumerate(files):
        print(f"Processing {os.path.basename(fp)}", file=sys.stderr)
        # … do work, write into a.output …
        print(f"PROGRESS:{int((i + 1) / len(files) * 100)}", flush=True)

    print("Done.", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

## node
- `runtime.engine: "node"`, `entrypoint: "script.js"` (or `.mjs`).
- Dependencies: `"dependencies": { "manager": "npm", "file": "package.json", "isolated": true }`.
- Parse `process.argv`; write with `fs`. `console.log("PROGRESS:50")` → stdout;
  `console.error("…")` → stderr.
- Skeleton:
```js
#!/usr/bin/env node
import fs from "node:fs";
const args = process.argv.slice(2);
function opt(name) { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : undefined; }
const input = opt("input"); const output = opt("output");
console.error("Reading input…");
const data = fs.readFileSync(input, "utf8");
console.log("PROGRESS:50");
fs.writeFileSync(output, data);
console.log("PROGRESS:100");
console.error("Done.");
```

## deno
- `runtime.engine: "deno"`, `entrypoint: "script.ts"`.
- The command typically needs permission flags, e.g.
  `"{{runtime}} run --allow-read --allow-write {{entrypoint}} --input {{input}} --output {{output}}"`.
- Use `Deno.args`, `Deno.readTextFile`, `Deno.writeTextFile`; `console.log`/`console.error` as above.

## ruby
- `runtime.engine: "ruby"`, `entrypoint: "script.rb"`.
- Dependencies via bundler: `"dependencies": { "manager": "bundler", "file": "Gemfile", "isolated": true }`.
- Use `OptionParser` or manual `ARGV`; `$stdout.puts "PROGRESS:50"; $stdout.flush`;
  `$stderr.puts "log"`.

## bash
- `runtime.engine: "bash"`, `entrypoint: "script.sh"`. `{{runtime}}` is the shell.
- Command: `"{{runtime}} {{entrypoint}} {{input}} {{output}}"` (positional args are simplest in bash).
- Skeleton:
```bash
#!/usr/bin/env bash
set -euo pipefail
input="$1"; output="$2"
echo "Processing $input" >&2
# … work …
echo "PROGRESS:100"
echo "Done." >&2
```

## Passing args from the form to the CLI
- Strings/numbers/selects: `--key {{args.key}}`.
- Booleans: either pass the value (`--flag {{args.flag}}` → `true`/`false`, parse in-script) or gate
  with Handlebars (`{{#if args.flag}}--flag{{/if}}`).
- Multiple inputs: `--input {{inputFiles}}` and read `nargs="+"` (python) / loop argv (node/bash).
- Single input: `--input {{input}}`.

## Output modes & writing
- `output.mode: "file"` → write the single file at `{{output}}`.
- `output.mode: "directory"` → `{{output}}` is a directory; create it (`os.makedirs(out, exist_ok=True)`)
  and write your files inside.
- `output.mode: "none"` → in-place / side effects only (e.g. a renamer that mutates inputs).
