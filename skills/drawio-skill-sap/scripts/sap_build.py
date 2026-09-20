"""Render a SAP BTP solution diagram (.drawio) from a small JSON layout spec.

Why this exists: every SAP icon in references/drawio-sap-config.json is a ~4 KB
base64 SVG embedded in the `style=` string. Hand-copying those into XML is slow
and one truncated character silently breaks the icon. This script resolves them
by name and emits valid, uncompressed .drawio XML with correct parent nesting
(children of an area are real child cells with coordinates relative to that
area, which is what validate.py expects - sibling cells that merely overlap a
container are reported as "vertices overlap").

  python3 sap_build.py spec.json -o diagram.drawio
  python3 sap_build.py --list-generic
  python3 sap_build.py --find "cloud integration"

Spec format (all coordinates are relative to `parent`, default the page root):

{
  "name": "My Scenario (L1)",
  "page": {"width": 1500, "height": 760},
  "nodes": [
    {"id": "title",  "type": "text", "value": "My Scenario", "x": 40, "y": 30,
     "w": 940, "h": 30, "size": 16, "bold": true, "align": "left",
     "color": "title"},

    {"id": "tp",  "type": "box",  "title": "Third-Party Application",
     "palette": "nonsap", "x": 40, "y": 340, "w": 280, "h": 100,
     "generic": "third-party-apps"},

    {"id": "btp", "type": "area", "title": "SAP Business Technology Platform",
     "palette": "sap", "x": 480, "y": 180, "w": 460, "h": 400},
    {"id": "sub", "type": "area", "parent": "btp", "title": "Subaccount",
     "palette": "neutral", "x": 30, "y": 60, "w": 400, "h": 290},

    {"id": "ci",  "type": "icon", "parent": "sub", "icon": "cloud integration",
     "label": "Cloud Integration", "x": 150, "y": 70, "w": 40, "h": 40},
    {"id": "s4",  "type": "logo", "parent": "cloud", "logo": "SAP S/4HANA Cloud",
     "x": 76, "y": 100, "w": 168}
  ],
  "edges": [
    {"id": "e1", "source": "tp", "target": "ci", "kind": "direct",
     "exit": [1, 0.5], "entry": [0, 0.5],
     "label": "HTTPS\n(HTTP adapter)", "labelPos": -0.57, "labelDy": -24}
  ]
}

Node types
  area     titled container (title band top-left, bold 16px)
  box      container with its title centred inside; add "generic" to place the
           reference grey/blue generic icon in the title band
  icon     SAP service icon (looked up in drawio-sap-config.json by keyword)
  logo     SAP product logo; height is derived from the logo's native aspect
  generic  standalone generic icon from SAP_Build_Process_Automation_L2.drawio
  text     plain label
  swatch   small rounded chip, for legends

Edge kinds: direct, bidirectional, plain, indirect, optional, trust, auth,
authz, highlight, warning, error, firewall.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.parse
import zlib
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(HERE, "..", "references")
SAP_CONFIG = os.path.join(REFS, "drawio-sap-config.json")
GENERIC_SRC = os.path.join(REFS, "SAP_Build_Process_Automation_L2.drawio")

# Generic (non-product) SAP icons. These have no entry in the shape library, so
# they are lifted verbatim out of the official reference diagram by cell id.
GENERIC_ICONS = {
    "end-user": "-Aj5rOMPWS9pz5DeyN8X-33",              # person in a circle
    "application-clients": "-Aj5rOMPWS9pz5DeyN8X-22",   # desktop + mobile
    "third-party-idp": "-Aj5rOMPWS9pz5DeyN8X-37",       # two people
    "key-user": "-Aj5rOMPWS9pz5DeyN8X-72",              # person + settings
    "screen": "-Aj5rOMPWS9pz5DeyN8X-69",                # monitor
    "cloud-solutions": "-Aj5rOMPWS9pz5DeyN8X-29",       # cloud
    "third-party-apps": "ZNLiSohyDAu_GED2eyi8-9",       # cloud (3rd party box)
    "on-premise-solutions": "-Aj5rOMPWS9pz5DeyN8X-85",  # building
    "cloud-connector": "ZNLiSohyDAu_GED2eyi8-5",
}

PALETTES = {
    "sap": ("#0070F2", "#EBF8FF"),
    "sap-white": ("#0070F2", "#ffffff"),
    "neutral": ("#475E75", "#ffffff"),
    "nonsap": ("#475E75", "#F5F6F7"),
    "accent1": ("#07838F", "#DAFDF5"),
    "accent2": ("#5D36FF", "#F1ECFF"),
    "accent3": ("#CB00DC", "#FFF0FA"),
    "positive": ("#188918", "#F5FAE5"),
    "critical": ("#C35500", "#FFF8D6"),
    "negative": ("#D20A0A", "#FFEAF4"),
}

FONT_COLORS = {"title": "#1D2D3E", "body": "#556B82"}

ORTH = ("edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
        "strokeWidth=1.5;endSize=4;startSize=4;")
ENTITY = ("edgeStyle=entityRelationEdgeStyle;rounded=0;html=1;strokeWidth=1.5;endSize=4;"
          "startSize=4;jumpStyle=none;jumpSize=0;targetPerimeterSpacing=15;")

EDGE_KINDS = {
    "direct": ORTH + "strokeColor=#475E75;endArrow=blockThin;endFill=1;",
    "bidirectional": ORTH + "strokeColor=#475E75;endArrow=blockThin;endFill=1;startArrow=blockThin;startFill=1;",
    "plain": ORTH + "strokeColor=#475E75;endArrow=none;endFill=0;startArrow=none;startFill=0;",
    "indirect": ENTITY + "strokeColor=#475E75;endArrow=blockThin;endFill=1;startArrow=none;startFill=0;dashed=1;",
    "optional": ENTITY + "strokeColor=#475E75;endArrow=blockThin;endFill=1;startArrow=none;startFill=0;dashed=1;dashPattern=1 4;",
    "trust": ORTH + "strokeColor=#CB00DC;endArrow=blockThin;endFill=1;",
    "auth": ORTH + "strokeColor=#188918;endArrow=blockThin;endFill=1;dashed=1;",
    "authz": ORTH + "strokeColor=#5D36FF;endArrow=blockThin;endFill=1;",
    "highlight": ORTH + "strokeColor=#07838F;endArrow=blockThin;endFill=1;",
    "warning": ORTH + "strokeColor=#C35500;endArrow=blockThin;endFill=1;",
    "error": ORTH + "strokeColor=#D20A0A;endArrow=blockThin;endFill=1;",
    "firewall": ("edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
                 "strokeColor=#475E75;strokeWidth=3;endArrow=none;endFill=0;startArrow=none;startFill=0;"),
}

AREA_BASE = ("rounded=1;whiteSpace=wrap;html=1;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;"
             "container=0;")
TEXT_BASE = "text;html=1;points=[];resizable=0;strokeColor=none;fillColor=none;fontFamily=Helvetica;"


# ---------------------------------------------------------------- shape lookup

def _load_sap_entries():
    with open(SAP_CONFIG, "r", encoding="utf-8") as f:
        data = json.load(f)
    entries = []
    for lib in data.get("libraries", []):
        for sub in lib.get("entries", []):
            for l in sub.get("libs", []):
                cat = l.get("title", {}).get("main", "?")
                for e in l.get("data", []):
                    t = e.get("title")
                    if t and t != "?":
                        entries.append({"title": t, "category": cat, "xml": e["xml"],
                                        "w": e.get("w"), "h": e.get("h")})
    return entries


def _decode(entry):
    raw = base64.b64decode(entry["xml"])
    return urllib.parse.unquote(zlib.decompress(raw, -zlib.MAX_WBITS).decode("utf-8"))


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


_ENTRY_CACHE = None


def find_sap_shape(query, category=None):
    """Return (image_style, native_w, native_h) for the best title match."""
    global _ENTRY_CACHE
    if _ENTRY_CACHE is None:
        _ENTRY_CACHE = _load_sap_entries()
    terms = _norm(query).split()
    hits = [e for e in _ENTRY_CACHE
            if (not category or category.lower() in e["category"].lower())
            and all(t in _norm(e["title"] + " " + e["category"]) for t in terms)]
    if not hits:
        raise SystemExit("no SAP shape matches %r - try scripts/sap_shapesearch.py" % query)
    hits.sort(key=lambda e: len(e["title"]))
    best = hits[0]
    styles = re.findall(r'style="(shape=image;[^"]*)"', _decode(best))
    if not styles:
        raise SystemExit("shape %r carries no image style" % best["title"])
    return styles[0], best["w"], best["h"]


_GENERIC_CACHE = {}


def find_generic(name):
    if name not in GENERIC_ICONS:
        raise SystemExit("unknown generic icon %r - one of: %s"
                         % (name, ", ".join(sorted(GENERIC_ICONS))))
    if not _GENERIC_CACHE:
        with open(GENERIC_SRC, "r", encoding="utf-8") as f:
            txt = f.read()
        for key, cid in GENERIC_ICONS.items():
            m = re.search(r'<mxCell id="%s"[^>]*?style="(shape=image;[^"]*)"'
                          % re.escape(cid), txt)
            if m:
                _GENERIC_CACHE[key] = m.group(1)
    return _GENERIC_CACHE[name]


# -------------------------------------------------------------------- emitting

def _val(s):
    """Escape a label once and turn newlines into draw.io line breaks."""
    return escape(s or "").replace("\n", "&#xa;")


class Builder:
    def __init__(self, spec):
        self.spec = spec
        self.cells = []
        self.seen = set()

    def _cell(self, cid, value, style, x, y, w, h, parent):
        if cid in self.seen:
            raise SystemExit("duplicate node id %r" % cid)
        self.seen.add(cid)
        self.cells.append(
            '        <mxCell id="%s" value="%s" style="%s" vertex="1" parent="%s">\n'
            '          <mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry" />\n'
            '        </mxCell>' % (cid, value, style, parent, x, y, w, h))

    def node(self, n):
        t = n.get("type", "area")
        parent = n.get("parent", "1")
        x, y = n.get("x", 0), n.get("y", 0)
        border, fill = PALETTES[n.get("palette", "sap")]
        font = FONT_COLORS.get(n.get("color", "body"), n.get("color", "#556B82"))

        if t == "area":
            style = (AREA_BASE + "verticalAlign=top;align=left;fontSize=%d;fontStyle=1;"
                     "spacingLeft=14;spacingTop=12;fontColor=#1D2D3E;strokeColor=%s;fillColor=%s;"
                     % (n.get("size", 16), border, fill))
            self._cell(n["id"], _val(n.get("title")), style, x, y,
                       n["w"], n["h"], parent)

        elif t == "box":
            has_icon = bool(n.get("generic"))
            style = (AREA_BASE + "align=%s;verticalAlign=%s;fontSize=%d;fontStyle=1;"
                     "fontColor=#1D2D3E;strokeColor=%s;fillColor=%s;"
                     % ("left" if has_icon else "center",
                        "bottom" if has_icon else "middle",
                        n.get("size", 14), border, fill))
            if has_icon:
                style += "spacingLeft=12;spacingBottom=10;"
            self._cell(n["id"], _val(n.get("title")), style, x, y,
                       n["w"], n["h"], parent)
            if has_icon:
                self._cell(n["id"] + "-icon", "", find_generic(n["generic"]),
                           12, 10, n.get("iconW", 28), n.get("iconH", 18), n["id"])

        elif t in ("icon", "logo", "generic"):
            if t == "generic":
                style = find_generic(n["generic"])
                w, h = n.get("w", 40), n.get("h", 40)
            elif t == "icon":
                style, _, _ = find_sap_shape(n["icon"])
                w, h = n.get("w", 40), n.get("h", 40)
            else:
                style, nw, nh = find_sap_shape(n["logo"], category="SAP Products")
                w = n.get("w", 160)
                h = n.get("h", round(w * float(nh) / float(nw)))
            self._cell(n["id"], "", style, x, y, w, h, parent)
            if n.get("label"):
                lw = n.get("labelW", 240)
                self._cell(n["id"] + "-label", _val(n["label"]),
                           TEXT_BASE + "align=center;verticalAlign=middle;fontSize=%d;fontColor=%s;"
                           % (n.get("labelSize", 12), FONT_COLORS["body"]),
                           x + w / 2 - lw / 2, y + h + n.get("labelGap", 4),
                           lw, n.get("labelH", 30), parent)

        elif t == "text":
            self._cell(n["id"], _val(n.get("value")),
                       TEXT_BASE + "align=%s;verticalAlign=middle;fontSize=%d;fontColor=%s;fontStyle=%d;"
                       % (n.get("align", "center"), n.get("size", 12), font,
                          1 if n.get("bold") else 0),
                       x, y, n["w"], n["h"], parent)

        elif t == "swatch":
            self._cell(n["id"], "",
                       "rounded=1;arcSize=16;absoluteArcSize=1;html=1;strokeWidth=1.5;"
                       "strokeColor=%s;fillColor=%s;" % (border, fill),
                       x, y, n.get("w", 28), n.get("h", 18), parent)

        else:
            raise SystemExit("unknown node type %r" % t)

    def edge(self, e):
        style = EDGE_KINDS[e.get("kind", "direct")]
        style += "sourcePerimeterSpacing=%d;targetPerimeterSpacing=%d;" % (
            e.get("sourceGap", 6), e.get("targetGap", 6))
        ex, ey = e.get("exit", [None, None])
        nx, ny = e.get("entry", [None, None])
        if ex is not None:
            style += "exitX=%s;exitY=%s;exitDx=0;exitDy=0;" % (ex, ey)
        if nx is not None:
            style += "entryX=%s;entryY=%s;entryDx=0;entryDy=0;" % (nx, ny)

        pts = ""
        way = e.get("waypoint")
        if way:
            if len(e.get("waypoints", [way])) > 1:
                raise SystemExit("edge %r: at most one waypoint (one bend) is allowed" % e["id"])
            pts = ('            <Array as="points">\n'
                   '              <mxPoint x="%s" y="%s" />\n'
                   '            </Array>\n' % (way[0], way[1]))

        # "from"/"to" draw a free-floating sample line (legend swatches).
        if "from" in e:
            pts += ('            <mxPoint x="%s" y="%s" as="sourcePoint" />\n'
                    '            <mxPoint x="%s" y="%s" as="targetPoint" />\n'
                    % (e["from"][0], e["from"][1], e["to"][0], e["to"][1]))
            ends = ""
        else:
            ends = ' source="%s" target="%s"' % (e["source"], e["target"])

        geom = ('          <mxGeometry relative="1" as="geometry">\n%s'
                '          </mxGeometry>\n' % pts) if pts else \
               '          <mxGeometry relative="1" as="geometry" />\n'
        self.cells.append(
            '        <mxCell id="%s" value="" style="%s" edge="1" parent="1"%s>\n'
            '%s        </mxCell>' % (e["id"], style, ends, geom))

        if e.get("label"):
            self.cells.append(
                '        <mxCell id="%s-lbl" value="%s" style="edgeLabel;html=1;align=center;'
                'verticalAlign=middle;resizable=0;points=[];fontSize=11;fontColor=#556B82;'
                'labelBackgroundColor=none;spacing=2;" vertex="1" connectable="0" parent="%s">\n'
                '          <mxGeometry x="%s" relative="1" as="geometry">\n'
                '            <mxPoint y="%s" as="offset" />\n'
                '          </mxGeometry>\n'
                '        </mxCell>' % (e["id"], _val(e["label"]), e["id"],
                                       e.get("labelPos", 0), e.get("labelDy", -24)))

    def build(self):
        for n in self.spec.get("nodes", []):
            self.node(n)
        for e in self.spec.get("edges", []):
            self.edge(e)
        page = self.spec.get("page", {})
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<mxfile host="drawio" version="26.0.0">\n'
                '  <diagram name="%s">\n'
                '    <mxGraphModel dx="1400" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" '
                'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" '
                'math="0" shadow="0">\n'
                '      <root>\n'
                '        <mxCell id="0" />\n'
                '        <mxCell id="1" parent="0" />\n'
                '%s\n'
                '      </root>\n'
                '    </mxGraphModel>\n'
                '  </diagram>\n'
                '</mxfile>\n'
                % (escape(self.spec.get("name", "SAP BTP Solution Diagram")),
                   page.get("width", 1500), page.get("height", 900),
                   "\n".join(self.cells)))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?", help="JSON layout spec")
    ap.add_argument("-o", "--out", help="output .drawio path")
    ap.add_argument("--list-generic", action="store_true",
                    help="list generic icon names taken from the reference diagram")
    ap.add_argument("--find", metavar="KEYWORD",
                    help="show which SAP shape a keyword resolves to")
    args = ap.parse_args()

    if args.list_generic:
        for k in sorted(GENERIC_ICONS):
            print("%-22s %s" % (k, GENERIC_ICONS[k]))
        return
    if args.find:
        style, w, h = find_sap_shape(args.find)
        print("native size: %sx%s" % (w, h))
        print("style length: %d chars (resolved, not printed)" % len(style))
        return
    if not args.spec or not args.out:
        ap.error("spec and -o/--out are required")

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = json.load(f)
    xml = Builder(spec).build()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(xml)
    print("wrote %s" % args.out)
    print("next: python3 %s %s --strict --score"
          % (os.path.join(HERE, "validate.py"), args.out))


if __name__ == "__main__":
    sys.exit(main())