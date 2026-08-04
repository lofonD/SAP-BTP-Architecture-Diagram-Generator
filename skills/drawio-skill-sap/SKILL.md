---
name: drawio-skill-sap
description: "Generate SAP BTP solution diagrams following the official SAP BTP Solution Diagram Design Guideline (Horizon theme). Use when: user requests an SAP architecture diagram, BTP landscape, Cloud Foundry/Kyma topology, Integration Suite flow, on-premise connectivity, subaccount layout, or any SAP system visualization. Produces .drawio XML with official SAP Horizon colors, proper area nesting, connector semantics, and exports images via draw.io CLI. Reference: 1) https://github.com/SAP/btp-solution-diagrams  2) https://github.com/Agents365-ai/drawio-skill"
homepage: https://github.com/lofonD/SAP-BTP-Architecture-Diagram-Generator
compatibility: Requires draw.io desktop app CLI on PATH (macOS/Linux/Windows). Self-check step requires a vision-enabled model (e.g., Claude Sonnet/Opus); gracefully skipped if unavailable.
platforms: [macos, linux, windows]
metadata: {"openclaw":{"requires":{"anyBins":["draw.io","drawio"]},"emoji":"📐","os":["darwin","linux","win32"],"install":[{"id":"brew-drawio","kind":"brew","formula":"drawio","bins":["draw.io"],"label":"Install draw.io via Homebrew","os":["darwin"]}]},"hermes":{"tags":["drawio","diagram","flowchart","architecture","visualization","uml"],"category":"design","requires_tools":["draw.io"],"related_skills":["mermaid","excalidraw","plantuml"]},"author":"Agents365-ai","version":"1.5.3"}
---

# Draw.io Diagrams

## Overview
Generate `.drawio` XML files and export to PNG/SVG/PDF/JPG locally using the native draw.io desktop app CLI.

**Supported formats:** PNG, SVG, PDF, JPG — no browser automation needed.

# SAP BTP Solution Diagrams

Generate SAP Business Technology Platform solution diagrams following the **official SAP BTP Solution Diagram Design Guideline** (Horizon theme, atomic design system).

