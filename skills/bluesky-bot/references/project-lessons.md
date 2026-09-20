# Evidence and scope of the lessons

Reviewed 2026-09-20: 25 primary development sessions across the four example projects, focusing on user decisions, final results, relevant implementation evidence, and current checked-out documentation. Approval-review transcripts and duplicated internal agent histories were excluded from the primary-session count. Older assistant claims were checked against later corrections and current files; a session saying “deployed” is historical evidence, not a fresh production audit.

This skill is a synthesis, not an export of private logs. It includes no credentials, host addresses, production snapshots, or original attachments. Project names describe the requested local projects; Divvy's GitHub/application name later became `chicago-bikeshare-bot`.

## What changed the guidance

| Evidence | Reusable lesson | Scope |
|---|---|---|
| Divvy's first audit found source rows saved before publication and caps losing events | Atomically queue events separately from sending; caps leave pending work | Core reliability |
| Divvy and Buoys live tests rejected generic record keys | Validate the post-specific TID key and retain it across retries | Bluesky requirement |
| Divvy preview used wrong basemap and stale logo from an older branch | Render current accepted assets with real dependencies; disclose substitutes | Design process |
| Divvy small smoke viewport distorted layout | Keep logical viewport separate from pixel density | Rendering |
| Divvy selected Civic/Nightline, then tuned shade, zoom, marker, transit and POIs | Compare controlled variants; persist selected style; save design decisions | Iteration; style choices remain local |
| Divvy's later user changes replaced Divvy branding with Bikeshare and removed watermark | Later accepted choices supersede older logo/headline guidance | Avoid fossilizing early work |
| ADU requests initially called the data “permits” | Inspect source semantics and distinguish preapproval from permits/completion | Factual contract |
| ADU dynamic type/count and timing copy | Conditional language derives from real fields; adjusted dates need care | Editorial logic |
| ADU procedural avatar uses shared paths for SVG and PNG | Preserve a code-generated vector master and reproducible upload file | Profile art |
| ADU map selection removed many explanatory captions | Keep graphics concise; preserve source/provenance in appropriate supporting places | Design preference, not permission to mislead |
| ADU selected second-post maps exist as a preview, not an integrated automatic feature | Distinguish an approved prototype/manual test from production integration | Delivery scope |
| Buoys latest feed was stale while camera was updated | Independent freshness and eligibility for measurements/media | Observation bots |
| Buoys wording iterated toward metric emojis and timestamp + named source link | Improve scan order; do not repeatedly expose raw URLs or implementation text | Editorial preference |
| Buoy-camera terms explicitly restricted redistribution | Availability is not permission; verify that specific source and gate that media | Source-specific, not universal approval checklist |
| EveryLot city-only strings passed address checks | Validate components and identity; authoritative centroid/PIN fallback | Data quality |
| EveryLot/Divvy retained historical DBs through Rust and scheduler migrations | Switch code separately; preserve IDs/cursors/receipts, avoid DB rollback | Operations |
| ADU polls source six-hourly but worker runs every 15 minutes | Polling, editorial, and delivery/retry clocks differ | Scheduling |

## Public implementation examples

- [Chicago ADU preapprovals](https://github.com/MisterClean/chicago-adu-permits): source/status contract, native card renderer, procedural avatar, map-design review, deployment notes.
- [Chicago Buoys](https://github.com/MisterClean/chicago-buoys): quality-controlled observations, freshness, editorial lanes, camera permissions, delivery recovery.
- [EveryLot Chicago](https://github.com/MisterClean/everylotbot-chicago): ordered parcel publishing, address/centroid fallback, historical cursor and delivery preservation.
- [Chicago Bikeshare Bot](https://github.com/MisterClean/chicago-bikeshare-bot): inventory transitions, persistent style choices, native map rendering, threaded media and account rename.

These are examples rather than runtime dependencies. Inspect their current code before borrowing implementation details; the projects continue to evolve. The source review included 7 ADU, 2 Buoys, 4 EveryLot, and 12 Bikeshare development sessions. Private session identifiers and local paths are intentionally omitted from this public package.

## Deliberate generalizations and limits

The architecture, iterative review rules, and avatar workflow are directly grounded in the projects. The bundled four-motif generator is newly authored reusable tooling inspired by the ADU approach; it is not the original project generator. Biography examples and the consolidated account-registration/checklist are new guidance: the logs demonstrate account reuse, app-password creation, avatar upload, and handle-change verification, not a complete observed signup for all four accounts.

Do not generalize historical live-test permission, requests to remove production rows, or assistant deletion of zero-engagement posts into default behavior. Do not copy old credentials or host-specific settings. A specific unresolved camera license is a reason to resolve that media source, not a reason to hold all other bot work. Provider and trademark claims require checking the relevant current terms if they matter to a future task.
