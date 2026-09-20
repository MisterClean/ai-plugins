#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for entrypoint in skills/*/SKILL.md; do
    skills-ref validate "$(dirname "$entrypoint")"
done
