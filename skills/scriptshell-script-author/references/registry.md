# Packaging & publishing to a ScriptShell registry

A ScriptShell registry is a **static catalog**: an `index.json` listing scripts, plus a **zip per
script**. The desktop app fetches `index.json`, lets the user search/filter (client-side), and on
Install downloads the script's `download_url` (zip) and extracts it into the library.

## Packaging a script (the zip)
- Zip the **contents** of the script folder so that `manifest.json` and the entrypoint are at the
  **root of the archive** — NOT inside a nested `<id>/` folder. ScriptShell extracts the archive
  and imports the resulting directory directly.
- Include everything the script needs: `manifest.json`, the entrypoint, and any
  `requirements.txt` / `package.json` / `Gemfile`, plus optional `README.md`.
- Name it `<id>-<version>.zip` (e.g. `csv-merger-1.1.0.zip`).

## `index.json` schema (must match the app exactly)
```jsonc
{
  "version": 1,                       // index format version (integer)
  "updated_at": "2026-06-19T12:00:00Z",
  "scripts": [
    {
      "id": "csv-merger",             // required
      "name": "CSV Merger",           // required
      "version": "1.1.0",             // required
      "description": "Merge multiple CSV files into one", // required
      "engine": "python",             // required
      "author": "you",
      "tags": ["csv", "merge"],
      "input_accept": [".csv", ".tsv"],
      "capabilities": { "actions": ["merge"], "domains": ["csv"], "keywords": ["combine"] },
      "category": "data",
      "platforms": ["windows", "macos", "linux"],
      "repository": "https://github.com/Ultimatule1337/scriptshell-registry",
      "download_url": "https://raw.githubusercontent.com/Ultimatule1337/scriptshell-registry/main/packages/csv-merger-1.1.0.zip",
      "manifest_url": "https://raw.githubusercontent.com/Ultimatule1337/scriptshell-registry/main/scripts/csv-merger/manifest.json",
      "published_at": "2026-06-19T12:00:00Z",
      "updated_at": "2026-06-19T12:00:00Z",
      "size_bytes": 2048,
      "downloads": 0, "rating": 0, "rating_count": 0, "verified": false
    }
  ]
}
```
Field names are **snake_case**. Required per entry: `id, name, version, description, engine`. The
rest are optional but `download_url`, `manifest_url`, `engine`, `input_accept`, `capabilities`,
`size_bytes`, and `platforms` make search and install work well. Map them from the manifest:
`engine`←`runtime.engine`, `input_accept`←`input.accept`, `capabilities`←`capabilities`,
`platforms`←`platform.os`.

## Capabilities taxonomy (keep it controlled)
Use a small, shared vocabulary so capability search works across scripts:
- **actions:** `convert, merge, split, compress, extract, resize, transform, validate, generate,
  format, rename, analyze`.
- **domains:** `csv, json, image, pdf, text, archive, audio, video, markdown, html, code`.
- **keywords:** free-text synonyms to aid fuzzy search.
Pick the closest existing values; only add new ones deliberately.

## Hosting (recommended: static GitHub repo)
- Repo `scriptshell-registry` with `scripts/<id>/` (source of truth), generated `packages/*.zip`,
  and generated `index.json` at the root.
- A small generator (e.g. `tools/build_registry.py`) scans `scripts/`, validates each manifest
  (`scriptshell validate`), zips each folder's contents, computes `size_bytes`, and writes
  `index.json` with `download_url`/`manifest_url` built from the repo's raw URL.
- CI validates manifests on PRs and regenerates the index on merge.
- The app's `registry_url` points at the raw `index.json`. For scale, move zips to GitHub Releases
  and set `download_url` to the release-asset URL.

## Validate before publishing
Always run `scriptshell validate scripts/<id>/manifest.json` (or MCP `validate_manifest`) and fix
all errors before adding a script to `index.json`. A registry of invalid manifests installs broken
tools.
