# BeenThere Roadmap

## Product idea

BeenThere helps a person understand the history around them in real time.
The app shows the user's current location on a map and overlays nearby:

- national landmarks
- local landmarks
- historical markers
- notable historic sites
- short summaries of what happened there
- reference links for deeper reading, such as Wikipedia or source archives

The core experience is: "Where am I, and what important history happened near me?"

A second core loop is collection and progress:

- users can mark places as visited
- users build a personal collection of discovered sites
- users unlock badges for completing themed sets of places

## Recommended direction

The current codebase is a simple Django starter app. For an iPhone-ready product, the best next step is to split the app into two parts:

- a backend API that stores and serves historical places
- a native iPhone app that renders the map and nearby results

This lets the data pipeline, search logic, and user features evolve independently from the iPhone UI.

## Proposed architecture

### 1. Backend

Keep Django, but turn it into an API service instead of a server-rendered website.

Recommended stack:

- Django
- Django REST Framework
- PostgreSQL + PostGIS for geospatial queries
- background jobs for data import and refresh

Backend responsibilities:

- ingest historical-site datasets
- normalize records from different sources
- store latitude/longitude and metadata
- store a short event summary and one or more reference links
- return markers near a location
- support filtering by category, era, distance, and source
- track user visits, progress, and unlocked badges
- cache popular map areas

### 2. iPhone app

Build a dedicated iPhone client.

Recommended stack:

- SwiftUI
- Xcode
- Apple native location services

This product should be designed for iPhone only, not for desktop or general cross-platform clients.

### 3. Map layer

Because your original idea specifically mentions Google Maps, use one of these approaches:

- Preferred if you want Google styling and behavior: Google Maps SDK for iOS
- Preferred if you want the fastest native iPhone path: Apple MapKit

Recommendation:
Start with MapKit for MVP unless Google Maps is a hard requirement. It reduces setup overhead and feels more native on iPhone. If Google Maps is central to the vision, we can keep that requirement and build around the Google Maps iOS SDK.

## Core data model

A single normalized `HistoricSite` model should sit behind all source imports.

Suggested fields:

- `id`
- `name`
- `description`
- `summary`
- `latitude`
- `longitude`
- `address`
- `city`
- `state`
- `source_name`
- `source_id`
- `category`
- `designation`
- `date_established`
- `era`
- `tags`
- `image_url`
- `wikipedia_url`
- `reference_url`
- `source_links`
- `is_verified`
- `last_synced_at`

Helpful related tables:

- `SourceFeed`
- `ImportRun`
- `UserSavedPlace`
- `UserVisit`
- `Badge`
- `UserBadge`
- `BadgeRule`

## Data sources to pursue

You’ll want a layered strategy because no single source will cover national and local history well.

High-value starting points:

- National Register of Historic Places datasets
- National Park Service open data
- National Park System unit catalog
- state historical marker programs
- city and county open data portals
- Smithsonian or Library of Congress collections where location data exists
- Wikidata for enrichment

Important note:
Local historical marker coverage will likely be fragmented. Some cities publish clean GIS data; others may require one-off import scripts or manual curation.

Local city and county sources should be selected with a repeatable rubric rather than added ad hoc. See [docs/source-selection-rubric.md](/Users/erickupper/Github/BeenThere/docs/source-selection-rubric.md).

Current source inventory:

