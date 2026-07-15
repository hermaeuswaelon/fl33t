#!/usr/bin/env python3
"""
forge-memory — CLI for ARES Forge Memory Vault
================================================
Usage:
  forge-memory store --category <cat> --key <key> [--content <json>|--file <path>] [--tags "#tag1 #tag2"]
  forge-memory search <query> [--category <cat>] [--tags <tag>]
  forge-memory get --key <key>
  forge-memory list --category <cat>
  forge-memory delete --key <key>
  forge-memory purge --older-than <days> [--category <prefix>]
  forge-memory stats
  forge-memory tags
"""

import os, sys, json, argparse

# Find the forge_vault module alongside this script
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from forge_vault import ForgeVault

vault = ForgeVault()


def cmd_store(args):
    if args.file:
        with open(args.file) as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        content = sys.stdin.read()
    result = vault.store(args.key, content, category=args.category or "general",
                         tags=args.tags or "", priority=args.priority or 5,
                         ttl=args.ttl or 604800)
    print(f"Stored: {result['key']} ({result['category']})")


def cmd_search(args):
    results = vault.search(args.query, category=args.category, tags=args.tags,
                           limit=args.limit or 10)
    if args.format == "json":
        print(json.dumps(results, indent=2, default=str))
        return
    for r in results:
        preview = r["value"][:200].replace("\n", " ")
        print(f"[{r['category']}] {r['key']} ({r['updated_at']})")
        print(f"  Tags: {r['tags']} | Priority: {r['priority']}")
        print(f"  {preview}\n")


def cmd_get(args):
    entry = vault.get(args.key)
    if not entry:
        print("Not found or expired", file=sys.stderr)
        sys.exit(1)
    if args.format == "json":
        print(json.dumps(entry, indent=2, default=str))
        return
    print(f"Key: {entry['key']}")
    print(f"Category: {entry['category']}")
    print(f"Tags: {entry['tags']}")
    print(f"Priority: {entry['priority']}")
    print(f"Created: {entry['created_at']}")
    print(f"Updated: {entry['updated_at']}")
    print(f"Access: {entry['access_count']}")
    print("---")
    print(entry["value"])


def cmd_list(args):
    entries = vault.list_by_category(args.category or "general", limit=args.limit or 20)
    for e in entries:
        print(f"[{e['category']}] {e['key']} — {e['updated_at']} — [{e['tags']}]")


def cmd_delete(args):
    if vault.delete(args.key):
        print(f"Deleted: {args.key}")
    else:
        print(f"Not found: {args.key}", file=sys.stderr)
        sys.exit(1)


def cmd_purge(args):
    n = vault.purge(category_prefix=args.category or "", older_than_days=args.older_than or 30)
    print(f"Purged {n} entries")


def cmd_stats(args):
    s = vault.stats()
    if args.format == "json":
        print(json.dumps(s, indent=2, default=str))
        return
    print(f"Total entries: {s['total_entries']}")
    print(f"DB size: {s['db_size_bytes'] // 1024}KB")
    print(f"Date range: {s['oldest']} → {s['newest']}")
    print("\nBy category:")
    for c in s['by_category']:
        print(f"  {c['category']}: {c['cnt']}")
    if s['top_tags']:
        print("\nTop tags:")
        for t in s['top_tags']:
            print(f"  {t['tags']}: {t['cnt']}")


def cmd_tags(args):
    for tag in vault.list_tags():
        print(tag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARES Forge Memory Vault CLI")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    sub = parser.add_subparsers(dest="command", required=True)

    p_store = sub.add_parser("store")
    p_store.add_argument("--category", "-c", default="general")
    p_store.add_argument("--key", "-k", required=True)
    p_store.add_argument("--content", "-v")
    p_store.add_argument("--file", "-f")
    p_store.add_argument("--tags", "-t", default="")
    p_store.add_argument("--priority", "-p", type=int, default=5)
    p_store.add_argument("--ttl", type=int, default=604800)

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--category", "-c")
    p_search.add_argument("--tags", "-t")
    p_search.add_argument("--limit", "-l", type=int, default=10)

    p_get = sub.add_parser("get")
    p_get.add_argument("--key", "-k", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--category", "-c", default="general")
    p_list.add_argument("--limit", "-l", type=int, default=20)

    p_del = sub.add_parser("delete")
    p_del.add_argument("--key", "-k", required=True)

    p_purge = sub.add_parser("purge")
    p_purge.add_argument("--older-than", type=int, default=30)
    p_purge.add_argument("--category", "-c", default="")

    p_stats = sub.add_parser("stats")
    p_tags = sub.add_parser("tags")

    args = parser.parse_args()
    commands = {
        "store": cmd_store, "search": cmd_search, "get": cmd_get,
        "list": cmd_list, "delete": cmd_delete, "purge": cmd_purge,
        "stats": cmd_stats, "tags": cmd_tags,
    }
    commands[args.command](args)
