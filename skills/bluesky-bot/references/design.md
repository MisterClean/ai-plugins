# Editorial design and iteration

## Make a publication, not a debug report

Decide what the reader should understand in two seconds. Use a short event headline, a recognizable subject/location, a few useful facts, and a source link. Put body copy, card, and alt text through the same normalized evidence model.

Use dynamic templates: singular/plural, known unit/type combinations, valid timing, optional measurements. Unknown values disappear or are described accurately; they do not become zero or one. Use restrained semantic emojis when they help scan readings (temperature, waves, wind). Avoid emoji replacing labels or units. Native linked text such as “View data” or “Data Portal Record” keeps URLs from dominating the post; implement facets, not Markdown links.

Good body patterns:

- New-record alert: event → quantity/type → meaningful date/elapsed time → linked record.
- Observation: station → grouped readings with units → observation timestamp + linked source on one line.
- Collection: address or stable parcel identifier, with accurate contextual image description.

Put recurring project context in the bio/README/source notes. Do not cover each image with implementation labels, style names, preview badges, or repeated caveats. Preserve wording essential to interpreting the actual claim: a preapproval is not a permit, and old observations need an unambiguous observation date/time. Avoid describing a stale sample as current. Removing redundant disclaimers does not disable freshness checks.

## Review loop

1. Inspect the current selected branch, render defaults, environment overrides, sample output, and most recent accepted changes. Verify how every relevant option reaches the actual renderer; an `.env.example` entry is not evidence that code reads it.
2. Use the same source record and viewport to compare concepts. When exploration is requested, show a small set of meaningfully different concepts; obey a requested count. Worktrees are useful for independently implemented concepts but not mandatory for color/zoom variations.
3. After a concept is selected, vary one dimension at a time: zoom, shade opacity, label density, heading scale, or composition. Name variants with visible differences and show a contact sheet plus full-size exports.
4. Record the user's selection and rationale. Apply it to the intended branch and runtime path. Persist a style assignment per delivery if alternating styles is part of the publication contract; retries must not advance the sequence or select a new look.
5. Render representative edge cases with real dependencies: long/short names, Unicode, unknowns, zero/multiple quantities, dense/sparse maps, adjacent markers, and imagery unavailable. Inspect the actual exported artifact, not only HTML or code.
6. Inspect at mobile feed width as well as full resolution, and when authorized, inspect the live Bluesky root, reply, crop, link, and alt-text panel. Keep a selected sample and the generation command. Remove abandoned variants when requested; preserve useful selected design rules.

Do not silently replace a unavailable basemap, font, logo, or source image for a “production preview.” Label a substitute as a layout-only mock and resolve the missing dependency before claiming fidelity. Increasing pixel density is different from shrinking the CSS viewport: the latter changes layout, line wrapping, and map coverage.

## Repository design contract

Maintain a short `docs/post-design.md` (or existing equivalent) with:

| Decision | What to record |
|---|---|
| Hierarchy | Event heading, subject, facts, timestamp/source; omitted clutter |
| Typography | Font files/weights/licenses, fitting and wrapping behavior |
| Palette | Semantic colors and contrast roles |
| Geometry | Logical canvas, aspect ratio, scale, safe areas, map/photo layout |
| Map | Actual provider/style, zoom per variant, marker, label/POI/transit priorities |
| Thread | Root/reply content and image order; required versus optional media |
| Evidence | Source fields, alt-text template, selected fixtures and render command |
| Acceptance | Specific observed defects to prevent, with representative outputs |

Translate feedback into checkable outcomes. “Brighter map” becomes “street names and the subject marker remain legible at feed size.” “Less fluff” becomes a list of removed redundant labels. Do not freeze every pixel or add string-matching tests for one-off style changes. Use visual review for visual judgments and automated tests for meaningful constraints such as fitting, byte limits, facts, and thread references.

## Cards and maps

The Chicago projects favor editorial announcement posters: tall condensed headline, civic colors, a map or photograph as the main subject, and a quiet credit line. Big Shoulders and Roboto, `#41B6E6` blue, `#E4002B` red, black and white are local precedents. Apply a different identity when the user requests it; verify current Chicago guidance before asserting official conformance.

Keep the map useful. Limit gradients to the areas behind text, preserve street/POI contrast, and prioritize the subject over decorative marker containers. Chicago precedents used a lone six-point star; procedural paths avoid font-dependent star shapes. Transit infrastructure in a basemap is not scheduled transit service. Use authoritative route/station overlays when needed and validate their freshness/geographic fit. A CPU renderer reading vector tiles will not automatically reproduce MapLibre style expressions or label placement.

For geographic aggregates, calculate every number and marker from the same dated cohort. Keep true coordinates anchored; resolve overlaps with leader lines, not invented locations. Show coverage if some records cannot be mapped. Fit irregular ward bounds with padding. Do not place unknown addresses at a ward centroid. Extruded buildings depict existing map context, not a proposed construction rendering.

A portrait card is useful for one hero image; paired images can crop differently in the feed. The ADU map pair settled on square exports to preserve complete thumbnails. Treat root/reply composition as part of design: a primary announcement in the root and Street View/context in replies often gives each image more room.

## Media quality and accessibility

Render text/vectors at intended output resolution. Preserve the original photo's real detail; enlarging a small Street View does not create detail. Use bounded JPEG quality search and validate the final encoded size; reduce dimensions only when necessary. Budget decoded pixel memory as well as file bytes. Embed fonts for portable rendering and keep required attribution readable and uncropped.

Alt text should explain the subject and important visual information and include the public facts needed to understand the announcement: place, event/type, quantities, observation/date, units, and source/provenance as relevant. For charts/maps, state the meaningful pattern and location context. Do not dump internal fields, credentials, or irrelevant personal data. An exact record URL is useful, but also keep a clickable source link in the body. Verify current client/editor limits in [Bluesky API](bluesky-api.md).

Use deterministic rendering for recurring factual cards and editable icons. AI illustration can help a requested artistic concept, but never synthesize a purported Street View, data map, or factual chart. If an image-generation workflow is chosen, use the available image-generation skill/tool and retain the appropriate source/prompt provenance.
