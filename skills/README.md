# Skills

Portable instruction packages in the [Agent Skills format](https://agentskills.io/specification).

| Skill | Purpose |
| --- | --- |
| [bluesky-bot](bluesky-bot/SKILL.md) | Reliable data-driven bots, post design, procedural avatars, account setup, and state-preserving deployment. |
| [chicago-data-portal](chicago-data-portal/SKILL.md) | Chicago open data with Socrata/SODA and SoQL. |
| [cook-county-data-portal](cook-county-data-portal/SKILL.md) | Cook County property, finance, court, and health data. |
| [gridstatus-api](gridstatus-api/SKILL.md) | Electricity-grid data and energy calculations. |
| [housing-copywriter](housing-copywriter/SKILL.md) | Clear copy and pro-housing messaging. |
| [us-census-data](us-census-data/SKILL.md) | Census demographics, income, housing, and population. |

Install a selected skill:

```bash
npx skills add MisterClean/ai-plugins --skill bluesky-bot
```

Each skill directory contains its required `SKILL.md` plus the resources it needs.
Copy the entire directory for manual installation. See [installation and compatibility](../README.md#installation) and [contribution guidance](../CONTRIBUTING.md).
