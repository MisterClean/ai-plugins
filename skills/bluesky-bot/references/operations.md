# Deployment, migration, and operation

## Fit the actual environment

Inspect the existing runtime, scheduler, database version/path, credentials mechanism, logs, memory, and disk before planning a cutover. Reuse the user's provider. Rust binaries and one shared Petit scheduler worked well for the memory-constrained Chicago host; do not mandate them for every deployment or replace a working stack during a narrow change.

One-shot sequential work usually saves more memory than choosing a fashionable framework. Bound decompressed HTTP bodies, pages, geometry, database cache, pixels, and temporary media. Stream large CSV/video data and release source snapshots before rendering. Native CPU rendering avoids a browser but has a different cartographic fidelity contract. A smaller browser controller does not remove Chromium's rendering memory. Separate a heavy render worker if the required visual cannot fit the polling worker's budget.

Measure realistic Linux runs, including render/upload and overlapping scheduled jobs. A small offline audit RSS does not prove live rendering will fit. Build on CI, not on a tiny production machine. Avoid exact runtime/tool versions from old logs; use the target repository's current constraints.

## Separate code from state

Illustrative layout, configurable to the existing host:

```text
/opt/example-bot/releases/<commit>/    immutable executable and public assets
/opt/example-bot/current              atomic release pointer
/var/lib/example-bot/                 SQLite, session, durable prepared payloads
/etc/example-bot/                     protected config/credentials
/var/log/example-bot/                 persistent logs (or system journal)
```

Keep scheduler history separate too. Release cleanup must target only old release artifacts; never wildcard-delete state, logs, or unrelated services. Retain public documentation and selected reproducible samples in Git; exclude databases, backups, sessions, tokens, private configuration, research dumps, and machine-specific host details. A sample environment file must contain placeholders only.

A practical CI/CD flow is required checks → build exact commit → publish checksummed immutable artifact → host updater validates artifact and candidate → atomic switch → health verification. Fit existing branch/environment approval policy; do not add or remove approval gates unless authorized. A main merge can trigger deployment: inspect workflow behavior before merging.

## Cutover and migration

- Identify active runtime rather than trusting an old checkout. Record schema version, entity/event/delivery counts, cursor, schedule, and deployed version.
- Serialize deployments against worker runs. Pause only the relevant writer/schedule when needed, accounting for other bots sharing a scheduler.
- Make a SQLite-consistent backup using its backup API or an appropriate coordinated snapshot; copying only the main file during WAL writes is insufficient. Validate the backup.
- Run candidate checks on a disposable copy, with social writes disabled. Some `shadow`/`dry-run` commands ingest or update health state; read-only promises must be verified, not inferred from names. For strict no-change checks, compare the source copy checksum plus logical history.
- Preserve IDs, event keys, valid remote keys, frozen payloads, chosen styles, receipts, and cursor semantics. A historical database already carrying sent receipts is the production starting point, even if created locally before the first deployment.
- Default ordinary runs to opening an existing production DB. Use explicit initialization for new installations. Unknown schemas fail clearly.
- If schema changes are required, use a versioned transactional migration with backup and tested compatibility. “Preserve state” allows an authorized additive migration; it does not allow reimporting or resetting history.
- Transfer existing credentials via the authorized private channel, independently of releases. Respect actual config loading. If a backup command intentionally disables publishing in the copy, explicitly review/clear that state during authorized cutover.
- Switch the tested code artifact, verify health and the next intended run, then enable the schedule/publication as authorized. Recheck the effective timezone, missed-run behavior, and per-run limits.

Rollback normally changes code only. Restoring an old DB after new posts would erase receipts and invite duplicates. If a schema rollback is unavoidable, reconcile remote records and preserve newer history before any destructive recovery.

## Health and delivery pacing

Expose machine-readable status plus useful human output: last successful complete source scan, source observation age, last attempted/successful worker run, queue age and counts, holds/reasons, uncertain records, consecutive errors, scheduler state, release version, and storage headroom. “No new posts” can be healthy when no new events exist; a healthy process can still have stale data.

Decouple source failures, renderer failures, account pauses, and delivery errors. Health monitoring should notify on meaningful failures or action needed rather than repeat unchanged status. A source error shared by old and new versions should not automatically trigger code rollback. A bounded, paced backlog recovery should drain pending work without dropping events or flooding followers.

Daily backups are useful only with tested restore/reconciliation and an off-host retention plan appropriate to the project. State plainly if only local backups exist. A profile redesign is not an occasion to enable monitoring infrastructure unrelated to the request.

## Acceptance evidence

Verify baseline/replay behavior, pending delivery preservation, remote-write recovery, thread-part recovery, credentials isolation, selected render quality, target-platform build, and applicable migration invariants. If deployment is authorized, observe a real scheduler invocation and inspect status/logs. Distinguish a successful zero-event cycle from a delivered new-event post. Do not delete a production entity or receipt just to trigger a smoke test unless that exact operation is explicitly requested and planned; prefer a disposable DB and controlled fixture with a saved delivery identity.