Reference: [SAP/btp-solution-diagrams](https://github.com/SAP/btp-solution-diagrams/tree/main/guideline/docs/btp_guideline)

## Bundled Resources

Official SAP example diagrams are in `references/`. Load them when you need real-world XML patterns:

| File | Use Case |
|---|---|
| `references/drawio-sap-config.json` | The **real, official SAP shape library** (SAP Corporate / SAP BTP Graphics), exported from draw.io. Contains every persona/system icon, SAP product logo, reusable container ("Component Group"), and pre-styled connector as compressed shape XML. **Do not hand-write icon styles — always look shapes up here via `scripts/sap_shapesearch.py`.** <Mandatory to load> |
| `scripts/sap_shapesearch.py` | Search `drawio-sap-config.json` by keyword and get the exact, ready-to-paste `style=` string (or full mxCell XML) for a real SAP icon, product logo, container template, or connector. **Use this for every persona/system node — never a plain box.** |
| `references/BTP_Reference_Architect_Diagram.svg` | BTP Overall Reference Diagram Pattern |
| `references/SAP_Task_Center_L0.drawio` | L0 Task Center L0 pattern |
| `references/SAP_Task_Center_L1.drawio` | L1 Task Center L1 pattern |
| `references/SAP_Task_Center_L2.drawio` | L2 Task Center L2 pattern |
| `references/SAP_Start_L2.drawio` | SAP Start L2 pattern |
| `references/SAP_Build_Work_Zone_L2.drawio` | SAP Build Work Zone L2 pattern |
| `references/SAP_Build_Process_Automation_L2.drawio` | SAP Build Process Automation L2 |
| `references/SAP_Cloud_Identity_Services_Authentication_L2.drawio` | SAP Cloud Identity Services Authentication L2 |
| `references/SAP_Private_Link_Service_L2.drawio` | SAP Private Link connectivity (L2) |
| `scripts/repair_png.py` | After every `-e` PNG export — fixes draw.io's truncated IEND chunk (issue #8) |
| `scripts/encode_drawio_url.py` | The CLI is unavailable and you need a browser-fallback diagrams.net URL |

> Every bundled `references/*.drawio` example uses `shape=image;...;image=data:image/svg+xml,<data>` for its icons — none of them use a `mxgraph.sap.icon` stencil (that stencil does not exist in draw.io). Always match this pattern.

## Prerequisites

The draw.io desktop app must be installed:

```bash
# Windows
"C:\Program Files\draw.io\draw.io.exe" --version

# macOS
drawio --version

# Linux
draw.io --version
```

Install if missing: download from https://github.com/jgraph/drawio-desktop/releases

**SAP shape libraries:** Download the official draw.io shape libraries from [SAP/btp-solution-diagrams/assets/shape-libraries-and-editable-presets/draw.io](https://github.com/SAP/btp-solution-diagrams/tree/main/assets/shape-libraries-and-editable-presets/draw.io) for service icons with grey background circles.

## SAP BTP Design Guideline (Horizon Theme)

This skill follows the **Atomic Design System** approach:
- **Atoms**: colors, line styles, icons, text
- **Molecules**: arrows, areas, service icons with labels
- **Organisms**: component groups (User, BTP Layer, Third Party, On-Premise)

### Official SAP Horizon Color Palette

#### Primary Colors (mandatory for all BTP diagrams)

| Purpose | Border | Fill | Usage |
|---------|--------|------|-------|
| **SAP/BTP Areas** | `#0070F2` | `#EBF8FF` | All SAP/BTP boundaries, subaccounts, services |
| **Non-SAP Areas** | `#475E75` | `#F5F6F7` | Third-party systems, external services, on-premise |
| **Text Title** | `#1D2D3E` | — | Area/component titles |
| **Text Body** | `#556B82` | — | Descriptions, labels |

#### Semantic Colors (for status/flow meaning)

| Status | Border | Fill | Usage |
|--------|--------|------|-------|
| **Positive** | `#188918` | `#F5FAE5` | Authentication flows, success states |
| **Critical** | `#C35500` | `#FFF8D6` | Warning, attention needed |
| **Negative** | `#D20A0A` | `#FFEAF4` | Errors, failures |

#### Accent/Emphasized Colors (use sparingly)

| Accent | Border | Fill | Usage |
|--------|--------|------|-------|
| **Teal** | `#07838F` | `#DAFDF5` | Highlighted areas, special zones |
| **Indigo** | `#5D36FF` | `#F1ECFF` | Authorization flows |
| **Pink** | `#CB00DC` | `#FFF0FA` | Trust flows |

### Areas (Containers)

Areas are the primary structural element in BTP diagrams.

**Rules:**
- Fixed corner radius: `arcSize=24;absoluteArcSize=1;` (24px absolute radius per official examples)
- `strokeWidth=1.5;` on all area borders
- Alternate between fill (`#EBF8FF`) and no-fill (`#ffffff`) when nesting
- The parent layer is usually the BTP layer (blue)
- Stack areas to show cardinality (multiple instances)
- Do NOT overuse colors — keep diagrams predominantly blue with grey for non-SAP
- Use `container=0;` on outer areas (not draw.io container behavior)

**Area Nesting Pattern:**
```
L0: BTP Platform (blue border #0070F2, blue fill #EBF8FF)
  L1: Subaccount (grey border #475E75, white fill #ffffff)
    L2: Runtime/Service group (blue border #0070F2, blue fill #EBF8FF)
```

### Line Styles (Connectors)

| Style | Meaning | draw.io Style |
|-------|---------|---------------|
| **Solid** | Direct, synchronous request-response | `dashed=0;` |
| **Dashed** | Indirect, asynchronous data flow | `dashed=1;` |
| **Dotted** | Optional data flow | `dashed=1;dashPattern=1 2;` |
| **Thick grey** | Firewalls / network barriers only | `strokeWidth=3;strokeColor=#475E75;` |

### Connector Semantics (colored flows)

The official "Default Connectors" shapes use **grey `#475E75`** as the neutral/default connector color — color is reserved for specific semantic meaning, used sparingly (per the "keep diagrams predominantly blue/grey" rule above). Do not default every arrow to SAP Blue.

| Flow Type | Color | Hex |
|-----------|-------|-----|
| **Standard/default flow** | Grey | `#475E75` |
| **Trust** | Pink (Accent 3) | `#CB00DC` |
| **Authentication / success** | Green | `#188918` |
| **Authorization** | Indigo (Accent 2) | `#5D36FF` |
| **Highlighted/special flow** | Teal (Accent 1) | `#07838F` |
| **Warning** | Orange | `#C35500` |
| **Error/negative** | Red | `#D20A0A` |
| **Firewall/Network barrier** | Thick grey, no arrow | `#475E75` (strokeWidth=3) |

Solid = direct/synchronous, `dashed=1;edgeStyle=entityRelationEdgeStyle;targetPerimeterSpacing=15;` = indirect/asynchronous, add `dashPattern=1 4;` on top of dashed for optional/dotted (exact patterns per the official "Colored Connectors SAP BTP" library — look them up with `sap_shapesearch.py "direct one-directional"` etc. rather than hand-guessing).

### Icons — MANDATORY: use real SAP shapes, never plain boxes

**Every persona and every SAP system/service/product in a diagram MUST render as a real SAP icon or product logo — plain rounded rectangles are ONLY for area/container boundaries (BTP platform, subaccount, cloud-solutions box, on-premise box), never for an individual component, persona, or service.**

There is no `mxgraph.sap.icon` / `SAPIcon=<name>` stencil in draw.io — that style renders as an empty default shape, which is why generated diagrams look like plain boxes instead of icons. The **real** SAP icons are bundled, pre-rendered shapes in `references/drawio-sap-config.json` (SAP's own exported draw.io shape library), each stored as a `shape=image;...;image=data:image/svg+xml,<base64-svg>;` style — this is exactly what every bundled `references/*.drawio` example file actually uses.

**Workflow for every persona/system node:**
1. Search for it: `python3 <this-skill-dir>/scripts/sap_shapesearch.py "<keyword>"` (e.g. `"work zone"`, `"s/4hana"`, `"successfactors"`, `"cloud connector"`, `"identity authentication"`, `"hana cloud"`).
2. Copy the printed `style="..."` string verbatim into your `mxCell` (do not edit the embedded base64 image data).
3. Set `vertex="1"`, your own `id`/`parent`, a `value` label, and `<mxGeometry .../>` — icons are square (usually 32x32 for service icons, keep `aspect=fixed`); product logos have their own native aspect ratio (read the printed `w`x`h` and scale proportionally).
4. If nothing matches, fall back to `python3 <this-skill-dir>/scripts/shapesearch.py "<keyword>"` (generic draw.io shape index) before ever hand-writing a plain box for a named system.

**Business User & Application Clients icons** — these are NOT standalone shapes; they must be extracted from the `"Application and User"` component group:
1. Run `python3 <this-skill-dir>/scripts/sap_shapesearch.py "Application and User" --full`
2. Parse the returned XML for all `style="shape=image..."` attributes
3. The **first** `shape=image` match is the **Application Clients** icon (mobile/desktop devices, ~2600 chars)
4. The **second** `shape=image` match is the **Business User** icon (person-in-circle, ~4800 chars)
5. **NEVER use `shape=mxgraph.general.person`** for business users — it renders incorrectly in SAP diagrams. Always use the extracted person-in-circle SVG from the component group.
6. **Architecture pattern**: Business Users → Application Clients (mobile/desktop) → the first service explicitly requested by the user. Users do NOT connect directly to a BTP service when an application client is part of the scenario. Never insert SAP Build Work Zone or another intermediary unless the requirements call for it.

**SAP Cloud Identity Services** — always include in BTP diagrams that involve user authentication:
1. Search: `sap_shapesearch.py "cloud identity"` for the icon
2. Place inside a dedicated container within BTP (e.g., "SAP Cloud Identity Services" area with blue border)
3. Connect authentication flows using green dashed lines (`strokeColor=#188918;dashed=1;`)

**Other things available in the same library** (search the same way):
- **Reusable containers** ("Component Groups SAP BTP" category) — `"BTP Basic Layer"`, `"Non-SAP Content"`, `"Accented Layer"`, `"User"`, `"Third Party"`, `"Application and User"`, `"Bigger SAP Box with mutliple layers"` — pre-built multi-cell groups matching the guideline exactly; prefer these over hand-rolled areas when one fits.
- **SAP product logos** ("SAP Products SAP BTP" category) — `"SAP S/4HANA (Default)"`, `"SAP SuccessFactors (Default)"`, `"SAP Fieldglass (Text Only)"`, etc. Use `(Default)` (icon+logo) for primary systems, `(Text Only)` for secondary/incidental references.
- **Legend/title/description blocks** — `"Compact Legend"`, `"Extended Legend"`, `"Diagram Title"`, `"Diagram Description (mandatory)"`, `"Path Description"`.
- **Pre-styled connectors** — `"direct one-directional"`, `"indirect one-directional"`, `"default firewall"`, plus colored variants (`"success color"`, `"Accent 1 color"`, `"dashed error color"`, etc.) — use `--full` to get the exact style string.
- Run `python3 <this-skill-dir>/scripts/sap_shapesearch.py --list-categories` to see every category and how many shapes it holds.

### Text Styles (from Fiori Horizon)

Four hierarchy levels:
1. **H1 / Area Title**: Bold, `#1D2D3E`, fontSize=16
2. **H2 / Component Title**: Bold, `#1D2D3E`, fontSize=14
3. **Body / Label**: Regular, `#556B82`, fontSize=12
4. **Caption / Annotation**: Regular, `#556B82`, fontSize=10

### Product Names

- SAP product names **must** be paired with the SAP logo
- Do NOT use too many SAP logos in one diagram — use text-only for secondary references
- Always use official product naming (e.g., "SAP HANA Cloud", not "HANA DB")

### Spacing

- Elements must have enough space to "breathe"
- Rule of thumb: spacing around objects should be **even** and roughly the height of the SAP Logo (~40-60px)
- Grid alignment: snap to multiples of 10

### Numbers

- Use numbered circles to describe specific paths/sequences in diagrams
- Blue circle with white number text

### Legend

**Always include a legend** in each diagram to clarify line style meanings.

## SAP BTP Component Catalog

Areas/containers use plain Horizon-styled rectangles (`strokeWidth=1.5` on all). **Individual persona/system/service nodes do not** — look those up with `scripts/sap_shapesearch.py` (see Icons section) and use the real `shape=image;...` style it returns.

| Component | Shape | Border | Fill |
|-----------|-------|--------|------|
| BTP Global Account | `rounded=1;arcSize=24;absoluteArcSize=1;` (area) | `#0070F2` | `#EBF8FF` |
| Subaccount | `rounded=1;arcSize=24;absoluteArcSize=1;` (area) | `#475E75` | `#ffffff` |
| Cloud Foundry Runtime / Kyma Runtime / ABAP Environment | `rounded=1;arcSize=24;absoluteArcSize=1;` (area) or real icon (`sap_shapesearch.py "cloud foundry"` / `"kyma runtime"` / `"abap environment"`) depending on level of detail | `#0070F2` | `#EBF8FF` |
| SAP HANA Cloud | real icon (`sap_shapesearch.py "hana cloud"`) | — | — |
| Integration Suite | real icon (`sap_shapesearch.py "integration suite"`) | — | — |
| Connectivity Service | real icon (`sap_shapesearch.py "connectivity service"`) | — | — |
| Destination Service | real icon (`sap_shapesearch.py "destination service"`) | — | — |
| SAP Build Work Zone | real icon (`sap_shapesearch.py "work zone"`) | — | — |
| SAP Build Process Automation | real icon (`sap_shapesearch.py "build process automation"`) | — | — |
| SAP Task Center | real icon (`sap_shapesearch.py "task center"`) | — | — |
| Auth & Trust (XSUAA) / Cloud Identity Services | real icon (`sap_shapesearch.py "authorization and trust"` / `"cloud identity"`) | — | — |
| SAP Event Mesh | real icon (`sap_shapesearch.py "event mesh"`) | — | — |
| Business Application Studio | real icon (`sap_shapesearch.py "business application studio"`) | — | — |
| S/4HANA (on-prem or public/private cloud), SuccessFactors, Fieldglass, Ariba, etc. | real product logo (`sap_shapesearch.py "s/4hana"`, `"successfactors"`, ... — use `(Default)` variant) | — | — |
| Cloud Connector | real icon (`sap_shapesearch.py "cloud connector"`) | — | — |
| On-Premise SAP System box / Third-Party box | `rounded=1;` (area/container) | `#475E75` | `#F5F6F7` |
| End Users / Business Users | real icon — extract the **person-in-circle** style from the `"Application and User"` component group (`sap_shapesearch.py "Application and User" --full`, then take the second `shape=image` style). **Do NOT use `shape=mxgraph.general.person`** — it does not render as a proper SAP icon. | — | — |
| Application Clients (Mobile/Desktop) | real icon — extract the **mobile/desktop devices** style from the `"Application and User"` component group (first `shape=image` style). Place between Business Users and BTP services as a required intermediary layer. | — | — |
| SAP Cloud Identity Services | real icon (`sap_shapesearch.py "cloud identity"`) — include as a standard component inside BTP for authentication flows. | — | — |
| Semantic badge (e.g. OIDC) | `rounded=1;arcSize=16;absoluteArcSize=1;` | `#188918` | `#F5FAE5` |

## Workflow

### Step 1 — Clarify Requirements

If key details are missing, ask 1-3 focused questions:
- **Which SAP services?** — HANA Cloud, Integration Suite, Connectivity, Kyma, ABAP env, etc.
- **Detail level?** — L1 (high-level overview) or L2 (detailed with subaccounts)?
- **On-premise systems?** — S/4HANA, ECC, third-party APIs?
- **Output format?** — PNG (default), SVG, PDF?

Skip clarification if the request already specifies these details.

### Step 2 — Check Dependencies

Verify draw.io CLI is accessible:
```bash
# Windows
"C:\Program Files\draw.io\draw.io.exe" --version
```

### Step 3 — Plan & Generate .drawio XML

1. **Create a component allowlist** from the request before laying out the diagram: requested actors, clients, services, targets, and any architecturally required supporting services. Do not add familiar products as decoration. In particular, SAP Build Work Zone, SuccessFactors, or extra posting targets appear only when requested or required by an explicitly described flow.
2. **Preserve the requested sequence** as an ordered edge list. For example, `Outlook -> Document AI -> Integration Suite -> S/4HANA Cloud` means exactly those three adjacent business-flow edges in that order; it does not permit an inserted Work Zone step or an additional target.
3. **Plan** — identify component groups (Organisms): Users, BTP Layer, Non-SAP systems.
4. **Structure** — use nested areas with alternating fill/no-fill:
   - L0: Global Account / BTP Platform boundary (blue fill)
   - L1: Subaccounts (no fill / white)
   - L2: Runtime environments, services
5. **Generate** — write `.drawio` XML using official Horizon colors. **For every persona/system node, look up its real icon/logo with `scripts/sap_shapesearch.py "<name>"` first** — never fall back to a plain rounded rectangle for a named component (only areas/containers use plain rectangles).

Load one of the reference examples (e.g., `references/SAP_Task_Center_L2.drawio`) as a pattern when building complex diagrams.

**XML Rules:**
- `id="0"` and `id="1"` are required root cells — never omit
- All text uses `html=1` in style
- Multi-line labels: use `&#xa;` for line breaks in `value` attributes
- Never use `--` inside XML comments
- Escape special characters: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- Corner radius: `arcSize=24;absoluteArcSize=1;` on all area containers
- Stroke width: `strokeWidth=1.5;` on all shapes and edges
- Arrow style: `endArrow=blockThin;endFill=1;endSize=4;startSize=4;`
- All connectors must use `edgeStyle=orthogonalEdgeStyle;rounded=0;`
- Edge cells MUST contain `<mxGeometry relative="1" as="geometry" />` — self-closing edge cells are invalid
- Prefer plain-text `value` attributes plus `fontColor`, `fontSize`, and `fontStyle` in the cell style. Use inline HTML only when mixed formatting is essential.
- When building XML as a string, escape HTML-formatted values exactly once. When using an XML library such as `xml.etree.ElementTree`, pass the unescaped value and let the serializer escape it; pre-escaping causes literal `<font ...>` markup to appear in the diagram.
- Parse the written file with a real XML parser and reject any visible label containing tag-like text such as `<font`, `&lt;font`, or `<div`.
- Use `container=0;` on area shapes (not draw.io container behavior)
- SAP icons/logos: `shape=image;...;image=data:image/svg+xml,<base64>;` — obtain the exact string from `scripts/sap_shapesearch.py "<name>"`, never hand-write a `mxgraph.sap.icon`/`SAPIcon=` style (it doesn't exist and renders as an empty box).

### Step 4 — Export Draft PNG

Export preview (without `-e` for clean vision-compatible PNG):

```bash
# Windows
"C:\Program Files\draw.io\draw.io.exe" -x -f png -s 2 -o diagram.png diagram.drawio

# macOS/Linux
drawio -x -f png -s 2 -o diagram.png diagram.drawio
```

### Step 5 — Self-Check

Use vision capability to verify the exported PNG:

| Check | What to look for | Auto-fix |
|-------|-----------------|----------|
| Correct SAP colors | Blue `#0070F2` for SAP, Grey `#475E75` for non-SAP | Fix fillColor/strokeColor |
| Area nesting contrast | Alternating fill/no-fill between levels | Toggle fills |
| Overlapping shapes | Shapes stacked | Shift apart by ≥200px |
| Clipped labels | Text cut off | Increase shape dimensions |
| Missing connections | Disconnected arrows | Verify source/target ids |
| Line style consistency | Solid=sync, Dashed=async per legend | Fix dashed attribute |
| Spacing | Even spacing around elements | Adjust to ~50px gaps |
| Unrequested components | Products not present in the allowlist | Remove the component and its edges |
| Wrong service order | Business edge order differs from the requested sequence | Rebuild adjacent edges in the exact order |
| Title-band collision | An icon or label touches an area title | Move all child content below the reserved title band |
| Raw HTML text | `<font ...>` or other markup is visible | Use plain text or correct single escaping |

Before visual review, run `python scripts/validate.py diagram.drawio --strict --score`. Require 0 errors, 0 warnings, and score 0. Also assert the requested service sequence, absence of unrequested products, equal center coordinates for a uniform row, and no intersections among semantic leaf components. Max 2 self-check rounds.

### Step 6 — Review Loop

Show image to user. Apply targeted XML edits per feedback. Loop until approved.
Safety valve: after 5 rounds, suggest opening `.drawio` in draw.io desktop.

### Step 7 — Final Export

Once approved, export with `-e` for embedded diagram:

```bash
# Windows — final PNG with embedded diagram
"C:\Program Files\draw.io\draw.io.exe" -x -f png -e -s 2 -o diagram.drawio.png diagram.drawio

# SVG
"C:\Program Files\draw.io\draw.io.exe" -x -f svg -e -o diagram.drawio.svg diagram.drawio
```

Report file paths. Offer to open: `start diagram.drawio` (Windows).

## Draw.io XML Structure

### File Skeleton (SAP BTP)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" version="26.0.0">
  <diagram name="SAP BTP Architecture">
    <mxGraphModel dx="1400" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="1000" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- L0: BTP Platform boundary (blue fill) -->
        <mxCell id="2" value="" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#0070F2;fillColor=#EBF8FF;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;container=0;" vertex="1" parent="1">
          <mxGeometry x="50" y="80" width="1100" height="650" as="geometry"/>
        </mxCell>
        <!-- Title (separate text cell) -->
        <mxCell id="3" value="&lt;b style=&quot;color:#0070F2;font-size:16px;font-family:arial;&quot;&gt;SAP BTP Solution Diagram&lt;/b&gt;" style="text;html=1;align=left;verticalAlign=middle;resizable=0;points=[];autosize=1;strokeColor=none;fillColor=none;fontColor=#1D2D3E;" vertex="1" parent="1">
          <mxGeometry x="50" y="50" width="260" height="30" as="geometry"/>
        </mxCell>
        <!-- L1: Subaccount (grey border, white fill) -->
        <mxCell id="4" value="Subaccount" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#475E75;fillColor=#ffffff;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;verticalAlign=top;align=left;fontSize=16;fontStyle=1;spacingLeft=10;spacingTop=10;fontColor=#1D2D3E;" vertex="1" parent="1">
          <mxGeometry x="70" y="130" width="500" height="350" as="geometry"/>
        </mxCell>
        <!-- L2: Runtime (blue, inside subaccount) -->
        <mxCell id="5" value="" style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#0070F2;fillColor=#EBF8FF;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;container=0;" vertex="1" parent="1">
          <mxGeometry x="90" y="190" width="460" height="260" as="geometry"/>
        </mxCell>
        <!-- Service with a REAL SAP icon: style obtained via `sap_shapesearch.py "task center"` -->
        <!-- (the image= value is a base64 SVG data URI ~5-8KB long — always copy it verbatim from the script output, never shorten or hand-type it) -->
        <mxCell id="6" value="SAP Task&#xa;Center" style="shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,&lt;BASE64_SVG_DATA_FROM_sap_shapesearch.py&gt;;fontColor=#1D2D3E;" vertex="1" parent="1">
          <mxGeometry x="120" y="220" width="32" height="32" as="geometry"/>
        </mxCell>
        <!-- Non-SAP external system (grey) -->
        <mxCell id="7" value="External System" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F6F7;strokeColor=#475E75;fontColor=#1D2D3E;fontSize=12;strokeWidth=1.5;" vertex="1" parent="1">
          <mxGeometry x="100" y="850" width="160" height="70" as="geometry"/>
        </mxCell>
        <!-- Connector: synchronous (solid blue, strokeWidth=1.5) -->
        <mxCell id="10" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0070F2;strokeWidth=1.5;endArrow=blockThin;endFill=1;endSize=4;startSize=4;" edge="1" parent="1" source="6" target="7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Area Style Patterns (from official examples)

```xml
<!-- L0: BTP Platform (blue border, blue fill, no title bar) -->
style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#0070F2;fillColor=#EBF8FF;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;container=0;"

<!-- L1: Subaccount (grey border, white fill, with title) -->
style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#475E75;fillColor=#ffffff;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;verticalAlign=top;align=left;fontSize=16;fontStyle=1;spacingLeft=10;spacingTop=10;fontColor=#1D2D3E;"

<!-- L2: Runtime/service group (blue border, blue fill) -->
style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#0070F2;fillColor=#EBF8FF;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;container=0;"

<!-- Non-SAP area (grey border, light grey fill) -->
style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#475E75;fillColor=#F5F6F7;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;fontColor=#1D2D3E;"

<!-- Accent area (teal, use sparingly) -->
style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#07838F;fillColor=#DAFDF5;arcSize=24;absoluteArcSize=1;strokeWidth=1.5;fontColor=#1D2D3E;"
```

### Connector Style Patterns (from official examples)

These match the official "Default/Colored Connectors SAP BTP" bundled shapes (verify exact strings anytime with `sap_shapesearch.py "<name> color"` or `"direct one-directional"`, etc.).

```xml
<!-- Default/standard flow (solid grey, thin block arrow) -->
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#475E75;strokeWidth=1.5;endArrow=blockThin;endFill=1;endSize=4;startSize=4;"

<!-- Bidirectional (solid grey, arrows both ends) -->
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#475E75;strokeWidth=1.5;endArrow=blockThin;endFill=1;startArrow=blockThin;startFill=1;endSize=4;startSize=4;"

<!-- No arrow (connection line only) -->
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#475E75;strokeWidth=1.5;endArrow=none;endFill=0;startArrow=none;startFill=0;endSize=4;startSize=4;"

<!-- Asynchronous / indirect (dashed grey) -->
style="edgeStyle=entityRelationEdgeStyle;rounded=0;html=1;strokeColor=#475E75;strokeWidth=1.5;endArrow=blockThin;endFill=1;endSize=4;startArrow=none;startFill=0;startSize=4;jumpStyle=none;jumpSize=0;targetPerimeterSpacing=15;dashed=1;"

<!-- Optional (dotted) -->
style="edgeStyle=entityRelationEdgeStyle;rounded=0;html=1;strokeColor=#475E75;strokeWidth=1.5;endArrow=blockThin;endFill=1;endSize=4;startArrow=none;startFill=0;startSize=4;jumpStyle=none;jumpSize=0;targetPerimeterSpacing=15;dashed=1;dashPattern=1 4;"

<!-- Trust flow (pink / Accent 3) -->
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#CB00DC;strokeWidth=1.5;endArrow=blockThin;endFill=1;endSize=4;startSize=4;"

<!-- Authentication flow (green / success) -->
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#188918;strokeWidth=1.5;endArrow=blockThin;endFill=1;endSize=4;startSize=4;"

<!-- Authorization flow (indigo / Accent 2) -->
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#5D36FF;strokeWidth=1.5;endArrow=blockThin;endFill=1;endSize=4;startSize=4;"

<!-- Firewall / network barrier (thick grey, no arrow) -->
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#475E75;strokeWidth=3;endArrow=none;endFill=0;startArrow=none;startFill=0;"
```

## Export Commands

Two export modes:

- **Preview** (step 4) — no `-e`. Output `diagram.png`. Required for vision self-check.
- **Final** (step 7) — pass `-e`. Output `diagram.drawio.png`. Keeps file editable in draw.io.

```bash
# Windows — Preview
"C:\Program Files\draw.io\draw.io.exe" -x -f png -s 2 -o diagram.png input.drawio

# Windows — Final with embedded diagram
"C:\Program Files\draw.io\draw.io.exe" -x -f png -e -s 2 -o diagram.drawio.png input.drawio

# Windows — SVG
"C:\Program Files\draw.io\draw.io.exe" -x -f svg -e -o diagram.drawio.svg input.drawio

# macOS/Linux
drawio -x -f png -s 2 -o diagram.png input.drawio
drawio -x -f png -e -s 2 -o diagram.drawio.png input.drawio
```

**Key flags:**
- `-x` — export mode (required)
- `-f` — format: `png`, `svg`, `pdf`, `jpg`
- `-e` — embed diagram XML (PNG/SVG/PDF) — file remains editable in draw.io
- `-s` — scale: `1`, `2`, `3` (2 recommended for PNG)
- `-o` — output file path
- `-b` — border width (recommend 10)

## Layout Tips

- Snap all coordinates to **multiples of 10** (draw.io grid)
- Leave ~50-60px spacing around elements (SAP guideline: height of SAP Logo)
- Use **routing corridors** (~80px) between rows/columns for edge routing
- Place hub nodes centrally so edges radiate outward
- Pin `exitX/exitY/entryX/entryY` to distribute connections across shape perimeter
- For multiple connections on same side: space evenly (e.g., 3 on bottom → exitX = 0.25, 0.5, 0.75)
- Always include `orthogonalLoop=1;jettySize=auto` on edges for smart routing
- Leave ≥20px straight segment before arrowheads to avoid overlap with bends
- Reserve a 45-60px title band at the top of every area. Measure child positions from the container's inner top edge and keep the full icon/label bounding boxes below that band.
- Treat icon and label rectangles as indivisible components. Keep a visible gap between every pair; containment inside an area is intentional, component-to-component intersection is not.

### Avoiding Overlapping Connectors

**Connector overlap is a common issue.** When generating diagrams with many connections, apply these rules:

1. **Pin exit/entry points** — always set explicit `exitX`, `exitY`, `entryX`, `entryY` on connectors to control exactly where they leave/arrive at shapes. Without these, draw.io auto-routes all edges through the same point.
2. **Distribute across perimeter** — for N connections from one shape, distribute exit points: e.g., for 3 connections from the bottom, use `exitX=0.25`, `exitX=0.5`, `exitX=0.75` (never all at `exitX=0.5`).
3. **Use waypoints** — for complex routing, add intermediate `mxPoint` waypoints inside `<Array as="points">` to force edges through specific corridors.
4. **Stagger vertical spacing** — place elements with many connections at different Y-levels to give connectors room to route without crossing.
5. **Separate flow types visually** — use different sides of shapes for different flow types (e.g., data flows exit bottom, auth flows exit right).
6. **Prefer an area-level connector for grouped targets** — if S/4HANA and SuccessFactors are both inside one "SAP Cloud Solutions" area, connect Integration Suite once to the area boundary instead of drawing separate fan-out lines to every logo.
7. **Place external targets in a side column** — align the external area horizontally with the integration hub, as in SAP reference diagrams. Do not put a shared destination below the hub when that creates vertical trunks, branches, or label crossings.

### Connectors Must NOT Cross Through Containers

**Lines must never visually pass through (overlap) a container they are not connecting to.** This is a common issue when vertical lines from one service pass through a lower container.

To prevent crossing:
1. **Check the X/Y corridor of each connector** — trace the full path (with all bends) and verify it doesn't intersect any container's bounding box.
2. **Position containers to avoid line corridors** — if a connector goes straight down at X=800, no container should span that X value in the connector's Y range.
3. **Example fix**: Integration Suite (IS) at center X=804 sends a vertical line down to S/4HANA. If Cloud Identity Services (CIS) is positioned at x=330-630 (right edge=630), then X=804 > 630 → the vertical line passes to the RIGHT of CIS → no crossing.
4. **Verify ALL segments** — orthogonal connectors have horizontal and vertical segments. Check EACH segment independently:
   - Vertical segment at X=V: ensure no unrelated container spans that X at the segment's Y range
   - Horizontal segment at Y=H: ensure no unrelated container spans that Y at the segment's X range

### Straight & Uniform Lines (Minimize 90° Bends)

**Lines should be straight and uniform. Zero bends is preferred; one 90-degree bend is the normal maximum.** Two or more bends are allowed only when a documented obstacle makes them unavoidable.

To achieve straight lines:

1. **Align elements by center coordinates** — if two elements should have a straight connector between them, ensure they share the same X center (for vertical lines) or same Y center (for horizontal lines). Example:
   - Business User label center X=125 and App Clients icon center X=125 → straight vertical line (0 bends)
   - App Clients, Document AI, Integration Suite, and S/4HANA icon/logo centers all at Y=190 → one straight horizontal corridor (0 bends)
   - Integration Suite center Y=190 and the left-side entry of a right-hand SAP Cloud Solutions area at Y=190 → straight horizontal line (0 bends)

2. **Design layout AROUND the connector geometry** — decide which connectors must be straight first, then position elements to satisfy those constraints. Don't place elements arbitrarily and hope auto-routing produces straight lines.

3. **Enforce a bend budget before generating XML:**
   - 0 bends: source and target share X center (vertical) or Y center (horizontal)
   - 1 bend: source and target are offset; pin one explicit `mxPoint` at the intended corner
   - 2+ bends: reject and reposition elements unless an obstacle makes the extra bends unavoidable

4. **Position the User icon** to vertically align with its direct downstream target (typically Application Clients). The User should NOT be offset horizontally from App Clients.

5. **Do not trust automatic orthogonal routing for offset elements.** Auto-routing commonly creates two doglegs. When one bend is intended, add exactly one waypoint and verify the resulting vertical and horizontal segments.

### Connector Label Clearance & Arrow Placement

**A connector must never pass through an icon label, product name, or area title.** Labels have a visual footprint outside the icon's `mxGeometry`, so geometry-only collision checks are not enough.

Rules:
1. For connector-bearing icons, prefer an **icon cell with `value=""` plus a separate text cell** below it.
2. If a vertical connector must continue below an icon, start it from the **bottom edge of the separate label cell**, not from the icon's bottom edge. This prevents the line from crossing the label.
3. Keep horizontal connectors on the icon centerline and labels below the icon. Pin `exitY=0.5` and `entryY=0.5`.
4. Add `sourcePerimeterSpacing` / `targetPerimeterSpacing` (typically 4-8px) so arrowheads stop outside the icon artwork rather than covering it.
5. Leave at least 20px of straight line before an arrowhead. Never place a bend immediately beside an icon or label.
6. For a user-to-client stack, use: User icon -> separate User label -> straight connector -> Application Clients icon -> separate client label.
7. For Integration Suite to external cloud systems, place the external area to the **right** and connect horizontally to the area boundary. Do not route downward through the Integration Suite label.

### SAP Cloud Identity Services Placement

**CIS must be OUTSIDE the Subaccount but INSIDE BTP.** This reflects the actual architecture where identity services are provisioned at the BTP level, not within a specific subaccount.

Placement rules:
1. Position CIS group **below the Subaccount** (e.g., Subaccount bottom=300, CIS top=350) but within the BTP boundary
2. Place CIS to the **LEFT** side of BTP so that vertical connectors from Integration Suite (typically on the right) do not pass through it
3. Verify: CIS right edge < IS center X, so IS vertical lines never cross CIS
4. **CIS container fill color**: Use **white fill** (`fillColor=#ffffff`) with **grey border** (`strokeColor=#475E75`) — CIS is a direct child of BTP (blue fill), so it follows the alternating fill pattern: blue (BTP) -> white (CIS/Subaccount) -> blue (Services inside Subaccount) -> white (next level)
5. **CIS -> Subaccount connection**: Add an **OIDC** trust connection (green dashed, bidirectional) from CIS to the Subaccount. This represents the authentication trust configuration (IAS acts as IdP via OpenID Connect). For identity provisioning flows, use a separate **SCIM 2.0** connector (IPS replicates users/groups). **SAML 2.0 is NOT used** for modern multi-environment BTP Subaccount trust — SAML only applies to upstream corporate IdP federation (e.g., Active Directory → IAS) or legacy Neo environments.
6. **Do NOT** use a box container around the CIS icon if CIS is the only service in the group — the group container with title is sufficient.

### Application Clients Presentation

**Application Clients (Mobile / Desktop) should be shown as a standalone icon with label, NOT wrapped in a container box.** The icon already contains the mobile/desktop visual — adding a container around it is redundant and clutters the diagram.

Rules:
1. Use the App Clients icon from the `"Application and User"` component group (first `shape=image` match)
2. Set the icon's `value=""` and add a separate text cell below it with `value="Application Clients&#xa;Mobile / Desktop"`
3. Connect horizontal data flows from the icon's side (`exitY=0.5`), not through its text label
4. If an authentication flow must leave downward, start it from the bottom of the separate label cell
5. Do NOT add a separate container/area shape around it — the icon and label are the element

### Outlook + Document AI Pattern (Exact-Sequence L2 Baseline)

Use this baseline when the request specifies:
`Business User -> Microsoft Outlook -> SAP Document AI -> SAP Integration Suite -> SAP S/4HANA Cloud`.

1. **User/App lane (left):**
   - Reserve a title band inside the Third-Party Application area before placing the Business User icon.
   - Keep `Business User` icon centered above `Application Clients` icon.
   - Use a separate `Business User` label cell and route the vertical connector from `user-label` bottom (`exitX=0.5;exitY=1`) to `app-clients-icon` top (`entryX=0.5;entryY=0`).
   - For Outlook scenarios, set Application Clients label to `Application Clients&#xa;Microsoft Outlook (Desktop)` (or mobile equivalent).

2. **Service lane (inside Subaccount):**
   - Keep the complete business-flow row on one horizontal centerline:
     `Application Clients` -> `SAP Document AI` -> `SAP Integration Suite` -> `SAP S/4HANA Cloud`.
   - Use horizontal connectors only (`exitY=0.5`, `entryY=0.5`) between adjacent services.
   - Do not insert SAP Build Work Zone. Outlook submits the document to Document AI first; Document AI sends extracted/enriched data to Integration Suite.

3. **Posting lane (right):**
   - Place `SAP S/4HANA Cloud` in a right-side `SAP Cloud Solutions` area aligned with the service row.
   - Connect `SAP Integration Suite -> SAP S/4HANA Cloud` horizontally.
   - Post only to the target named by the user. Do not add SuccessFactors or fan out to unrelated systems.

4. **CIS authentication lane (below Subaccount):**
   - Keep `SAP Cloud Identity Services` below Subaccount, left side of BTP.
   - `Application Clients -> CIS`: green dashed, label `OIDC authentication`.
   - `CIS <-> Subaccount`: green dashed, **bidirectional**, label `OIDC trust`.
   - Route these auth connectors in a lower corridor so they do not cross service/data connectors.
   - This depicts IAS-based OpenID Connect authentication/trust. Show SCIM 2.0 separately only when identity provisioning is requested.

5. **No-overlap hard checks:**
   - No component rectangle may intersect another component rectangle.
   - No child icon/label may enter its container's title band.
   - No connector may intersect `Business User` / `Application Clients` text cells or cross another connector.
   - Give every checked connector explicit ports and at least one waypoint so `validate.py --strict --score` can inspect its route.
   - If overlap appears, reposition nodes first, then pin ports, then add at most one routing bend.

### Diagram Title Placement

**The diagram title must not be blocked by any container border.** Place the title text element:
1. **Above** the BTP area's top edge (e.g., title at y=10, BTP area at y=50)
2. OR **inside** the BTP area with enough spacing from the border (at least 10px padding)
3. Never let the title text overlap with a container's stroke/border line

### When Lines Should vs. Should Not Overlap

**Prefer one connector to a shared destination area.** If individual target connections are required, they may share a deliberate trunk and split once in clear space. Lines to different areas or with different semantics must not overlap.

| Scenario | Should overlap? | Rationale |
|----------|----------------|-----------|
| IS -> S/4HANA and IS -> SuccessFactors inside one "SAP Cloud Solutions" area | USE ONE AREA CONNECTOR | A single straight IS -> Cloud Solutions boundary arrow is cleaner than a fan-out |
| Data flow (App -> first requested service) and Auth flow (App -> CIS) | NO | Different destination areas and different flow types |
| Multiple services connecting to the same integration hub | CONDITIONAL | Share a trunk only when it is intentional and splits outside all labels |
| A connector from outside BTP and one inside BTP | NO | Different architectural layers |

Routing order for grouped destinations:
1. First choice: one connector from the hub to the destination area boundary
2. Second choice: one shared trunk with a single split point in empty space
3. Last choice: separate connectors, using distinct ports and non-overlapping corridors

### Area Nesting Fill Pattern (Alternating Colors)

**Always alternate between blue fill and white fill when nesting areas:**

```
L0: BTP Platform (blue border #0070F2, blue fill #EBF8FF)
  L1: Subaccount (grey border #475E75, white fill #ffffff)
    L2: Services group (blue border #0070F2, blue fill #EBF8FF)
  L1: Cloud Identity Services (grey border #475E75, white fill #ffffff)
```

**The rule**: Each nested level alternates: blue -> white -> blue -> white. A direct child of a blue-filled container MUST have white fill (not blue-on-blue). This applies to ALL containers at the same nesting level.

### Legend Placement

**The legend MUST NOT overlap with any connector line or element.** Follow these rules:

1. **Place the legend in an empty corner** — typically bottom-right or bottom-left, whichever has no connectors passing through it.
2. **Check for connector paths** — before placing the legend, trace all connector routes. The legend must not intersect any of them.
3. **Safe positions:**
   - Bottom-right corner (recommended): usually free since most flows go left-to-right and top-to-bottom
   - Below the main diagram area entirely
   - Inside a blank region with no crossing lines
4. **Never place the legend** between source and target elements where connectors route through.


### Browser fallback (no CLI needed)

When the draw.io desktop CLI is unavailable, generate a client-side viewer URL:

```bash
python3 <this-skill-dir>/scripts/encode_drawio_url.py input.drawio
```

Prints a `https://viewer.diagrams.net/...` URL with the diagram XML deflate-compressed and base64-encoded into the URL fragment. The fragment (after `#`) is never sent to the server, so nothing is uploaded — the diagram opens client-side for viewing and editing. Useful when the user cannot install the desktop app.

### Fallback chain

When tools are unavailable, degrade gracefully:

| Scenario | Behavior |
|----------|----------|
| draw.io CLI missing, Python available | Use browser fallback (diagrams.net URL) |
| draw.io CLI missing, Python missing | Generate `.drawio` XML only; instruct user to open in draw.io desktop or diagrams.net manually |
| draw.io CLI crashes / no output in macOS sandbox isolation | Treat CLI as unavailable in-sandbox; use browser fallback / XML-only; ask user to run CLI exports in a non-sandboxed host environment |
| Vision unavailable for self-check | Skip self-check (step 5); proceed directly to showing user the exported PNG |
| Export fails (Chromium/display issues) | On Linux, retry with `xvfb-run -a`; if still failing, deliver `.drawio` XML and suggest manual export |
| Export fails on Linux server (headless) | Try in order: (1) `xvfb-run -a`, (2) append `--no-sandbox` at the very end if root, (3) add `--disable-gpu`, (4) `export HOME=/tmp`, (5) install apt deps (`libgtk-3-0 libnotify4 libnss3 libgbm1 libasound2t64` etc.), (6) fall back to [tomkludy/drawio-renderer](https://hub.docker.com/r/tomkludy/drawio-renderer) Docker (REST API for headless export) |

### Checking if draw.io is in PATH

```bash
# Try short command first
if command -v draw.io &>/dev/null; then
  DRAWIO="draw.io"
elif [ -f "/Applications/draw.io.app/Contents/MacOS/draw.io" ]; then
  DRAWIO="/Applications/draw.io.app/Contents/MacOS/draw.io"
else
  echo "draw.io not found — install from https://github.com/jgraph/drawio-desktop/releases"
fi
```

## Common Mistakes

When something looks wrong (export fails, vision rejects a PNG, layout broken, edges misroute), see `references/troubleshooting.md` for a row-by-row mistake → fix table.
