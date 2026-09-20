# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-09-20

### Added

- **bluesky-bot**: Source/event architecture, reliable delivery, design iteration, profile/account setup, state-preserving deployment, and a procedural SVG/PNG avatar generator.
- `AGENTS.md` contributor instructions and automated validation using the Agent Skills reference implementation.

### Changed

- Renamed the repository to **ai-plugins** and adopted the open Agent Skills format as the shared distribution contract.
- Updated all skill installation guides to the cross-agent installer and documented manual installation.
- Moved skill versions into the standard `metadata` mapping.
- Made the published Bluesky skill independent of a particular assistant, browser product, or private session archive.

### Removed

- Previous vendor-specific marketplace manifests and install commands. Existing marketplace installations must migrate to the documented skill installation flow.

## [1.0.6] - 2026-01-25

### Changed

- **gridstatus-api** skill (v1.2.0 → v1.3.0): Rewrote to prefer Python SDK over curl
  - **CRITICAL**: Direct curl API has date filtering issues on free tier - returns stale sample data
  - Python SDK correctly handles date parameters and returns current data
  - Simplified skill structure with "Standard Query Template" using heredoc pattern
  - Added "Why Not curl?" section explaining the free tier API limitation
  - Removed curl-first examples; SDK is now the primary method
  - Added uv-based installation for dependency isolation
  - Streamlined troubleshooting table with SDK-first guidance

## [1.0.5] - 2026-01-25

### Changed

- **gridstatus-api** skill (v1.1.0 → v1.2.0): Enhanced for common user questions
  - Added "Quick Answers" section for common questions (energy consumption, current load, dataset discovery)
  - Added prominent "Energy Calculations" section with conversion formulas (MW to MWh)
  - Improved dataset discovery workflow using `/v1/datasets` metadata API
  - Enhanced troubleshooting for Python SDK numpy issues with curl fallback guidance
  - Added `/v1/datasets/{dataset_id}` single dataset metadata endpoint documentation
  - Added energy consumption calculation examples to common-queries.md
  - Added "Most Recent Data Point" query pattern (`order=desc&limit=1`)
  - Documented 455+ available datasets across 10 ISOs
- Updated root README.md with improved gridstatus-api description
- Updated skills/README.md with gridstatus-api feature highlights and meme image

## [1.0.4] - 2026-01-13

### Changed

- **gridstatus-api** skill (v1.0.0 → v1.1.0): Updated based on real-world API testing
  - **CRITICAL FIX**: Corrected API parameter names - use `start_time`/`end_time` for curl, `start`/`end` for Python SDK
  - Added documentation for standardized datasets (`pjm_standardized_hourly`, `pjm_standardized_5_min`)
  - Clarified zone-specific data access via columns (e.g., `load.comed`) not filters
  - Added energy calculation formulas for hourly and 5-minute data
  - Enhanced troubleshooting section with common errors and fixes
  - Added timezone parameter guidance (`timezone="market"` for local time)
  - Documented curl as fallback when Python SDK has dependency issues
  - Added zone-specific load query examples for PJM

## [1.0.3] - 2026-01-13

### Added

- **gridstatus-api** skill: Query electricity grid data from US ISOs via GridStatus.io API
  - SKILL.md with workflow for load, pricing (LMP/SPP), fuel mix, forecasts, and ancillary services
  - Support for all major US ISOs: ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP
  - Support for Canadian markets: IESO (Ontario), AESO (Alberta)
  - EIA national/regional data
  - `references/datasets-by-iso.md`: Complete catalog of 454 datasets organized by ISO
  - `references/api-reference.md`: Full API parameter documentation (filtering, resampling, pagination)
  - `references/common-queries.md`: Ready-to-use query patterns for common analysis tasks
  - `examples/python-query.py`: Python SDK examples using gridstatusio library
  - `examples/curl-examples.sh`: curl command templates for direct API access
  - API key management via GRIDSTATUS_API_KEY in .env file
  - Rate limit guidance (500K rows/month free tier)

### Added

- **Historical marketplace packaging**: Added a harness-specific marketplace and individual manifests. This packaging is superseded by the portable skill distribution in 2.0.0.

- Individual README.md files for each skill with installation instructions, triggers, usage examples, and file contents overview
  - `skills/chicago-data-portal/README.md`
  - `skills/cook-county-data-portal/README.md`
  - `skills/housing-copywriter/README.md`
  - `skills/us-census-data/README.md`

### Changed

- **chicago-data-portal** skill (v1.1.0): Added Prerequisites section with .env API key check
  - Checks for `CHICAGO_DATA_PORTAL_TOKEN` in user's .env file
  - Provides signup instructions if token not found
  - Clarifies that queries work without token but are rate-limited

- **cook-county-data-portal** skill (v1.1.0): Added Prerequisites section with .env API key check
  - Checks for `COOK_COUNTY_DATA_PORTAL_TOKEN` in user's .env file
  - Falls back to `CHICAGO_DATA_PORTAL_TOKEN` (both use Socrata, tokens are interchangeable)
  - Provides signup instructions if neither token found

