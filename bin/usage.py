#!/usr/bin/env python3
"""Show where Claude Code usage went on this machine.

Reads the session transcripts Claude Code keeps under ~/.claude/projects and
reports, for the last N days: the share of each model, main sessions versus
subagents, how much came from large contexts, and which projects cost most.
Nothing leaves the machine.

  bin/usage.py                 # last 7 days
  bin/usage.py --days 14
  bin/usage.py --prices my-prices.json

The dollar figures are an estimate at list prices, useful for comparing shares
and for before/after comparisons. They are not what a subscription charges, and
the prices below go stale: edit PRICES or pass --prices.
Runs on Windows, macOS and Linux; needs only Python 3.9+.
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
import time
from pathlib import Path

# USD per million tokens (input, output), matched by substring of the model id.
# Edit these to current list prices.
PRICES = {"fable": (8.0, 40.0), "opus": (4.0, 20.0), "sonnet": (2.0, 10.0), "haiku": (0.1, 0.5)}
CACHE_READ, CACHE_WRITE = 0.1, 1.25  # multipliers on the input price

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def family(model: str, prices: dict) -> str | None:
    for name in prices:
        if name in (model or ""):
            return name
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--projects-dir", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--prices", help='JSON file: {"opus": [4, 20], ...}')
    args = ap.parse_args()

    prices = dict(PRICES)
    if args.prices:
        prices = {k: tuple(v) for k, v in json.loads(Path(args.prices).read_text(encoding="utf-8")).items()}
    root = Path(args.projects_dir)
    if not root.is_dir():
        sys.exit(f"ERROR: {root} does not exist")
    since = time.time() - args.days * 86400
    since_day = time.strftime("%Y-%m-%d", time.gmtime(since))

    rows = collections.defaultdict(collections.Counter)
    by_project, by_context = collections.Counter(), collections.Counter()
    subagents: dict[str, dict] = {}
    seen, unpriced = set(), collections.Counter()

    for file in root.rglob("*.jsonl"):
        try:
            if file.stat().st_mtime < since:
                continue
            handle = open(file, encoding="utf-8", errors="replace")
        except OSError:
            continue
        in_subagent_file = "subagents" in file.parts or file.name.startswith("agent-")
        project = file.relative_to(root).parts[0]
        with handle:
            for line in handle:
                if '"usage"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if (entry.get("timestamp") or "")[:10] < since_day:
                    continue
                message = entry.get("message") or {}
                usage = message.get("usage")
                if not usage:
                    continue
                key = (message.get("id"), entry.get("requestId"))
                if key in seen:
                    continue
                seen.add(key)
                model = message.get("model") or "?"
                fam = family(model, prices)
                if not fam:
                    unpriced[model] += 1
                    continue
                p_in, p_out = prices[fam]
                fresh = usage.get("input_tokens", 0)
                written = usage.get("cache_creation_input_tokens", 0)
                read = usage.get("cache_read_input_tokens", 0)
                out = usage.get("output_tokens", 0)
                parts = {"output": out * p_out, "cache read": read * p_in * CACHE_READ,
                         "cache write": written * p_in * CACHE_WRITE, "input": fresh * p_in}
                cost = sum(parts.values()) / 1e6
                side = in_subagent_file or bool(entry.get("isSidechain"))
                row = rows[(fam, "subagent" if side else "main")]
                row["cost"] += cost
                row["requests"] += 1
                for name, value in parts.items():
                    row[name] += value / 1e6
                by_project[project] += cost
                context = fresh + written + read
                by_context["over 200K" if context > 200_000 else "100-200K" if context > 100_000 else "under 100K"] += cost
                if side:
                    s = subagents.setdefault(str(file), {"requests": 0, "peak": 0, "cost": 0.0})
                    s["requests"] += 1
                    s["peak"] = max(s["peak"], context)
                    s["cost"] += cost

    total = sum(r["cost"] for r in rows.values())
    if not total:
        sys.exit(f"No usage found in the last {args.days} days under {root}")

    print(f"Last {args.days} days, list-price estimate: ${total:,.0f}\n")
    print(f"{'model':8} {'where':9} {'share':>6} {'requests':>9}   what the cost is made of")
    for (fam, where), r in sorted(rows.items(), key=lambda kv: -kv[1]["cost"]):
        made_of = ", ".join(f"{name} {100 * r[name] / r['cost']:.0f}%"
                            for name in ("cache read", "cache write", "output", "input") if r["cost"])
        print(f"{fam:8} {where:9} {100 * r['cost'] / total:5.1f}% {r['requests']:9}   {made_of}")

    print("\nBy context size of the request:")
    for name in ("under 100K", "100-200K", "over 200K"):
        print(f"  {name:11} {100 * by_context[name] / total:5.1f}%")

    print("\nTop projects (the folder Claude Code was started in):")
    for project, cost in by_project.most_common(6):
        print(f"  {100 * cost / total:5.1f}%  {project}")

    if subagents:
        requests = [s["requests"] for s in subagents.values()]
        peaks = [s["peak"] for s in subagents.values()]
        costs = sorted((s["cost"] for s in subagents.values()), reverse=True)
        print(f"\nSubagents: {len(subagents)}; median {statistics.median(requests):.0f} requests each, "
              f"median peak context {statistics.median(peaks) / 1000:.0f}K, "
              f"{sum(1 for p in peaks if p > 200_000)} went past 200K; "
              f"the 10 most expensive account for {100 * sum(costs[:10]) / sum(costs):.0f}% of subagent cost.")
    if unpriced:
        print("\nNot priced (add to PRICES):", ", ".join(f"{m} x{n}" for m, n in unpriced.most_common(5)))


if __name__ == "__main__":
    main()
