# Source Selection Rubric

This rubric helps decide which state, city, and local historical datasets should be ingested into BeenThere and which should be deferred.

The goal is not to include every possible city at once. The goal is to choose sources that add real user value without creating unmanageable maintenance cost.

## Selection principles

- prefer broad national coverage first
- add state sources that publish structured, reusable data
- add local city sources only when they meet a clear quality threshold
- skip or defer sources that are expensive to maintain and low in user value

## Evaluation categories

Each candidate source should be reviewed across the categories below.

### 1. Coverage value

Questions:

- Does the source add places not already covered by national datasets?
- Does it materially improve local historical depth?
- Is the location historically dense, tourist-heavy, or likely to matter to users?

Scoring guide:

- `3`: adds major coverage value or uniquely rich local history
- `2`: adds moderate value beyond existing coverage
- `1`: adds little new value
- `0`: duplicates existing coverage almost entirely

### 2. Data quality

Questions:

- Are records structured and internally consistent?
- Are titles, categories, and descriptions usable without major cleanup?
- Are duplicate or broken records limited?

Scoring guide:

- `3`: clean, structured, and consistent
- `2`: usable with moderate cleanup
- `1`: inconsistent and cleanup-heavy
- `0`: not reliable enough to ingest

### 3. Geospatial quality

Questions:

- Does the source include latitude and longitude?
- If not, can addresses be geocoded reliably?
- Are the coordinates accurate enough for map use?

Scoring guide:

- `3`: strong coordinates already present
- `2`: mostly geocoded or easy to geocode
- `1`: weak or inconsistent location data
- `0`: not usable for map-driven product needs

### 4. Licensing clarity

Questions:

- Is reuse clearly allowed?
- Are there restrictions on redistribution or display?
- Is attribution straightforward?

Scoring guide:

- `3`: clear, permissive, reusable
- `2`: usable with straightforward attribution
- `1`: unclear or requires manual legal review
- `0`: cannot confidently use

### 5. Refresh reliability

Questions:

- Is the source likely to remain available?
- Does it publish a stable dataset, feed, or API?
- Can we refresh it without scraping brittle pages?

Scoring guide:

- `3`: stable and refreshable
- `2`: mostly stable with some manual oversight
- `1`: brittle or intermittently available
- `0`: too fragile to rely on

### 6. Maintenance cost

Questions:

- How much one-off parsing or cleanup logic is required?
- Will the source require frequent manual intervention?
- Does it create a large long-tail burden for little value?

Scoring guide:

- `3`: low maintenance cost
- `2`: moderate maintenance cost
- `1`: high maintenance cost
- `0`: too costly for current scope

## Recommended threshold

Use a total score out of 18.

- `15-18`: strong candidate, ingest soon
- `11-14`: reasonable candidate, ingest if it fits roadmap priorities
- `7-10`: defer unless it fills an important coverage gap
- `0-6`: skip for now

Hard-stop rules:

- skip any source with `0` in geospatial quality
- skip any source with `0` in licensing clarity
- skip any source with `0` in data quality unless it is manually curated first

## Rollout strategy

Recommended order:

1. National datasets for broad baseline coverage
2. High-quality state marker or preservation datasets
3. High-value local city datasets that score above threshold
4. Long-tail local sources only after earlier tiers are stable

## Decision outcomes

Every evaluated source should land in one of these buckets:

- `ingest now`
- `defer`
- `skip`

For each evaluated source, capture:

- source name
- jurisdiction level
- jurisdiction name
- score by category
- total score
- decision
- rationale

## Example decisions

### Example: major city open-data landmarks dataset

- Coverage value: `3`
- Data quality: `3`
- Geospatial quality: `3`
- Licensing clarity: `2`
- Refresh reliability: `2`
- Maintenance cost: `2`
- Total: `15`
- Decision: `ingest now`

### Example: small city landmarks listed only on fragile HTML pages

- Coverage value: `2`
- Data quality: `1`
- Geospatial quality: `1`
- Licensing clarity: `1`
- Refresh reliability: `0`
- Maintenance cost: `1`
- Total: `6`
- Decision: `skip`

### Example: National Park System unit catalog

- Coverage value: `3`
- Data quality: `2`
- Geospatial quality: `1`
- Licensing clarity: `3`
- Refresh reliability: `2`
- Maintenance cost: `2`
- Total: `13`
- Decision: `defer`

Rationale:

- This source adds meaningful national coverage for NPS-managed units and designation types such as battlefields, memorials, monuments, and national historical parks.
- It is not fully duplicative of National Register data because it represents the park-system unit catalog rather than the preservation register.
- It likely needs a purpose-built importer and deduplication work because some units will overlap existing register-backed records.
- It is a strong follow-on national layer, but less ingestion-ready than the structured spreadsheet source already in use.
