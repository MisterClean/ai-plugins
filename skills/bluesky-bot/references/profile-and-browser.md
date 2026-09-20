# Profile identity, procedural avatars, and browser setup

## Prepare a concrete profile package

Draft a recognizable display name, a stable handle candidate (verify availability only when network/account access is in scope), a concise bio, an avatar, and an optional banner. The identity should describe the publication and avoid implying an official account. Put detailed methodology, sources, code, and operating caveats behind a repository/site link. Keep account rename, repository rename, runtime identifier, and on-disk state path as separate decisions.

Bio formula: **what is published + geographic/source scope + automation/unofficial status + source/code link or essential qualification**. Mention cadence only when it is dependable. Example drafts, not copied live bios:

- “Chicago ADU preapprovals from city data. Automated, unofficial. Requested homes—not building permits or completed construction. Data & code: [URL]”
- “Lake Michigan observations near Chicago: water, waves and weather. Automated, unofficial; readings may be delayed. Sources & code: [URL]”
- “New and newly electrified Chicago bikeshare stations observed in city inventory. Automated, unofficial. Availability varies. Data & code: [URL]”
- “A tour of Chicago parcels in PIN order, with Street View context. Automated, unofficial. Sources & code: [URL]”

Replace `[URL]` with a real chosen link and re-count before saving. Do not insert Markdown link syntax into the bio. Check the current profile limits in [API guidance](bluesky-api.md). If the UI has a website field, use it to free biography space. A short profile is often better than mechanically filling the limit.

## Procedural avatar workflow

For an icon-like identity, favor editable vector geometry. The ADU precedent generated a six-point red star inside a blue coach-house outline, with SVG and PNG derived from the same paths. It used an opaque white background for consistent appearance in dark/light UI.

1. Choose one subject motif—house, buoy/waves, parcel, or bicycle—and one civic accent if appropriate. Avoid tiny lettering, detailed maps, and several competing emblems.
2. Use a normalized square coordinate system, named palette tokens, and shared path definitions. Keep the whole silhouette and strokes inside a circular safe area. Optically center the mass, not only the bounding box.
3. Generate SVG with title/description and no linked fonts/images. Use explicit paths for stars rather than an unreliable font glyph. A Chicago-style six-point star can be constructed from 12 alternating radii at 30° intervals, inner/outer ratio 3/7; verify official geometry when exact conformance matters.
4. Rasterize the **same SVG**, preferably supersampled then downsampled, to a 1024-square PNG as a working export. Verify against the separate avatar byte limit (not the larger post-image limit). SVG is the editable master; PNG/JPEG is the profile upload.
5. Inspect at 32, 48, 96, and full size with a circular crop in light/dark contexts. Simplify details that collapse at small sizes. Adjust geometry in the generator and regenerate both formats together.
6. Commit the source/generator, selected SVG/PNG, and one regeneration command in the project's existing docs. Do not require the original assistant session, temporary screenshot, or remote font to rebuild it.

The bundled helper is a starting point, not a mandatory visual identity:

```sh
python3 scripts/generate_avatar.py --motif house --name 'Example bot' --out /path/to/project/assets/profile
```

Run it relative to this skill directory, or use its absolute path. It writes `avatar.svg`, an inspectable `avatar-preview.html`, and a parameter manifest. Add `--png` with CairoSVG and Pillow available to rasterize the same SVG to `avatar.png` and enforce the 1,000,000-byte profile budget. For an isolated dependency environment: `uv run --with cairosvg --with pillow python scripts/generate_avatar.py --motif house --name 'Example bot' --out /path/to/project/assets/profile --png`. CairoSVG also needs the platform's Cairo library; if unavailable, generate SVG only and use the project's renderer. Inspect the PNG as well as the SVG: a rasterizer can report success while omitting stroked paths. Alternatives are the project's existing SVG renderer (such as resvg/tiny-skia or sharp). `--motif` supports `house`, `buoy`, `parcel`, and `bike`; colors and title are configurable; `--star` opts into the six-point Chicago-style accent. Omit it for identities where that motif is inappropriate. Copy/adapt the helper into the target repository if used. The preview HTML is review material; the selected artwork and generator are the durable assets.

If the user requests photographic or painterly artwork, use the available image-generation workflow instead of forcing vector motifs. Never substitute generated art for factual source imagery.

## Account setup with browser automation

Use the available browser-automation tool documentation and observed page state; labels and navigation change. Follow its current requirements for file uploads, credential creation, account verification, and terms acceptance; past session approvals do not bypass action-specific requirements. Honor the user’s selected browser/tab. Otherwise find the intended existing Bluesky session or open `https://bsky.app/` with the available browser tools. If no browser tool is available, finish local preparation and give the user the concrete account-setup steps; do not claim the profile was updated. Do not assume that the currently logged-in account is the intended bot.

Typical sequence, adapted to the actual UI:

1. Confirm the visible handle/account switcher against the intended account. Reuse an existing logged-in bot account. If registration is requested, follow the visible signup flow with the user's supplied details; let the user complete CAPTCHA, verification, or missing private information. Never invent personal account details.
2. Open the profile editor. Save the agreed display name and bio and upload the PNG avatar. Inspect and adjust the circular crop, save, refresh, and verify the public result. Only add a banner when useful/requested, and inspect its mobile crop and avatar overlap.
3. Find the automated-account setting and enable the bot label within the authorized account-setup scope. If an authorized API update is needed instead, read the existing `app.bsky.actor.profile/self`, preserve its other fields and labels, merge the `bot` self-label, and write with a current-record guard. Do not replace the whole profile with a minimal example.
4. For credentials, use the account's App Passwords settings (commonly `https://bsky.app/settings/app-passwords`). Create a descriptively named password for this bot/environment if needed, with DM access off. Store it directly in the authorized ignored/protected configuration; do not echo it into chat, docs, logs, or commits. Avoid capturing screenshots of the revealed credential.
5. Verify ignore rules **and tracked files**: `.gitignore` does not protect an already tracked secret. Check authentication with the app's no-post diagnostic. Verify DID/PDS and persist a protected session. Do not assume `.env` loads automatically; inspect the CLI/config contract.
6. Check relevant profile/settings such as website and public visibility to fit the requested publication. Do not mass-follow accounts, alter unrelated preferences, or enable DMs as a side effect of setup.
7. After an authorized handle change, update configured identifiers and public links, verify the same DID, and retain DB paths, event keys, and receipts. Do not rename production state directories simply for cosmetic consistency.

Respect existing authorization: “set up this bot account” can authorize the necessary profile/settings work; “draft a bio” does not authorize saving it. Ask only for genuinely missing required information or scope. Stop at account mismatch or unresolved verification, while completing independent local assets. Retry a failed UI save only after inspecting whether it actually succeeded; do not repeatedly create app passwords or accounts.

## Profile acceptance

Verify saved name/bio, avatar crop at feed size, public source link, automated label when applied, correct account authentication, and actual config loading. Report what was saved versus only drafted. A logged-in browser session is for setup/review; unattended bot posting should use its authenticated API adapter.
