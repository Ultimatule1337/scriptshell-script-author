#!/usr/bin/env python3
"""Reference ScriptShell entrypoint: merge multiple CSV files into one.

Demonstrates the contract:
- reads --input (many), --output (one), and form args (--delimiter, --has-header)
- prints PROGRESS:<n> to stdout, human logs to stderr
- writes exactly to --output, exits 0 on success
"""
import argparse
import csv
import os
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", nargs="+", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--delimiter", default=",")
    p.add_argument("--has-header", default="true")
    args = p.parse_args()

    has_header = args.has_header.lower() not in ("false", "0", "no")
    files = args.input
    total = len(files)

    rows_out = []
    header = None

    for i, fp in enumerate(files):
        print(f"Processing: {os.path.basename(fp)}", file=sys.stderr)
        with open(fp, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f, delimiter=args.delimiter))
        if rows:
            if has_header:
                if header is None:
                    header = rows[0]
                rows_out.extend(rows[1:])
            else:
                rows_out.extend(rows)
        print(f"PROGRESS:{int((i + 1) / total * 100)}", flush=True)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=args.delimiter)
        if header:
            w.writerow(header)
        w.writerows(rows_out)

    print(f"Done. Wrote {len(rows_out)} rows.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
