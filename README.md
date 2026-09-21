# SAP BTP Architecture Diagram Generator

A GitHub Copilot agent skill that generates production-quality **SAP Business Technology Platform (BTP) solution diagrams** following the official [SAP BTP Solution Diagram Design Guideline](https://github.com/SAP/btp-solution-diagrams/tree/main/guideline/docs/btp_guideline) (Horizon theme).

> **Skill ID:** `drawio-skill-sap` · **Version:** 1.0.3
> **Homepage:** [lofonD/SAP-BTP-Architecture-Diagram-Generator](https://github.com/lofonD/SAP-BTP-Architecture-Diagram-Generator)

## What You Get

- Editable, uncompressed `.drawio` files
- Official SAP service icons and product logos from the bundled shape library
- L0, L1, or L2 diagrams for different audiences
- Structural validation for IDs, nesting, geometry, and connector routing
- Optional PNG, SVG, PDF, or JPG exports through the draw.io desktop CLI
- Optional browser previews through the official [`@drawio/mcp`](https://www.drawio.com/doc/faq/drawio-mcp.html) server

The skill can create and validate `.drawio` files without draw.io desktop. The desktop app is required only for image or PDF export.

## Quick Start

### 1. Install the skill

<details>
<summary><strong>Clone</strong></summary>

Clone this repository and place `skills/drawio-skill-sap` in an Agent Skills location recognized by your Copilot environment, such as `.github/skills/drawio-skill-sap` in the repository where you want to use it.

```bash
git clone https://github.com/lofonD/SAP-BTP-Architecture-Diagram-Generator.git
```
</details>

<details>
<summary><strong>Skills CLI</strong></summary>

Install via Skills CLI

```bash
npx skills add lofonD/SAP-BTP-Architecture-Diagram-Generator --skill drawio-skill-sap
```
</details>

### 2. Start using the skill

Open Chat in Agent mode and ask for a diagram:

```text
/drawio-skill-sap Create an L1 BTP diagram for SAP Build Work Zone,
Integration Suite, SAP S/4HANA Cloud, and SAP SuccessFactors.
```

You can also use a natural-language request:

```text
Create an L2 SAP BTP architecture diagram showing Integration Suite
connecting to SAP S/4HANA Cloud through Cloud Connector, with SAP Cloud
Identity Services handling authentication.
```

If no level is specified, the skill asks once and defaults to L1.

**Diagram generated:**

![Example SAP BTP architecture diagram](https://github.com/user-attachments/assets/29f0d68f-69ea-4c55-aad0-bdfb73626fcd)

### 3. Validate the result

Python 3 is required for the bundled scripts; they use only the standard library.

```bash
python skills/drawio-skill-sap/scripts/validate.py diagram.drawio --strict --score
```

Strict validation returns a nonzero exit code for errors or warnings, making it suitable for CI.

### 4. Export the diagram (optional)

Install [draw.io desktop](https://github.com/jgraph/drawio-desktop/releases), then export with its CLI:

```powershell
# Windows: high-DPI PNG with editable diagram XML embedded
& "C:\Program Files\draw.io\draw.io.exe" -x -f png -e -s 2 -o diagram.png diagram.drawio
```

```bash
# macOS / Linux
drawio -x -f png -e -s 2 -o diagram.png diagram.drawio
```

Use `-f svg`, `-f pdf`, or `-f jpg` for another output format. The `-e` flag embeds the source diagram in supported exports so it can be reopened in draw.io.

## Diagram Levels

| Level | Audience | Typical content |
|---|---|---|
| **L0** | Business stakeholders | Platform boundaries, core systems, and simple flows |
| **L1** | Architects and solution owners | Subaccounts, major services, integrations, and selected semantic flows |
| **L2** | Implementation teams | Runtimes, services, trust and authentication paths, protocols, and a full legend |

## Design Rules

The skill applies SAP's atomic design approach rather than treating the diagram as a collection of generic boxes:

- Named SAP services use official SAP icons or product logos.
- BTP, subaccount, runtime, and external-system boundaries use nested Horizon areas.
- Grey is the default connector color; semantic colors are reserved for specific flow meanings.
- Solid, dashed, and dotted lines distinguish direct, indirect, and optional flows.
- Structural validation catches broken references, invalid nesting, overlaps, and explicit routing defects.

### Horizon palette

| Purpose | Border / line | Fill |
|---|---|---|
| SAP/BTP area | `#0070F2` | `#EBF8FF` |
| Non-SAP or external area | `#475E75` | `#F5F6F7` |
| Authentication | `#188918` | `#F5FAE5` |
| Authorization | `#5D36FF` | `#F1ECFF` |
| Trust | `#CB00DC` | `#FFF0FA` |
| Warning | `#C35500` | `#FFF8D6` |
| Error | `#D20A0A` | `#FFEAF4` |
| Highlight | `#07838F` | `#DAFDF5` |

### Connector semantics

| Style | Meaning |
|---|---|
| Solid | Direct or synchronous flow |
| Dashed | Indirect or asynchronous flow |
| Dotted | Optional flow |
| Thick grey, no arrow | Firewall or network barrier |

For the complete generation rules, see [`skills/drawio-skill-sap/SKILL.md`](skills/drawio-skill-sap/SKILL.md).

## Included Tools

Run these commands from the repository root.

### Find an SAP shape

```bash
python skills/drawio-skill-sap/scripts/sap_shapesearch.py "integration suite"
python skills/drawio-skill-sap/scripts/sap_shapesearch.py "cloud identity" --format json
python skills/drawio-skill-sap/scripts/sap_shapesearch.py --list-categories
```

The search returns exact styles from the bundled SAP shape library. `shapesearch.py` provides a generic draw.io fallback when no SAP shape matches.

### Build from a JSON layout spec

`sap_build.py` turns a compact JSON specification into uncompressed `.drawio` XML and resolves SAP icons by name:

```bash
python skills/drawio-skill-sap/scripts/sap_build.py spec.json -o diagram.drawio
python skills/drawio-skill-sap/scripts/sap_build.py --find "cloud integration"
```

See the script's module documentation for the supported node types, edge kinds, and specification format.

### Validate a diagram

```bash
python skills/drawio-skill-sap/scripts/validate.py diagram.drawio --strict --score
python skills/drawio-skill-sap/scripts/validate.py diagram.drawio --format json
```

### Preview without draw.io desktop

Generate a diagrams.net URL from a local file:

```bash
python skills/drawio-skill-sap/scripts/encode_drawio_url.py diagram.drawio
```

The optional `.vscode/mcp.json` configuration starts the official draw.io MCP server with `npx -y @drawio/mcp`. It can open XML in the browser, but SAP shape lookup still belongs to `sap_shapesearch.py`, and file export still requires draw.io desktop.

## Repository Contents

```text
skills/drawio-skill-sap/
|-- SKILL.md                       # Agent instructions and design rules
|-- references/
|   |-- drawio-sap-config.json     # Bundled SAP shape library
|   |-- *.drawio                   # Official reference patterns
|   `-- troubleshooting.md
`-- scripts/
    |-- sap_build.py               # JSON spec to .drawio builder
    |-- sap_shapesearch.py         # SAP shape lookup
    |-- shapesearch.py             # Generic draw.io shape lookup
    |-- validate.py                # Structural linter
    |-- encode_drawio_url.py       # Browser-preview URL generator
    `-- repair_png.py              # Repair truncated PNG IEND chunks
```

Bundled examples cover SAP Task Center at L0/L1/L2, SAP Start, SAP Build Work Zone, SAP Cloud Identity Services, SAP Private Link Service, and a broader BTP reference architecture.

## Troubleshooting

For common XML, icon, layout, routing, and export issues, see [`skills/drawio-skill-sap/references/troubleshooting.md`](skills/drawio-skill-sap/references/troubleshooting.md).

## References

- [SAP BTP Solution Diagrams](https://github.com/SAP/btp-solution-diagrams)
- [SAP BTP Solution Diagram Design Guideline](https://github.com/SAP/btp-solution-diagrams/tree/main/guideline/docs/btp_guideline)
- [draw.io desktop releases](https://github.com/jgraph/drawio-desktop/releases)
- [draw.io Agent Skill base project](https://github.com/Agents365-ai/drawio-skill)

## License

See [LICENSE](LICENSE) if present. SAP shape assets are subject to [SAP's IP and usage terms](https://github.com/SAP/btp-solution-diagrams).
