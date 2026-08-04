#!/usr/bin/env python3
"""Search the official SAP BTP draw.io shape library for ready-to-use shape XML.

The bundled references/drawio-sap-config.json is SAP's own draw.io custom
shape library (exported from the "SAP Corporate" / "SAP BTP Graphics"
palette). It is NOT the generic draw.io shape index used by shapesearch.py,
and the shapes are NOT referenced by a simple `shape=mxgraph.sap.icon;...`
style string (that style does not exist / will not render). Each shape is
stored as a compressed, URL-encoded mxGraphModel XML blob under a `xml` key.

This script decodes that blob format (base64 -> raw DEFLATE -> URL-decode,
the exact reverse of scripts/encode_drawio_url.py's _deflate_b64) and lets
you search across ALL categories by title keyword:

  - Service/product icons  (e.g. "work zone", "hana cloud", "identity")
  - SAP product logos      (e.g. "s/4hana", "successfactors")
  - Reusable containers    (e.g. "btp basic layer", "non-sap content", "user")
  - Pre-styled connectors  (e.g. "direct one-directional", "dashed success")
  - Legend / title / description blocks

Usage:
  python3 sap_shapesearch.py "work zone"
  python3 sap_shapesearch.py "s/4hana" --category "SAP Products SAP BTP"
  python3 sap_shapesearch.py --list-categories
  python3 sap_shapesearch.py "identity authentication" --limit 5 --full
"""
import argparse
import base64
import json
import os
import re
import sys
import zlib
import urllib.parse

CONFIG = os.path.join(os.path.dirname(__file__), "..", "references", "drawio-sap-config.json")


def decode_shape_xml(xml_b64):
    raw = base64.b64decode(xml_b64)
    inflated = zlib.decompress(raw, -zlib.MAX_WBITS)
    return urllib.parse.unquote(inflated.decode("utf-8"))


def load_entries():
    with open(CONFIG, "r", encoding="utf-8") as f:
        data = json.load(f)
    entries = []
    for lib in data.get("libraries", []):
        for sub in lib.get("entries", []):
            for l in sub.get("libs", []):
                cat = l.get("title", {}).get("main", "?")
                for e in l.get("data", []):
                    title = e.get("title")
                    if not title or title == "?":
                        continue
                    entries.append({"category": cat, "title": title, "xml": e["xml"],
                                     "w": e.get("w"), "h": e.get("h")})
    return entries


def normalize(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def search(entries, query, category=None, limit=10):
    terms = normalize(query).split()
    results = []
    for e in entries:
        if category and category.lower() not in e["category"].lower():
            continue
        hay = normalize(e["title"] + " " + e["category"])
        if all(t in hay for t in terms):
            results.append(e)
    # Prefer shorter titles (more specific match) first
    results.sort(key=lambda e: len(e["title"]))
    return results[:limit]


def list_categories(entries):
    counts = {}
    for e in entries:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
    for cat, n in sorted(counts.items()):
        print(f"{n:4d}  {cat}")


def main():
    ap = argparse.ArgumentParser(description="Search the official SAP BTP shape library.")
    ap.add_argument("query", nargs="?", help='keywords, e.g. "work zone" or "s/4hana"')
    ap.add_argument("--category", help="restrict to a category name substring")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--list-categories", action="store_true")
    ap.add_argument("--full", action="store_true", help="print the full decoded mxGraphModel XML")
    args = ap.parse_args()

    if not os.path.exists(CONFIG):
        sys.exit(f"error: SAP shape config not found at {CONFIG}")
    entries = load_entries()

    if args.list_categories:
        list_categories(entries)
        return

    if not args.query:
        sys.exit("error: provide a search query, or use --list-categories")

    results = search(entries, args.query, args.category, args.limit)
    if not results:
        sys.exit(f"no shapes matched {args.query!r}")

    for e in results:
        print(f"[{e['category']}] {e['title']}  ({e['w']}x{e['h']})")
        decoded = decode_shape_xml(e["xml"])
        if args.full:
            print(decoded)
        else:
            m = re.search(r'<mxCell[^>]*style="([^"]+)"', decoded)
            print("  style: " + (m.group(1) if m else "(group/container - use --full to see all cells)"))
        print()


if __name__ == "__main__":
    main()