- implemented: National Park Service National Register listed-properties spreadsheet
- implemented: Kansas Historical Society historical markers
- approved next source: [NPS National Park System](https://www.nps.gov/aboutus/national-park-system.htm)

Why the NPS National Park System source is worth adding:

- it adds NPS-managed unit and designation coverage
- it includes categories like national battlefields, national historical parks, national historic sites, memorials, and monuments
- it overlaps some National Register records, but it is not fully duplicative because it is a park-system catalog rather than a preservation-register listing
- it should be added as a distinct source layer with deduplication against existing sites

## MVP feature set

The first version should stay very focused.

### MVP user flow

1. User opens the app.
2. App requests location permission.
3. Map centers on the user's location.
4. Nearby historical places appear as pins.
5. User taps a pin to view a short summary and source links.
6. User can mark a place as visited.
7. User can filter by radius or category.

### MVP features

- current-location map
- nearby historical markers and landmarks
- tap-to-open place details
- short event summary on each detail view
- external links for deeper reading
- mark place as visited
- basic visited/unvisited state on markers or detail cards
- distance from current location
- basic filters
- lightweight search by place name or city

### Features to defer until later

- social features
- reviews or comments
- full trip planning
- augmented reality
- advanced personalization

### Gamification features

This should be a major product layer, but introduced in stages.

Stage 1:

- logged-in users can check off visited places
- profile shows total places visited
- place detail shows whether the user has visited it

Stage 2:

- badges for category milestones
- badges for geography milestones
- simple progress bars toward the next badge

Stage 3:

- curated collections like "Civil War Sites" or "Texas Historical Markers"
- limited-time challenges
- streaks or trip summaries if they still feel aligned with the product

Examples of badge ideas:

- `Landmark Hunter`: visit 10 national landmarks
- `Marker Scout`: visit 25 historical markers
- `Hometown Historian`: visit 10 places in one metro area
- `Road Trip Archivist`: visit places in 5 different states
- `Civil War Explorer`: visit 8 Civil War-related sites

## API design

Suggested first endpoints:

- `GET /api/sites/nearby?lat=...&lng=...&radius=...`
- `GET /api/sites/{id}`
- `GET /api/sites/search?q=...`
- `GET /api/categories`
- `GET /api/sources`

Example nearby response should include:

- site name
- coordinates
- short summary
- distance
- category
- source
- wikipedia or reference link when available
- detail page id

Example detail response should include:

- site name
- short event summary
- longer description if available
- source links
- wikipedia link if available
- coordinates
- address
- source attribution
- whether the current user has marked it visited

## Geospatial behavior

This app lives or dies by map performance and query quality.

Important backend capabilities:

- radius search around current location
- viewport query for visible map bounds
- clustering support for dense areas
- deduplication when two sources describe the same site

PostGIS is the right long-term foundation because it handles distance queries and map bounding boxes cleanly.

## iPhone-specific needs

Key mobile concerns:

- permission handling for location services
- smooth map panning and pin rendering
- offline or low-connectivity fallback for recently viewed areas
- battery-friendly location updates
- App Store-compliant privacy messaging

Each marker's detail card should open with:

- title
- 2 to 4 sentence summary
- "Read more" links
- source attribution
- a clear `Mark Visited` action for logged-in users

Profile and collection views should later include:

- total places visited
- recently visited places
- badges earned
- progress toward next badge

The app should not constantly track location in the background for MVP. Foreground proximity updates are enough to start.

## Security priorities

Because this app will include accounts, visit history, and location-aware features, security needs to be built in from the start.

Immediate priorities:

- never commit real secrets to the repo
- load `SECRET_KEY` and deployment settings from environment variables
- separate local development defaults from production settings
- require HTTPS and secure cookies in production

Account and data protection priorities:

- use Django's built-in auth system or a well-supported extension
- enforce strong password validation
- add rate limiting for login and account endpoints
- preserve CSRF protection for browser-based flows
- keep mobile auth tokens minimal and well-scoped
- store only the location and visit data needed for product features
- clearly communicate to users what visit history is stored

Operational priorities:

- rotate any secret that may have been committed before
- review dependencies for known vulnerabilities
- log auth and import failures without logging sensitive data
- tightly restrict admin access

## Phased build plan

### Phase 1: Turn the backend into a real API

- add Django REST Framework
- replace SQLite with PostgreSQL/PostGIS
- create `HistoricSite` and import-tracking models
- build nearby/detail/search endpoints
- add admin tools for reviewing imported sites

### Phase 2: Build ingestion pipelines

- import one reliable national dataset
- import one state or city marker dataset
- normalize fields into the shared model
- enrich records with summary text and reference links
- log import failures and duplicates

### Phase 3: Add users and visit tracking

- add authentication
- create `UserVisit` model and visited endpoints
- let a user mark and unmark places as visited
- return visited state in nearby/detail APIs

### Phase 4: Build the iPhone app

- create native iOS app in SwiftUI
- add map screen
- request user location
- fetch nearby markers from the API
- show pins and detail cards
- let logged-in users check places off from the detail card

### Phase 5: Improve usefulness and retention

- add filters
- add saved places
- add photos and richer descriptions
- add "history near me" list view
- add badges and progress tracking

### Phase 6: Scale coverage and quality

- onboard more local data sources
- improve deduplication
- add editorial curation for bad or sparse records

## What should change in this repo next

If we continue from this codebase, the most valuable next implementation steps are:

1. Convert the `pages` app from a static page into an API-driven project structure.
2. Add Django REST Framework and create a `HistoricSite` model.
3. Move from SQLite to PostgreSQL/PostGIS.
4. Add `UserVisit`, `Badge`, and `UserBadge` models early so the API shape supports gamification.
5. Add a `nearby` endpoint with sample hard-coded seed data first.
6. Build a separate iPhone client after the API returns usable map data.

## Recommended MVP milestone

The best first shippable target is:

"Show my location, the 20 closest historical places within 10 miles, and let me mark them as visited."

If that works well, the rest of the product becomes much easier to expand.
