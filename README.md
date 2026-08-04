# SAP BTP Architecture Diagram Generator

A GitHub Copilot agent skill that generates production-quality **SAP Business Technology Platform (BTP) solution diagrams** following the official [SAP BTP Solution Diagram Design Guideline](https://github.com/SAP/btp-solution-diagrams/tree/main/guideline/docs/btp_guideline) (Horizon theme).

> **Skill ID:** `drawio-skill-sap` · **Version:** 1.5.3
> **Homepage:** [lofonD/SAP-BTP-Architecture-Diagram-Generator](https://github.com/lofonD/SAP-BTP-Architecture-Diagram-Generator)

---

## What It Does

Describe your SAP architecture in plain language and the agent generates:

- A `.drawio` file with the correct SAP Horizon colors, nested areas, official SAP icon/logo shapes, and semantically-colored connectors
- A rendered PNG, SVG, or PDF export via the draw.io desktop CLI

The skill enforces the SAP atomic design system — no plain boxes for named services, no hand-written icon styles, no off-palette colors.

---

## Prerequisites

**draw.io desktop app** must be installed and on your PATH:

```bash
# Windows
"C:\Program Files\draw.io\draw.io.exe" --version

# macOS
drawio --version

# Linux
draw.io --version
```

Download from [jgraph/drawio-desktop/releases](https://github.com/jgraph/drawio-desktop/releases) if missing.

**Optional:** Download the official SAP shape libraries from [SAP/btp-solution-diagrams](https://github.com/SAP/btp-solution-diagrams/tree/main/assets/shape-libraries-and-editable-presets/draw.io) to use service icons with grey background circles in the draw.io desktop app.

---

## Supported Platforms

| Platform | CLI binary |
|----------|-----------|
| Windows  | `draw.io.exe` |
| macOS    | `draw.io` / `drawio` |
| Linux    | `draw.io` / `drawio` |

---

## Supported Output Formats

| Format | Flag | Notes |
|--------|------|-------|
| PNG    | `-f png` | Default; `-s 2` recommended for high-DPI |
| SVG    | `-f svg` | Vector; scales without loss |
| PDF    | `-f pdf` | Print-ready |
| JPG    | `-f jpg` | Lossy; use when file size matters |

Add `-e` to the final export to embed the diagram XML inside the PNG/SVG/PDF so the file stays editable in draw.io.

---

## Diagram Levels of Detail

| Level | Description | Typical use |
|-------|-------------|-------------|
| **L0** | High-level context (platform boundaries only) | Executive overview |
| **L1** | Subaccount topology | Architecture review |
| **L2** | Full detail — runtimes, services, connectors, auth flows | Implementation spec |

---

## SAP Horizon Design System

### Color Palette

| Purpose | Border | Fill |
|---------|--------|------|
| SAP/BTP areas | `#0070F2` | `#EBF8FF` |
| Non-SAP / external areas | `#475E75` | `#F5F6F7` |
| Authentication flow | `#188918` | `#F5FAE5` |
| Authorization flow | `#5D36FF` | `#F1ECFF` |
| Trust flow | `#CB00DC` | `#FFF0FA` |
| Warning | `#C35500` | `#FFF8D6` |
| Error | `#D20A0A` | `#FFEAF4` |
| Accent (teal) | `#07838F` | `#DAFDF5` |

### Area Nesting Pattern

```
L0: BTP Platform   (blue border #0070F2, blue fill #EBF8FF)
  L1: Subaccount   (grey border #475E75, white fill #ffffff)
    L2: Service group (blue border #0070F2, blue fill #EBF8FF)
```

### Connector Semantics

| Line style | Meaning |
|------------|---------|
| Solid      | Direct / synchronous |
| Dashed     | Indirect / asynchronous |
| Dotted     | Optional flow |
| Thick grey | Firewall / network barrier |

---

## Bundled Reference Diagrams

| File | Pattern |
|------|---------|
| `references/SAP_Task_Center_L0.drawio` | Task Center — context level |
| `references/SAP_Task_Center_L1.drawio` | Task Center — subaccount level |
| `references/SAP_Task_Center_L2.drawio` | Task Center — full detail |
| `references/SAP_Start_L2.drawio` | SAP Start |
| `references/SAP_Build_Work_Zone_L2.drawio` | SAP Build Work Zone |
| `references/SAP_Build_Process_Automation_L2.drawio` | SAP Build Process Automation |
| `references/SAP_Cloud_Identity_Services_Authentication_L2.drawio` | Cloud Identity — authentication |
| `references/SAP_Cloud_Identity_Services_Authorization_L1.drawio` | Cloud Identity — authorization |
| `references/SAP_Cloud_Identity_Services_Identity_Lifecycle_L1.drawio` | Cloud Identity — identity lifecycle |
| `references/SAP_Private_Link_Service_L2.drawio` | SAP Private Link connectivity |
| `references/BTP_Reference_Architect_Diagram.svg` | BTP overall reference pattern |

---

## Bundled Scripts

| Script | Purpose |
|--------|---------|
| `sap_shapesearch.py` | Look up exact `style=` strings for any SAP icon, product logo, container template, or connector from the official shape library |
| `shapesearch.py` | Search the full draw.io generic shape index |
| `autolayout.py` | Graph JSON → auto-placed `.drawio` (Graphviz-based) |
| `validate.py` | Lint a `.drawio` file for style, XML, and guideline errors |
| `repair_png.py` | Fix truncated IEND chunks in draw.io PNG exports |
| `encode_drawio_url.py` | Generate a diagrams.net browser-fallback URL (when CLI unavailable) |
| `explain.py` | Convert a `.drawio` to a Markdown description |
| `drawio2pptx.py` | Export `.drawio` to a PowerPoint deck |
| `drawio2mermaid.py` | Convert `.drawio` to Mermaid diagrams-as-code |
| `restyle.py` | Re-theme a diagram (dark, corporate, colorblind-safe) |
| `compress.py` | Compress a complex diagram into an exec-summary view |
| `heatmap.py` | Colour a diagram by a metrics data file |
| `timelapse.py` | Animate how an architecture evolved over git history |
| `drawiodiff.py` | Show what changed between two diagram versions |
| `buildup.py` | Animate a diagram building itself (HTML player / GIF) |
| `prdiff.py` | Render before/after/diff for `.drawio` files in PRs |
| `c4.py` | Generate a C4 model with drill-down links |
| `seqlayout.py` | Generate a UML sequence diagram |
| `tubemap.py` | Draw a London-Underground-style metro/tube map |
| `runbook.py` | Convert a decision tree into a click-through HTML runbook |
| `sqlerd.py` | Generate an ER diagram from a SQL schema |
| `openapiimports.py` | Generate an API diagram from an OpenAPI spec |
| `ciimports.py` | Generate a pipeline DAG from CI workflow files |
| `tfimports.py` / `tfstate.py` | Generate infrastructure diagrams from Terraform |
| `k8simports.py` | Generate cluster diagrams from Kubernetes manifests |
| `composeimports.py` | Generate service diagrams from Docker Compose |
| `pyimports.py` / `jsimports.py` / `goimports.py` / `rustimports.py` | Module import graphs |
| `pyclasses.py` | Python class-inheritance graph |
| `raster2drawio.py` | Convert a whiteboard photo or legacy PNG to editable `.drawio` |
| `svgflow.py` | Animate data flows on a diagram as an SVG |
| `drawiohtml.py` | Wrap a `.drawio` in an interactive HTML viewer |
| `aiicons.py` | Look up draw.io image styles for AI/LLM brand logos |
| `relabel.py` | Extract labels → translate → reapply (multilingual diagrams) |
| `edgeports.py` | Inspect or fix connector exit/entry port assignments |

---

## Usage Examples

### Basic BTP diagram

> "Generate an L2 SAP BTP architecture diagram showing Integration Suite connecting to S/4HANA Cloud via the Cloud Connector, with Cloud Identity Services for authentication."

The agent will:
1. Clarify any missing details (services, detail level, on-premise systems)
2. Look up every service icon with `sap_shapesearch.py`
3. Write the `.drawio` XML following the Horizon design system
4. Export a preview PNG and show it for review
5. Apply feedback edits until approved
6. Produce the final PNG/SVG with embedded diagram XML

### Search for a shape style

```bash
python scripts/sap_shapesearch.py "integration suite"
python scripts/sap_shapesearch.py "cloud identity"
python scripts/sap_shapesearch.py --list-categories
```

### Validate a diagram

```bash
python scripts/validate.py my-diagram.drawio --strict --score
```

### Export a diagram

```bash
# Windows — PNG preview
"C:\Program Files\draw.io\draw.io.exe" -x -f png -s 2 -o diagram.png diagram.drawio

# Windows — final PNG with embedded XML
"C:\Program Files\draw.io\draw.io.exe" -x -f png -e -s 2 -o diagram.drawio.png diagram.drawio

# SVG
"C:\Program Files\draw.io\draw.io.exe" -x -f svg -e -o diagram.drawio.svg diagram.drawio

# macOS/Linux
drawio -x -f png -e -s 2 -o diagram.drawio.png diagram.drawio
```

---

## References

- [SAP BTP Solution Diagrams (official)](https://github.com/SAP/btp-solution-diagrams)
- [draw.io Skill (base)](https://github.com/Agents365-ai/drawio-skill)
- [draw.io Desktop Releases](https://github.com/jgraph/drawio-desktop/releases)
- [`references/xml-authoring.md`](skills/drawio-skill-sap/references/xml-authoring.md) — XML authoring guide
- [`references/diagram-types.md`](skills/drawio-skill-sap/references/diagram-types.md) — Supported diagram types
- [`references/shapes.md`](skills/drawio-skill-sap/references/shapes.md) — Shape reference
- [`references/style-presets.md`](skills/drawio-skill-sap/references/style-presets.md) — Style presets
- [`references/troubleshooting.md`](skills/drawio-skill-sap/references/troubleshooting.md) — Common issues and fixes
- [`skills/drawio-skill-sap/references/toolbox.md`](skills/drawio-skill-sap/references/toolbox.md) — Full script reference

---

## License

See [LICENSE](LICENSE) if present. SAP shape assets are subject to [SAP's IP and usage terms](https://github.com/SAP/btp-solution-diagrams).
