# User Stories

This document groups implementation work by roadmap phase. Each story has a stable ID, a checkbox, and acceptance criteria. The BDD progress suite should map directly to these story IDs so implementation progress can be measured by pass rate.

## Phase 1: API foundation

### US-1.1 [x] As a developer, I can configure the app with environment-based secrets so production credentials are not committed to the repository.
Acceptance criteria:
- `DJANGO_SECRET_KEY` is loaded from environment configuration instead of a committed production secret.
- The repository includes an example env file but not a committed real secret file.

### US-1.2 [x] As a developer, I can run the backend with documented local configuration.
Acceptance criteria:
- The README documents local environment setup and backend launch steps.
- A new developer can follow the documented commands to prepare the app locally.

### US-1.3 [x] As a developer, I have Django REST Framework installed and configured for API development.
Acceptance criteria:
- The dependency list includes Django REST Framework.
- Django settings register `rest_framework` and default the API to JSON-oriented behavior.

### US-1.4 [x] As a developer, I have a `HistoricSite` model that can represent landmarks, markers, and other historical sites.
Acceptance criteria:
- `HistoricSite` stores name, summary, coordinates, category, and source-link data.
- The model is backed by a migration and ready for API serialization.

### US-1.5 [x] As a developer, I have a database setup that can evolve from SQLite to PostgreSQL/PostGIS.
Acceptance criteria:
- Local development can continue with SQLite.
- Environment-driven settings support switching to PostgreSQL or PostGIS without rewriting application code.

### US-1.6 [x] As an administrator, I can manage historical site records from the admin interface.
Acceptance criteria:
- `HistoricSite` is registered in Django admin.
- The admin exposes useful list columns and filters for site management.

## Phase 2: Historical data ingestion

### US-2.1 [x] As a developer, I can import one national historical dataset into the normalized place model.
Acceptance criteria:
- A repeatable import path exists for one national dataset.
- Imported records create `HistoricSite` entries without manual admin entry.

### US-2.2 [x] As a developer, I can import one state or local historical dataset into the same model.
Acceptance criteria:
- A second importer exists for a state or local source.
- Both importers normalize into the same `HistoricSite` schema.

### US-2.3 [x] As a developer, I can retain source attribution for every imported record.
Acceptance criteria:
- Each imported site stores source name and an upstream identifier or equivalent attribution.
- API responses expose source attribution for downstream clients.

### US-2.4 [x] As a developer, I can attach summary text and reference links, including Wikipedia when available.
Acceptance criteria:
- Imported or enriched records can store a short summary.
- Records can carry one or more external reading links such as Wikipedia or source archives.

### US-2.5 [x] As a developer, I can track import runs and failures for debugging and repeatability.
Acceptance criteria:
- Import execution captures success and failure counts.
- Import failures can be reviewed after a run instead of disappearing silently.

### US-2.6 [x] As a user, I can trust that places shown in the app reference a real source.
Acceptance criteria:
- Place detail responses include source attribution.
- Imported records can be distinguished from unverified or incomplete data.

### US-2.7 [x] As a product team, we can decide which cities and local sources to ingest based on value and maintenance cost.
Acceptance criteria:
- The project defines a repeatable rubric for evaluating local city sources before ingestion.
- Source selection considers data quality, geographic value, licensing clarity, and maintenance cost.
- Cities without a sufficient data-quality threshold can be explicitly deferred or skipped.

## Phase 3: Nearby discovery

### US-3.1 [x] As a user, I can open the app and allow location access.
Acceptance criteria:
- The iPhone client requests foreground location permission.
- The app handles granted and denied location states clearly.

### US-3.2 [x] As a user, I can request nearby historical places by my current location.
Acceptance criteria:
- The API accepts latitude and longitude as query parameters.
- A valid nearby request returns matching historical places in JSON.

### US-3.3 [x] As a user, I can see the closest places within a defined radius.
Acceptance criteria:
- Nearby responses exclude places outside the requested radius.
- Nearby responses return matching places ordered from closest to farthest.

### US-3.4 [x] As a user, I can tap a place and read a short summary of what happened there.
Acceptance criteria:
- Place detail responses include a short summary.
- The summary is available without opening an external source link.

### US-3.5 [x] As a user, I can open a source link such as Wikipedia for deeper reading.
Acceptance criteria:
- Place detail responses expose at least one reference or Wikipedia link when available.
- Links are returned as normal URL fields suitable for a mobile client to open.

### US-3.6 [x] As a user, I can filter nearby results by category.
Acceptance criteria:
- Nearby requests accept a category filter.
- Filtered results only include places in the requested category.

### US-3.7 [x] As a user, I can browse imported sites through a simple HTML filter page instead of raw JSON.
Acceptance criteria:
- The app exposes an HTML page for browsing imported sites.
- The page supports filtering by state and type.
- The page supports pagination for large result sets.
- The page makes browsing the dataset easier than inspecting raw API JSON.

## Phase 4: Accounts and visit tracking

