# Repository guidance

This repository publishes portable Agent Skills. Keep domain instructions independent of model vendors and host applications; describe required capabilities and fallbacks instead of inventing a universal plugin API.

## Layout and metadata

- Store each skill at `skills/<name>/SKILL.md`, with a lowercase, hyphenated directory/name match.
- Follow https://agentskills.io/specification. Required frontmatter: `name` and `description`. Put version strings in `metadata.version`, not an unsupported top-level `version` field.
- Keep the entrypoint focused. Link task-specific detail in `references/`; bundle scripts, examples, or assets only when useful.
- Keep a skill usable when its whole directory is copied independently. Do not require local session archives, private paths, credentials, or optional vendor UI metadata.
- Preserve existing domain behavior during packaging/documentation edits. Check source/API claims when changing them; packaging validation is not a domain-data audit.

## Editing and validation

- Read a skill and its referenced resources before changing it. Keep user authorization separate from capabilities a skill describes.
- Update the root catalog, `skills/README.md`, relevant installation guidance, and `CHANGELOG.md` when adding/removing skills or changing distribution.
- Validate with `uv run --with-requirements requirements-dev.txt sh scripts/validate-skills.sh`.
- Run changed helpers with representative local fixtures and inspect generated files. Use disposable state and no live account writes for routine validation.
- Check relative links and scan outgoing changes for secrets and machine-specific paths. Keep application data, tokens, sessions, and generated scratch work out of Git.
- Changes to supported installation contracts must include migration instructions. Do not introduce a vendor-specific marketplace as the portable core.
