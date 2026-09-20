# Bluesky adapter and protocol checks

Checked against official source on 2026-09-20. Recheck the relevant live Lexicons, installed SDK validation, and client behavior when implementing or updating limits. Repository history contained obsolete 1 MB image limits and older video limits. Do not treat historical examples as the current specification.

## Payload limits and links

| Surface | Verified rule | Source |
|---|---|---|
| Post | TID key; text up to 300 graphemes and 3,000 UTF-8 bytes; `createdAt` required | [Post Lexicon](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/feed/post.json) |
| Standard image embed | Up to 4 images; each up to 2,000,000 bytes; alt required; aspect ratio supported | [Images Lexicon](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/images.json) |
| Profile | Display name 64 graphemes / 640 bytes; bio 256 graphemes / 2,560 bytes; PNG/JPEG avatar/banner each up to 1,000,000 bytes | [Profile Lexicon](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/actor/profile.json) |
| First-party client | Post-image target maximum dimension 4,000 px; alt editor limit 2,000; these are client choices, not all protocol limits | [Client constants](https://github.com/bluesky-social/social-app/blob/main/src/lib/constants.ts) |

The post Lexicon also supports a gallery embed. Do not infer that the four-image standard embed is a universal limit across all media types. Check gallery/client support if a task needs more images. Check current video upload limits, account eligibility, and processing APIs separately rather than hardcoding a remembered duration.

Use `app.bsky.richtext.facet` link annotations on final plain text. Offsets are UTF-8 byte offsets, end-exclusive—not character counts or UTF-16 offsets. With an SDK, use its rich-text helpers; otherwise compute bytes after final formatting. Test emoji and accented names before the link. Post body Markdown syntax does not create a named link. See [official rich-text guide (archived repository)](https://github.com/bluesky-social/bsky-docs/blob/main/docs/advanced-guides/post-richtext.md).

## Authentication and account identity

Use a dedicated bot account and a revocable app password for this personal bot workflow, with direct-message access disabled unless needed. Reuse and refresh persisted sessions instead of logging in every tick. Save rotated access/refresh tokens atomically to private files and never log authentication payloads, token-bearing URLs, or response bodies containing secrets.

Resolve the account DID and PDS during authentication; a user need not manually obtain a DID before development. Pin/check the expected account identity before publishing. Handles are mutable; a renamed handle does not warrant a new baseline or delivery namespace. Route writes and reconciliation to the authoritative PDS, not a lagging AppView. Keep identities and credentials in configuration rather than embedded in reusable code.

Bluesky recommends labeling automated accounts and opt-in interaction with other users; a broadcast bot need not like, follow, mention, or reply to strangers. Persist session refreshes, not only the initial login. [Official bot guidance (archived repository)](https://github.com/bluesky-social/bsky-docs/blob/main/docs/starter-templates/bots.mdx).

## Durable publishing algorithm

1. Claim an eligible delivery and load its stable event/account/part identity.
2. If a remote key already exists, reconcile it **before** expensive rendering or uploading. A prior confirmed delivery remains sent even if a human later deletes the post; never recreate it automatically.
3. For unprepared work, render the approved facts, prepare/upload required media, and persist its returned blob references, text, facets, alt, aspect ratios, timestamp, template/style, and valid TID before the first record write. Persist the payload the retry will actually use.
4. Use a supported record write with that key. For guarded `putRecord`, explicit JSON `swapRecord: null` means create only if absent; omission permits overwrite. Verify the serializer preserves the explicit null. Do not send unconditional overwrites as a retry strategy. See the [PDS implementation](https://github.com/bluesky-social/atproto/blob/main/packages/pds/src/api/com/atproto/repo/putRecord.ts), [putRecord Lexicon](https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/putRecord.json) and [AT Protocol repository operations](https://atproto.com/specs/repository).
5. After success, persist URI/CID and completion atomically. After timeout, lost response, or conflict, read that key on the PDS. If the record matches the frozen expected value, confirm it locally. If confirmed absent and retry is appropriate, reuse the exact key and payload. If different or still unreadable, hold or retry reconciliation within bounds; do not allocate another key.
6. Media blobs can need recovery if never referenced by a completed record. Retain/reconstruct the exact prepared bytes under a bounded retention policy and preserve their content identity; do not substitute a newly rendered image for an uncertain attempt.

A generic valid record key is insufficient for `app.bsky.feed.post`: it specifically requires a TID. Both Divvy and Buoys encountered this in live tests. Use a tested TID library/allocator and persist allocation; do not invent a UUID or hash syntax, or derive a different current-time TID on retry. This provides idempotent recovery, not a blanket exactly-once guarantee across independent systems.

## Thread parts

Each root and reply has a distinct durable TID, payload, and receipt. A reply needs `root` and `parent` strong references, each with the actual URI and CID. First reply: both reference the root. Further chained replies: root remains original, parent is the preceding post. Never guess a CID or rebuild the root on reply failure.

Make media failure policy explicit. ADU required its Street View card and deferred the announcement if missing; Divvy allowed unavailable Street View while retrying actual reply-send failures. Neither behavior is universal. Record a permanent optional-media skip separately from retryable media/API failure.

## Verification ladder

- Pure text/media preview: no social credentials or remote writes.
- Local mock adapter: limits, Unicode facets, auth rotation, same-key retries, mismatched remote record, crash after remote success, partial thread.
- Auth check: correct DID/PDS, no post.
- Authorized bounded live fixture: inspect stored record plus public presentation, facets, alt, image order, reply links, and playback when applicable. Repeat the fixture via the same persisted identity to test recovery, not by inventing fresh posts.

Keep real test receipts. Do not remove posts just because they have no engagement; use the current user's deletion instructions. A live test authorized for one account or task is not standing authorization for future skills.
