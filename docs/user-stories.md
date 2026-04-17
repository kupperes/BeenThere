# User Stories

This document groups implementation work by roadmap phase. Check off stories as they are completed.

## Phase 1: API foundation

- [x] As a developer, I can configure the app with environment-based secrets so production credentials are not committed to the repository.
- [x] As a developer, I can run the backend with documented local configuration.
- [ ] As a developer, I have Django REST Framework installed and configured for API development.
- [x] As a developer, I have a `HistoricSite` model that can represent landmarks, markers, and other historical sites.
- [ ] As a developer, I have a database setup that can evolve from SQLite to PostgreSQL/PostGIS.
- [x] As an administrator, I can manage historical site records from the admin interface.

## Phase 2: Historical data ingestion

- [ ] As a developer, I can import one national historical dataset into the normalized place model.
- [ ] As a developer, I can import one state or local historical dataset into the same model.
- [ ] As a developer, I can retain source attribution for every imported record.
- [ ] As a developer, I can attach summary text and reference links, including Wikipedia when available.
- [ ] As a developer, I can track import runs and failures for debugging and repeatability.
- [ ] As a user, I can trust that places shown in the app reference a real source.

## Phase 3: Nearby discovery

- [ ] As a user, I can open the app and allow location access.
- [x] As a user, I can request nearby historical places by my current location.
- [ ] As a user, I can see the closest places within a defined radius.
- [x] As a user, I can tap a place and read a short summary of what happened there.
- [x] As a user, I can open a source link such as Wikipedia for deeper reading.
- [ ] As a user, I can filter nearby results by category.

## Phase 4: Accounts and visit tracking

- [ ] As a user, I can create an account securely.
- [ ] As a user, I can sign in and sign out securely.
- [ ] As a logged-in user, I can mark a place as visited.
- [ ] As a logged-in user, I can remove a mistaken visit check-off.
- [ ] As a logged-in user, I can tell whether I have already visited a place.
- [ ] As a logged-in user, I can view a running count of places I have visited.

## Phase 5: Gamification and collection

- [ ] As a logged-in user, I can earn badges for collecting places in a category.
- [ ] As a logged-in user, I can earn badges for collecting places across regions.
- [ ] As a logged-in user, I can view my earned badges.
- [ ] As a logged-in user, I can see progress toward the next badge.
- [ ] As a logged-in user, I can browse curated collections such as themed history trails.

## Phase 6: iPhone client

- [ ] As an iPhone user, I can see nearby historical places on a mobile map.
- [ ] As an iPhone user, I can open a place detail card with summary, sources, and visited state.
- [ ] As an iPhone user, I can mark a place as visited from the detail card.
- [ ] As an iPhone user, I can review my collection and badges in a mobile-friendly view.
- [ ] As an iPhone user, I can use the app comfortably without excessive battery drain.
- [ ] As an iPhone developer, I can consume stable JSON endpoints in Xcode without relying on Django template behavior.
- [ ] As an iPhone developer, I can map backend responses directly into Swift models with minimal transformation.
- [ ] As a product team, we can make backend decisions that prioritize iPhone usage instead of desktop compatibility.

## Cross-cutting security stories

- [ ] As a user, my account credentials are handled securely.
- [ ] As a user, my visit history is only available to my account unless I explicitly share it.
- [ ] As an administrator, I can operate the app without exposing secrets in source control.
- [ ] As a maintainer, I can review the system's security posture as part of implementation planning.
