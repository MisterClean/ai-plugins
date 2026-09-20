# GridStatus API

<p align="center">
  <img src="../../assets/aicnua.jpg" alt="I know the American electricity grid" width="400">
</p>

Query real-time and historical electricity grid data from US Independent System Operators (ISOs) via the GridStatus.io API. Access load, pricing (LMP), generation, fuel mix, forecasts, and ancillary services data from 455+ datasets.

## Triggers

Use this skill when you ask your agent to:
- "get electricity data"
- "query grid data"
- "get LMP prices"
- "fetch load data"
- "get fuel mix"
- "query ERCOT data"
- "query CAISO data"
- "query PJM data"
- "get electricity prices"
- "analyze grid operations"
- "how much electricity was consumed"

Or when you mention electricity market data (load, generation, pricing, LMP, fuel mix, ancillary services, etc.).

## Installation

```bash
npx skills add MisterClean/ai-plugins --skill gridstatus-api
```

Select your supported agent and install scope when prompted. For manual installation,
copy this entire folder into your harness's documented skills directory. See the
[repository installation guide](../../README.md#installation) for compatibility details.


## API Key Setup

The GridStatus API requires an API key:

1. Create a free account at https://www.gridstatus.io
2. Go to Settings to get your API key
3. Add to your `.env` file: `GRIDSTATUS_API_KEY=your_key_here`

**Free tier limits:** 500,000 rows per month, 250 requests max.

## Usage

Once installed, ask your agent naturally:

> "What's the current load in ERCOT?"

> "How much electricity was consumed in PJM in the last hour?"

> "Get real-time LMP prices for the Western Hub"

> "Show me CAISO's fuel mix for yesterday"

A compatible agent can use this skill to find the right dataset, construct the API query, and calculate energy consumption when needed.

## Supported ISOs

| ISO | Region | Example Datasets |
|-----|--------|------------------|
| ERCOT | Texas | `ercot_load`, `ercot_spp_*`, `ercot_fuel_mix` |
| CAISO | California | `caiso_load`, `caiso_lmp_*`, `caiso_fuel_mix` |
| PJM | Mid-Atlantic/Midwest | `pjm_load`, `pjm_lmp_*`, `pjm_standardized_*` |
| MISO | Midwest | `miso_load`, `miso_lmp_*` |
| NYISO | New York | `nyiso_load`, `nyiso_lmp_*` |
| ISO-NE | New England | `isone_load`, `isone_lmp_*` |
| SPP | Southwest/Central | `spp_load`, `spp_lmp_*` |

## Contents

| File | Description |
|------|-------------|
| [SKILL.md](./SKILL.md) | Core instructions, workflow, and energy calculation formulas |
| [references/api-reference.md](./references/api-reference.md) | Full API parameter documentation |
| [references/common-queries.md](./references/common-queries.md) | Ready-to-use query patterns |
| [references/datasets-by-iso.md](./references/datasets-by-iso.md) | Complete catalog of 455+ datasets |
| [examples/curl-examples.sh](./examples/curl-examples.sh) | Sample curl commands |
| [examples/python-query.py](./examples/python-query.py) | Python SDK examples |

## Resources

- [GridStatus.io](https://www.gridstatus.io) - API provider
- [GridStatus Documentation](https://docs.gridstatus.io) - Official API docs
- [gridstatusio Python SDK](https://pypi.org/project/gridstatusio/) - Python client library
- [Main Repository](../../README.md)
