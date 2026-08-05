#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
import sys
from urllib.parse import urlparse
import urllib.request

MANIFEST = os.path.join(os.path.dirname(__file__), "..", "data", "lobe-icons.json")
STYLE = ("shape=image;html=1;imageAspect=0;aspect=fixed;"
         "verticalLabelPosition=bottom;verticalAlign=top;image=")
_VARIANT = re.compile(r"-(?:color|text(?:-[a-z]{2})?|brand(?:-color)?)$")

# Common RAG/LLM data stores that lobe-icons lacks, mapped to simple-icons
# slugs (https://simpleicons.org, CC0). Each slug below is verified to resolve
# from the published simple-icons asset endpoint.
_SIMPLEICONS_BASE_URL = "https://cdn.simpleicons.org/"
_ALLOWED_ICON_HOSTS = {
    "cdn.simpleicons.org",
    "unpkg.com",
    "cdn.jsdelivr.net",
    "raw.githubusercontent.com",
    "github.com",
}
_SUPPLEMENT = {
    "qdrant": "qdrant",
    "milvus": "milvus",
    "supabase": "supabase",
    "redis": "redis",
    "postgresql": "postgresql",
    "mongodb": "mongodb",
    "elasticsearch": "elasticsearch",
    "neo4j": "neo4j",
    "kafka": "apachekafka",
    "clickhouse": "clickhouse",
    "duckdb": "duckdb",
    "mysql": "mysql",
    "sqlite": "sqlite",
    "cassandra": "apachecassandra",
    "snowflake": "snowflake",
    "databricks": "databricks",
    "mariadb": "mariadb",
    "couchbase": "couchbase",
}


def families(icons):
    """base brand name -> set of its variant filenames (without .svg)."""
    fam = {}
    for name in icons:
        base = _VARIANT.sub("", name)
        fam.setdefault(base, set()).add(name)
    return fam


def squish(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def search(fam, query, limit):
    """Rank brand bases against the query (squished + per-token matching)."""
    q = squish(query)
    tokens = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if t]
    scored = {}
    for base in fam:
        b = squish(base)
        s = 0
        if q and q == b:
            s = 100
        elif q and b.startswith(q):
            s = 60
        elif q and q in b:
            s = 40
        for t in tokens:
            if t == b:
                s = max(s, 90)
            elif len(t) >= 3 and b.startswith(t):
                s = max(s, 50)
            elif len(t) >= 3 and t in b:
                s = max(s, 30)
        if s:
            scored[base] = s
    return sorted(scored, key=lambda base: (-scored[base], base))[:limit]


def search_supplement(query):
    """Fall back to the simple-icons supplement (exact or substring match)."""
    q = squish(query)
    if not q:
        return None
    if q in _SUPPLEMENT:
        return q
    for brand in _SUPPLEMENT:
        if q in brand or brand in q:
            return brand
    return None


def pick_variant(base, variants, prefer):
    order = {"color": ["-color", "-brand-color", "", "-brand", "-text", "-text-cn"],
             "mono":  ["", "-brand", "-color", "-brand-color", "-text", "-text-cn"],
             "text":  ["-text", "-text-cn", "-brand", "-brand-color", "-color", ""]}[prefer]
    for suffix in order:
        cand = base + suffix
        if cand in variants:
            return cand
    return next(iter(sorted(variants)), None)


def _is_allowed_icon_url(url):
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.netloc in _ALLOWED_ICON_HOSTS


def _fetch_svg(url, timeout=15):
    if not _is_allowed_icon_url(url):
        raise ValueError(f"blocked icon URL host: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "aiicons/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        svg = resp.read()
    if b"<svg" not in svg[:512]:
        raise ValueError(f"response is not SVG: {url}")
    return svg


def main():
    ap = argparse.ArgumentParser(description="Find AI/LLM brand logos as draw.io styles (lobe-icons asset URLs).")
    ap.add_argument("query", nargs="?", help='brand name, e.g. "openai" or "claude"')
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--variant", choices=["color", "mono", "text"], default="color")
    ap.add_argument("--size", type=int, default=48, help="cell width/height in px (icons are square)")
    ap.add_argument("--embed", action="store_true",
                    help="inline the SVG as a data URI (fetches it now; portable, no network at render time)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list", action="store_true", help="list all brand names and exit")
    args = ap.parse_args()

    if not os.path.exists(MANIFEST):
        sys.exit(f"error: manifest not found at {MANIFEST}")
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    fam = families(manifest["icons"])
    asset_base_url = manifest.get("base_url") or manifest["cdn"]
    if not _is_allowed_icon_url(asset_base_url):
        sys.exit(f"error: untrusted icon base URL in manifest: {asset_base_url}")

    if args.list:
        for base in sorted(fam):
            print(base)
        return
    if not args.query:
        ap.error("a query is required (or use --list)")

    matches = search(fam, args.query, args.limit)

    results = []
    if matches:
        for base in matches:
            file = pick_variant(base, fam[base], args.variant)
            url = f"{asset_base_url}{file}.svg"
            if args.embed:
                try:
                    svg = _fetch_svg(url, timeout=15)
                except Exception as exc:                   # noqa: BLE001 - report and skip
                    sys.stderr.write(f"warning: could not fetch {url} ({exc})\n")
                    continue
                # Rewrite the 1em intrinsic size so draw.io scales the inlined SVG.
                svg = svg.replace(b'width="1em"', b'width="24"').replace(b'height="1em"', b'height="24"')
                # Marker-less base64: draw.io splits style values on ';', so a
                # ';base64,' marker would truncate the image= value (issue #80).
                image = "data:image/svg+xml," + base64.b64encode(svg).decode()
            else:
                image = url
            results.append({"brand": base, "file": file, "w": args.size, "h": args.size,
                            "style": STYLE + image})
    else:
        # lobe has no logo for this brand; fall back to the simple-icons supplement.
        brand = search_supplement(args.query)
        if brand:
            slug = _SUPPLEMENT[brand]
            url = _SIMPLEICONS_BASE_URL + slug
            image = url
            if args.embed:
                try:
                    svg = _fetch_svg(url, timeout=15)
                    # Marker-less base64 (see issue #80 note above).
                    image = "data:image/svg+xml," + base64.b64encode(svg).decode()
                except Exception as exc:                   # noqa: BLE001 - keep the asset URL
                    sys.stderr.write(f"warning: could not fetch {url} ({exc}); using asset URL\n")
            results.append({"brand": brand, "file": f"simpleicons:{slug}",
                            "w": args.size, "h": args.size, "style": STYLE + image})

    if not results:
        sys.exit(f"no logo for {args.query!r} — for a data store try a cylinder "
                 f"(shape=cylinder3) or shapesearch.py '{args.query} database'")

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            shown = r["style"] if len(r["style"]) < 160 else r["style"][:157] + "..."
            print(f"{r['brand']}  ({r['file']}, {r['w']}x{r['h']})\n  {shown}")


if __name__ == "__main__":
    main()