- **us-census-data** skill (v1.1.0): Standardized Prerequisites section format
  - Moved API key setup to dedicated Prerequisites section for consistency
  - Checks for `CENSUS_API_KEY` in user's .env file
  - Clarifies that API works without key but is rate-limited

### Tested

- Verified all data portal skills with smoke tests:
  - **chicago-data-portal**: Crimes, 311 requests, building permits - all APIs working
  - **cook-county-data-portal**: Assessed values, Medical Examiner, payroll - all APIs working
  - **us-census-data**: ACS state population, county median income - all APIs working

## [1.0.3] - 2026-01-17

### Added

- **housing-copywriter** skill: Write authentic, human-sounding copy that avoids AI-generated patterns
  - SKILL.md with 5 core copywriting principles (specificity, cutting ruthlessly, conversational tone, showing vs announcing, earning adjectives)
  - Self-check framework to prevent AI-sounding output
  - Tone calibration guidance for different contexts (casual, professional, luxury, startup)
  - Pro-housing advocacy messaging framework (5-step housing structure, 3-step parking structure)
  - `references/avoid-list.md`: Comprehensive banned words, phrases, and patterns with alternatives (204 items)
  - `references/pro-housing-messaging.md`: Research-backed YIMBY messaging (Welcoming Neighbors Network, Sightline Institute, Parking Reform Network)
  - Terminology guide for housing advocacy (homes vs units, housing shortage vs crisis, etc.)
  - Top-performing message examples with statistical backing
  - Before/after examples for common copywriting scenarios
  - Specialized guidance for zoning reform, parking reform, and housing affordability communications

## [1.0.2] - 2026-01-13

### Added

- **us-census-data** skill: Query demographic, economic, and housing data from the US Census Bureau API
  - SKILL.md with complete workflow for dataset selection, variable discovery, and query building
  - Support for ACS 5-Year, ACS 1-Year, Decennial Census, and Population Estimates
  - All geography levels (state, county, tract, block group, ZCTA, congressional district, etc.)
  - `references/datasets.md`: Complete dataset documentation with selection guide
  - `references/popular-variables.md`: 100+ curated variables by topic (demographics, income, housing, education, etc.)
  - `references/geographies.md`: Geography hierarchy, FIPS codes, query syntax
  - `references/tigerweb.md`: TIGERweb API guide for boundary geometry retrieval
  - `examples/python-query.py`: Python code using requests + pandas with .env API key loading
  - `examples/curl-examples.sh`: curl command templates for all query scenarios
  - API key management via CENSUS_API_KEY in .env file
  - Margin of error handling guidance for ACS estimates
  - Inspired by tidycensus R package but language-agnostic

## [1.0.1] - 2026-01-13

### Added

- **cook-county-data-portal** skill: Query and download datasets from Cook County Open Data Portal
  - SKILL.md with complete workflow for dataset discovery, querying, and output formatting
  - Progressive disclosure architecture with category-specific reference files
  - `references/datasets-property.md`: Property & Taxation datasets (Assessor, Treasurer)
  - `references/datasets-courts.md`: Courts & Legal datasets (State's Attorney, sentencing)
  - `references/datasets-health.md`: Health & Medical Examiner datasets
  - `references/datasets-finance.md`: Finance & Administration datasets (payroll, procurement)
  - `references/soql-quick-ref.md`: Complete SoQL function reference
  - `examples/python-query.py`: Python code using requests + pandas
  - `examples/curl-examples.sh`: Ready-to-run curl commands
  - Cook County-specific documentation (PINs, townships, fiscal quarters)

### Changed

- Reorganized project structure: skills now live in `skills/` directory
- Added `skills/README.md` as skills index
- Updated all documentation to reflect new structure

## [1.0.0] - 2026-01-13

### Added

- **chicago-data-portal** plugin: Query and download datasets from the City of Chicago Data Portal
  - SKILL.md with complete workflow for dataset discovery, querying, and output formatting
  - Support for both legacy GET and SODA3 POST query patterns
  - Geospatial query support (within_circle, within_box, within_polygon)
  - `references/popular-datasets.md`: 8 verified popular datasets with IDs
  - `references/soql-quick-ref.md`: Complete SoQL function reference
  - `examples/python-query.py`: Python code using requests + pandas
  - `examples/curl-examples.sh`: Ready-to-run curl commands
- Project README with installation and contribution guidelines
- MIT License
- This changelog

[1.0.6]: https://github.com/MisterClean/ai-plugins/releases/tag/v1.0.6
[1.0.5]: https://github.com/MisterClean/ai-plugins/releases/tag/v1.0.5
[1.0.4]: https://github.com/MisterClean/ai-plugins/releases/tag/v1.0.4
[1.0.3]: https://github.com/MisterClean/ai-plugins/releases/tag/v1.0.3
[1.0.2]: https://github.com/MisterClean/ai-plugins/releases/tag/v1.0.2
[1.0.1]: https://github.com/MisterClean/ai-plugins/releases/tag/v1.0.1
[1.0.0]: https://github.com/MisterClean/ai-plugins/releases/tag/v1.0.0

[2.0.0]: https://github.com/MisterClean/ai-plugins
