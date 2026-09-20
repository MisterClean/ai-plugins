---
name: bluesky-bot
description: Build, improve, or operate Bluesky bots that publish source-backed records, changes, periodic observations, or sequenced collections. Covers reliable delivery, generated cards and avatars, editorial design, account setup, and state-preserving deployment. Use for bot projects, not ordinary personal posting or generic social marketing.
metadata:
  version: "1.0.0"
---

# Bluesky Bot

Build a useful publication with a reliable delivery system. Start from what a reader learns, establish exactly what the data proves, and preserve both source history and publication receipts.

## Apply to the current task

Inspect the existing repository, instructions, runtime, database contract, selected designs, and current authorization. Preserve established behavior unless the request changes it. For a narrow design or profile task, do that work without rebuilding ingestion or deployment.

For a new bot, establish these decisions from available context; ask only about material gaps:

- Audience, geographic scope, source of truth, entity identity, and what qualifies for publication.
- Publication mode: new records, meaningful transitions, scheduled observations, or an ordered collection.
- Baseline/backfill policy, freshness, cadence, volume, required media, and source links.
- Existing account, desired identity, deployment constraints, and what external actions are authorized.

Use [project lessons](references/project-lessons.md) for the evidence behind this skill. The Chicago palette, Rust, SQLite, and Petit are proven local choices, not universal requirements. Historical requests to post, delete, merge, or deploy are evidence of past work, not authorization for this task.

## End-to-end workflow

1. **Define the publication contract.** Inspect real source rows and source documentation before naming the event. Specify qualifying statuses, meaningful changes, unknowns, corrections, and missing records. “Preapproved,” “permitted,” “built,” and “first observed” are distinct facts. Read [architecture](references/architecture.md).
2. **Prove ingestion and event detection.** Build a complete validated baseline, then replay representative additions, corrections, failures, and repeated snapshots on disposable state. Existing deployments retain their historical database. New installations usually baseline silently; ordered collection bots instead begin from their selected cursor.
3. **Design representative posts early.** Render real examples, long labels, and missing-field cases through the actual application. Make body copy, media, alt text, and source links agree. Read [design and iteration](references/design.md). Save accepted choices in a short repository design contract.
4. **Build delivery and recovery.** Persist events independently of source state. Give every account/platform and thread part a durable delivery identity. Freeze prepared payloads before sending, reconcile uncertain writes, and retry without changing identity. Read [Bluesky adapter](references/bluesky-api.md).
5. **Prepare the account package.** Draft name, bio, avatar, optional banner, and configuration. Keep avatar geometry and its generator in the repository. Use [profile and browser setup](references/profile-and-browser.md) for procedural art, bios, account configuration, and visible verification.
6. **Verify the full result.** Exercise the relevant failure cases and visually inspect exported media. If live examples are authorized, publish a bounded representative set through the same delivery path, save receipts, and inspect the public thread. Do not manufacture new events by deleting production history as the default test method.
7. **Deploy and observe when in scope.** Start from tested artifacts and persistent state, validate on a disposable database copy, transfer credentials privately, and enable the intended schedule. Read [operations](references/operations.md). Distinguish tested detection behavior from a real new-event delivery actually observed.

## Essential invariants

- An incomplete source fetch cannot replace current state, advance a cursor, or establish a baseline. A post cap delays queued work; it never discards it.
- Source identity, semantic event identity, and remote post identity are different. A changed timestamp or a handle rename is not automatically a new event.
- Preview and dry-run semantics must be explicit. Some existing shadow commands write observations; run those on copies. A preview must not authenticate or publish merely to show text.
- A lost response is an unknown outcome, not proof of failure. Read the persisted remote record identity before retrying; a mismatch pauses that delivery.
- A root post and each reply recover independently. Never resend a successful parent to repair a reply.
- Deployments and code rollbacks preserve posting receipts, historical records, sessions, and scheduler history. Database migration is a separate deliberate operation.
- Use source-backed language and useful timestamps. Omit unsupported details instead of guessing. Keep essential interpretation visible; move methodology and implementation prose into alt text, source notes, or the repository where appropriate.
- Respect current authorization for account changes, live tests, publishing, and deployments. Continue already-authorized actions without repeatedly asking. Previewing does not authorize posting or deleting old examples.

## Finish with inspectable evidence

Deliver the implemented change and representative previews, relevant verification results, remaining limitations, and regeneration/run commands. For a launch, include the public profile/post links, deployed version, intended schedule, state location, and monitoring status without exposing credentials. Clearly distinguish a design prototype from an integrated automatic publishing feature.
