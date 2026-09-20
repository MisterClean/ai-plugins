# Cook County Data Portal

Query and download datasets from the Cook County Open Data Portal using the Socrata Open Data API (SODA) and SoQL.

## Triggers

Use this skill when you ask your agent to:
- "query Cook County data"
- "find Cook County datasets"
- "get property assessments"
- "download parcel data"
- "search datacatalog.cookcountyil.gov"
- "get medical examiner data"
- "find court cases"
- "query State's Attorney data"

Or when you mention Cook County government data (assessor, treasurer, courts, payroll, medical examiner, etc.).

## Installation

```bash
npx skills add MisterClean/ai-plugins --skill cook-county-data-portal
```

Select your supported agent and install scope when prompted. For manual installation,
copy this entire folder into your harness's documented skills directory. See the
[repository installation guide](../../README.md#installation) for compatibility details.


## Usage

Once installed, ask your agent naturally:

> "Get the assessed value for PIN 14-08-203-015-0000"

> "Find all medical examiner cases from last year"

> "Query property tax appeals in Northfield township"

A compatible agent can use this skill to discover datasets, build SoQL queries, and retrieve the data.

## Contents

| File | Description |
|------|-------------|
| [SKILL.md](./SKILL.md) | Core instructions and workflow |
| [references/datasets-property.md](./references/datasets-property.md) | Assessor, Treasurer, parcel data |
| [references/datasets-courts.md](./references/datasets-courts.md) | State's Attorney, sentencing |
| [references/datasets-health.md](./references/datasets-health.md) | Medical Examiner cases |
| [references/datasets-finance.md](./references/datasets-finance.md) | Payroll, procurement, budgets |
| [references/soql-quick-ref.md](./references/soql-quick-ref.md) | SoQL syntax reference |
| [examples/curl-examples.sh](./examples/curl-examples.sh) | Sample curl commands |
| [examples/python-query.py](./examples/python-query.py) | Python query example |

## Resources

- [Cook County Data Portal](https://datacatalog.cookcountyil.gov)
- [SODA API Documentation](https://dev.socrata.com/)
- [Main Repository](../../README.md)
