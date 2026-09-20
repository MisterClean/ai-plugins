# AI Plugins

Reusable skills for AI coding agents, published in the open [Agent Skills format](https://agentskills.io/specification). Each skill is a self-contained directory with a `SKILL.md` entrypoint and supporting resources.

The shared content is model- and harness-neutral. A compatible harness loads the instructions and supplies its own tools, permissions, and runtime. This repository distributes skills; plugin marketplaces, browser automation, hooks, and tool servers have separate harness-specific contracts. There is no claim that every harness supports the same tools or installation path.

## Available skills

| Skill | Purpose |
| --- | --- |
| [bluesky-bot](skills/bluesky-bot/SKILL.md) | Build reliable data-driven Bluesky bots, iterate on posts and maps, generate profile artwork, configure accounts, and preserve state through deployments. |
| [chicago-data-portal](skills/chicago-data-portal/SKILL.md) | Discover and query Chicago open data using Socrata/SODA and SoQL. |
| [cook-county-data-portal](skills/cook-county-data-portal/SKILL.md) | Query Cook County property, finance, court, and health datasets. |
| [gridstatus-api](skills/gridstatus-api/SKILL.md) | Query electricity-grid load, pricing, generation, forecasts, and energy data. |
| [housing-copywriter](skills/housing-copywriter/SKILL.md) | Write clear copy and pro-housing advocacy messaging. |
| [us-census-data](skills/us-census-data/SKILL.md) | Query Census demographics, housing, income, and population data. |

## Installation

The [Skills CLI](https://github.com/vercel-labs/skills) discovers the `skills/` directory and installs selected skills for supported agents:

```bash
# Inspect the available skills without installing.
npx skills add MisterClean/ai-plugins --list

# Install one skill; select your agent and scope when prompted.
npx skills add MisterClean/ai-plugins --skill bluesky-bot
```

Node.js/npm is required for this installer, not for reading skill instructions. Review installed skill content before running bundled scripts. See the installer's current supported-agent list for per-harness paths and options.

For manual installation, clone the repository and copy the **entire skill directory** into the skills directory documented by your harness:

```bash
git clone https://github.com/MisterClean/ai-plugins.git
```

For harnesses that support project-scoped `.agents/skills/`, an example is:

```bash
mkdir -p /path/to/project/.agents/skills
cp -R ai-plugins/skills/bluesky-bot /path/to/project/.agents/skills/
```

Other harnesses use different paths. Do not copy only `SKILL.md`: references and helper scripts are part of the skill. Restart or reload skill discovery if your harness requires it. Ask the agent to use `bluesky-bot` by name; explicit invocation syntax and automatic selection depend on the harness.

**Migration:** earlier versions used vendor-specific marketplace packaging. That packaging is removed in version 2.0.0. Reinstall through the skill workflow above and remove the superseded marketplace installation in your harness to avoid duplicate instructions.

## Structure

```text
ai-plugins/
├── AGENTS.md                    # Guidance for agents editing this repository
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md              # Required name, description, instructions
│       ├── references/           # Detailed guidance loaded as needed
│       ├── scripts/              # Optional executable helpers
│       ├── assets/               # Optional output/template assets
│       └── examples/             # Optional worked examples
├── scripts/validate-skills.sh
├── requirements-dev.txt         # Pinned reference validator
├── CONTRIBUTING.md
└── LICENSE
```

Only `SKILL.md` is required inside a skill. Version information lives under its standard `metadata` mapping. Optional resources are included only when useful; there is no vendor manifest required to consume these skills.

## Bluesky bot workflow

Source validation → durable history → semantic events → delivery queue → generated posts/media → publication and receipt reconciliation.

The [Bluesky skill](skills/bluesky-bot/SKILL.md) covers all four publication modes: new records, meaningful changes, periodic observations, and ordered collections. It includes account setup and bios, design review rules, and a reproducible avatar generator. SVG generation needs Python 3.10+; optional PNG export needs CairoSVG, Pillow, and system Cairo. The skill documents these dependencies and browser-tool fallbacks rather than assuming one host application.

## Validation and contributions

```bash
uv run --with-requirements requirements-dev.txt sh scripts/validate-skills.sh
```

This uses the pinned [Agent Skills reference validator](https://github.com/agentskills/agentskills/tree/main/skills-ref). CI runs the same format checks for all skills. Behavioral quality and helper output still need task-specific review; see [CONTRIBUTING.md](CONTRIBUTING.md).

MIT licensed. See [LICENSE](LICENSE).
