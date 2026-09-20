# US Census Data

Query demographic, economic, housing, and population data from the US Census Bureau API. Supports American Community Survey (ACS), Decennial Census, and Population Estimates.

## Triggers

Use this skill when you ask your agent to:
- "get Census data"
- "query American Community Survey"
- "find ACS data"
- "get population by state"
- "query Decennial Census"
- "find Census variables"
- "get median income data"
- "download demographic data"

Or when you mention US Census Bureau data (demographics, income, poverty, education, housing, population estimates, etc.).

## Installation

```bash
npx skills add MisterClean/ai-plugins --skill us-census-data
```

Select your supported agent and install scope when prompted. For manual installation,
copy this entire folder into your harness's documented skills directory. See the
[repository installation guide](../../README.md#installation) for compatibility details.


## API Key Setup

The Census API requires a key for production use:

1. Register at https://api.census.gov/data/key_signup.html
2. Add to your `.env` file: `CENSUS_API_KEY=your_key_here`

## Usage

Once installed, ask your agent naturally:

> "Get median household income by county for Illinois"

> "What's the population of Chicago by census tract?"

> "Find poverty rates for all states from ACS 5-year"

A compatible agent can use this skill to select the right dataset, find variable codes, and construct the API query.

## Contents

| File | Description |
|------|-------------|
| [SKILL.md](./SKILL.md) | Core instructions and workflow |
| [references/datasets.md](./references/datasets.md) | Available Census datasets |
| [references/geographies.md](./references/geographies.md) | Geography levels and FIPS codes |
| [references/popular-variables.md](./references/popular-variables.md) | Common variable codes |
| [references/tigerweb.md](./references/tigerweb.md) | Geographic boundary data |
| [examples/curl-examples.sh](./examples/curl-examples.sh) | Sample curl commands |
| [examples/python-query.py](./examples/python-query.py) | Python query example |

## Resources

- [Census API Documentation](https://www.census.gov/data/developers/guidance.html)
- [Census Data Explorer](https://data.census.gov)
- [Main Repository](../../README.md)
