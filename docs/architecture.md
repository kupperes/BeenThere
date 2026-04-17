# Architecture

## Overview

BeenThere is planned as a location-aware history platform with two main surfaces:

- a backend service that stores and serves historical place data
- a native iPhone client that turns that data into a nearby discovery and collection experience

The platform should answer two user needs at the same time:

- discovery: "What happened near me?"
- collection: "Which historic places have I visited, and what have I unlocked?"

From the backend side, the project should be designed so the iPhone app can be built in Xcode without needing Django-specific assumptions in the client. There is no intended desktop client or Windows app in the target architecture.

## High-level architecture

```text
Historical data sources
        |
        v
Ingestion + normalization jobs
        |
        v
PostgreSQL + PostGIS
        |
        v
Django REST API
        |
        +--> Admin/review tools
        |
        +--> iPhone client
```

## Core backend responsibilities

The backend should:

- ingest data from national and local historical sources
- normalize different source formats into a shared place model
- store geospatial coordinates for nearby and viewport queries
- provide summaries and source links for each place
- track authenticated user visits
- award badges based on visit history and category rules

## Major components

### 1. Data ingestion layer

This layer imports records from outside sources such as:

- National Register of Historic Places
- National Park Service data
- state marker registries
- city and county open data portals
- curated enrichment sources like Wikidata

Responsibilities:

- fetch raw records
- map source fields into a common schema
- deduplicate likely duplicates
- preserve source attribution
- log import runs and failures

### 2. Core data store

Recommended database:

- PostgreSQL
- PostGIS extension for geospatial queries

Why:

- radius searches are first-class
- map viewport queries are easier
- clustering and future spatial features are more natural

### 3. API layer

Recommended framework:

- Django REST Framework

The API should expose:

- nearby place lookup
- place detail lookup
- search and filters
- visited status for authenticated users
- visit check-off endpoints
- badge and profile progress endpoints

The API should stay mobile-friendly:

- JSON-only responses for app endpoints
- stable field naming across endpoints
- explicit versioning once the iPhone client begins active development
- no coupling between mobile flows and Django templates
- predictable error responses the Swift client can decode cleanly

### 4. Authentication and user progression

Authenticated users unlock the collection loop.

Core capabilities:

- account creation and login
- per-user visit history
- visited and unvisited state in detail views
- badge awards driven by rules
- profile progress summaries

### 5. Mobile client

Recommended first client:

- native iPhone app in SwiftUI, built and maintained in Xcode

Core client responsibilities:

- request location permission
- render nearby sites on a map
- display detail cards with summaries and source links
- let users mark sites as visited
- show collection progress and badges

Recommended iPhone stack:

- SwiftUI for app UI
- MapKit for the first map implementation unless Google Maps is a hard requirement
- Core Location for location permission and foreground updates
- `URLSession` or a lightweight networking layer for API calls
- Codable API models aligned with backend JSON responses

Xcode considerations:

- keep backend response shapes simple enough to map directly into Swift structs
- avoid mixed HTML and JSON response patterns for app routes
- keep auth flows compatible with native mobile login
- separate API domain models from admin or web-only concerns
- optimize decisions for iPhone usage first, not desktop reuse

## Domain model

### HistoricSite

Represents a normalized historical place from one or more sources.

Suggested fields:

- `id`
- `name`
- `summary`
- `description`
- `latitude`
- `longitude`
- `address`
- `city`
- `state`
- `category`
- `designation`
- `era`
- `source_name`
- `source_id`
- `wikipedia_url`
- `reference_url`
- `image_url`
- `is_verified`

### SourceFeed

Tracks upstream datasets and source metadata.

### ImportRun

Tracks ingestion execution, failures, counts, and timestamps.

### UserVisit

Represents that a user has marked a place as visited.

Suggested fields:

- `user_id`
- `historic_site_id`
- `visited_at`
- `visit_method`
- `notes` optional

### Badge

Defines a collectible achievement.

Examples:

- visit count in a category
- visit count in a geography
- completion of a curated collection

### UserBadge

Represents a badge earned by a specific user.

## Request flow

### Nearby map query

1. Mobile app gets the user's foreground location.
2. App calls nearby endpoint with latitude, longitude, and radius.
3. API performs geospatial query in PostGIS.
4. API returns nearby places, summaries, and visited state.
5. App renders pins and summary previews.

The ideal response contract for Xcode integration is:

- one top-level object
- one `results` array
- primitive values or simple nested objects
- no HTML fragments

### Mark visited flow

1. Authenticated user opens a place detail card.
2. User taps `Mark Visited`.
3. App sends authenticated request to visit endpoint.
4. API records `UserVisit`.
5. Badge rules are evaluated.
6. API returns updated visit and badge state.

## Security architecture notes

Because the app handles accounts and visit history, the architecture should assume privacy-sensitive user data from the beginning.

Security priorities:

- secrets from environment variables only
- HTTPS in production
- secure session or token handling
- minimal retention of sensitive user data
- rate limiting on login and account endpoints
- least-privilege admin access

For iPhone support, auth should eventually use an approach that translates cleanly to native clients, such as token-based authentication with clear expiration and revocation behavior.

## Implementation strategy

Recommended order:

1. Build the API foundation and normalized historical place model.
2. Add one or two reliable data imports.
3. Add authenticated visit tracking.
4. Add badge rules and progress endpoints.
5. Freeze a stable versioned API contract for the iPhone client.
6. Build the SwiftUI/Xcode app against that contract.
