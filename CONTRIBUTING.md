# Contributing to AI Plugins

Add focused skills or improve existing ones using the [Agent Skills specification](https://agentskills.io/specification).

## Add a skill

Create `skills/<skill-name>/SKILL.md`. Names use lowercase letters, digits, and hyphens and match the parent directory. Use valid YAML frontmatter:

```yaml
---
name: example-skill
description: Explain what the skill does and when an agent should use it.
metadata:
  version: "1.0.0"
---

# Example Skill

Instructions that help an agent perform the task well.
```

Required fields are `name` and `description`. Versions belong in the optional standard `metadata` mapping. Describe real capabilities and meaningful trigger conditions; do not rely on exact phrase matching. Keep detailed or conditional guidance in linked `references/` files and bundle helpers/examples only when they improve execution.

Keep the directory self-contained and portable. Use relative resource paths, capability-based tool instructions, explicit helper dependencies, and fallbacks for unavailable tools. Do not require one assistant product, private session logs, or machine-specific paths. Skills do not grant permission to post, deploy, access accounts, or transmit data.

## Validate the result

Run the same reference-format validation as CI:

```bash
uv run --with-requirements requirements-dev.txt sh scripts/validate-skills.sh
```

Without uv, use a virtual environment with Python 3.11+:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
PATH="$PWD/.venv/bin:$PATH" sh scripts/validate-skills.sh
```

Then inspect relative links, execute new/changed helpers on representative fixtures, and review observable results. Format validation does not prove that instructions make good decisions. Test discovery in a compatible harness or list the catalog without installing:

```bash
npx skills add . --list
```

Do not use production credentials or modify live accounts as part of routine validation. Keep examples free of secrets and unnecessary personal data.

## Submit

Update the root skill catalog, `skills/README.md`, and `CHANGELOG.md`. Use semantic versions in each changed skill's `metadata.version`; changes to shared distribution should include migration notes. Open a pull request explaining the user-facing capability and relevant validation.

Keep scope focused: packaging work should preserve unrelated domain guidance. When updating an API workflow, verify endpoints and field names against current authoritative sources. Be respectful and constructive in reviews.