### US-4.1 [x] As a user, I can create an account securely.
Acceptance criteria:
- The system exposes a secure account-creation path.
- Password policy and secure credential handling are enforced.

### US-4.2 [x] As a user, I can sign in and sign out securely.
Acceptance criteria:
- The system provides authenticated sign-in and sign-out flows.
- Session or token invalidation is handled cleanly on sign-out.

### US-4.3 [x] As a logged-in user, I can mark a place as visited.
Acceptance criteria:
- A logged-in user can create a visit record for a place.
- The place response reflects visited state after the action succeeds.

### US-4.4 [x] As a logged-in user, I can remove a mistaken visit check-off.
Acceptance criteria:
- A logged-in user can undo a previously created visit record.
- The API returns the updated unvisited state after removal.

### US-4.5 [x] As a logged-in user, I can tell whether I have already visited a place.
Acceptance criteria:
- Place detail responses include per-user visited state.
- Nearby results can reflect visited state for the current user.

### US-4.6 [x] As a logged-in user, I can view a running count of places I have visited.
Acceptance criteria:
- The system exposes a visit count for the current user.
- The count updates when visits are added or removed.

## Phase 5: Gamification and collection

### US-5.1 [ ] As a logged-in user, I can earn badges for collecting places in a category.
Acceptance criteria:
- Badge rules can award progress based on category-specific visit totals.
- A user receives a badge once the threshold is met.

### US-5.2 [ ] As a logged-in user, I can earn badges for collecting places across regions.
Acceptance criteria:
- Badge rules can evaluate visits across multiple geographic regions.
- A qualifying user receives the region-based badge automatically.

### US-5.3 [ ] As a logged-in user, I can view my earned badges.
Acceptance criteria:
- The API exposes badges earned by the current user.
- Each earned badge includes enough metadata for an iPhone UI to render it.

### US-5.4 [ ] As a logged-in user, I can see progress toward the next badge.
Acceptance criteria:
- The system exposes progress toward at least one upcoming badge.
- Progress values are machine-readable, not just free-form text.

### US-5.5 [ ] As a logged-in user, I can browse curated collections such as themed history trails.
Acceptance criteria:
- The system exposes curated collections or themed sets of places.
- Collection membership can be presented in a mobile-friendly way.

## Phase 6: iPhone client

### US-6.1 [x] As an iPhone user, I can see nearby historical places on a mobile map.
Acceptance criteria:
- The Xcode app renders map pins for nearby historical places.
- Pins are backed by live API data rather than static mock content.

### US-6.2 [x] As an iPhone user, I can open a place detail card with summary, sources, and visited state.
Acceptance criteria:
- Tapping a pin opens a detail view or sheet.
- The detail view shows summary text, source links, and visited state when available.

### US-6.3 [x] As an iPhone user, I can mark a place as visited from the detail card.
Acceptance criteria:
- The detail card includes a visited action for authenticated users.
- The detail card updates after the action without requiring an app restart.

### US-6.4 [x] As an iPhone user, I can review my collection and badges in a mobile-friendly view.
Acceptance criteria:
- The iPhone app exposes a collection or profile screen.
- The view includes visit totals and earned badges.

### US-6.5 [x] As an iPhone user, I can use the app comfortably without excessive battery drain.
Acceptance criteria:
- The app uses foreground location updates appropriate for the core experience.
- The app avoids unnecessary background tracking in the MVP.

### US-6.6 [x] As an iPhone developer, I can consume stable JSON endpoints in Xcode without relying on Django template behavior.
Acceptance criteria:
- Mobile-facing routes return structured JSON rather than HTML fragments.
- API routes do not depend on Django template rendering for app behavior.

### US-6.7 [x] As an iPhone developer, I can map backend responses directly into Swift models with minimal transformation.
Acceptance criteria:
- API fields use stable names and consistent types.
- Response shapes are simple enough to decode into Swift `Codable` models.

### US-6.8 [x] As a product team, we can make backend decisions that prioritize iPhone usage instead of desktop compatibility.
Acceptance criteria:
- The backend roadmap explicitly prioritizes iPhone needs.
- New API decisions are evaluated against mobile-first requirements.

## Cross-cutting security stories

### US-S1 [x] As a user, my account credentials are handled securely.
Acceptance criteria:
- Credentials are transmitted and stored using secure platform-appropriate controls.
- The system does not expose raw credentials in logs, responses, or source control.

### US-S2 [x] As a user, my visit history is only available to my account unless I explicitly share it.
Acceptance criteria:
- Visit-history endpoints require authentication and authorization.
- One user cannot read another user's visit history by default.

### US-S3 [x] As an administrator, I can operate the app without exposing secrets in source control.
Acceptance criteria:
- Operational secrets are supplied outside committed application code.
- The project documents a safe local configuration path for secret values.

### US-S4 [x] As a maintainer, I can review the system's security posture as part of implementation planning.
Acceptance criteria:
- Security requirements are documented in architecture or roadmap materials.
- New phases account for secret handling, auth, and privacy-sensitive data.
