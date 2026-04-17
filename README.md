# BeenThere

BeenThere is an iPhone-only, location-aware history app concept that helps users discover what happened around them.

The core experience is:

- show the user's location on a map
- overlay nearby landmarks, historical markers, and notable sites
- let the user tap a place to read a short summary
- link out to deeper reading like Wikipedia or source archives
- let logged-in users mark places as visited
- reward collection progress with badges and themed achievements

## Current state

This repository started as a small Django site and is now being reshaped into the foundation for:

- a backend API for historical place data
- a native iPhone client for the location and map experience

The current codebase is still early-stage. Most of the product direction now lives in the project documentation.

There is now also an initial native iPhone scaffold in [ios/README.md](/Users/erickupper/Github/BeenThere/ios/README.md) and [ios/BeenThere.xcodeproj/project.pbxproj](/Users/erickupper/Github/BeenThere/ios/BeenThere.xcodeproj/project.pbxproj) so we can begin Xcode work against the live Django API.

## Project docs

- [Roadmap](/Users/erickupper/Github/BeenThere/ROADMAP.md)
- [Architecture](/Users/erickupper/Github/BeenThere/docs/architecture.md)
- [User Stories](/Users/erickupper/Github/BeenThere/docs/user-stories.md)
- [Source Selection Rubric](/Users/erickupper/Github/BeenThere/docs/source-selection-rubric.md)
- [Contributing](/Users/erickupper/Github/BeenThere/CONTRIBUTING.md)

## Product vision

BeenThere is meant to answer:

"Where am I, and what important history happened near me?"

It also adds a collection loop:

- users can check off places they have visited
- users build a personal history collection
- users earn badges for collecting categories, regions, and themed sets

## Planned architecture

The planned long-term shape is:

- Django + Django REST Framework backend
- PostgreSQL + PostGIS for geospatial search
- data ingestion pipelines for national and local historical datasets
- native iPhone app in Xcode, likely using SwiftUI
- map-driven browsing with nearby search, detail cards, and visit tracking

The backend should be built as an API-first service so the iPhone app can consume clean JSON contracts without depending on server-rendered Django pages. There is no planned Windows, Mac desktop, or general-purpose web client for this product.

## iPhone scaffold

The repo now includes a first-pass SwiftUI/Xcode scaffold with:

- a map-first nearby screen using `MapKit`
- foreground location permission handling
- an API client aligned with the Django JSON endpoints
- a place detail sheet with source links and visited actions
- a collection/profile shell for auth and visit summaries

Open [ios/BeenThere.xcodeproj/project.pbxproj](/Users/erickupper/Github/BeenThere/ios/BeenThere.xcodeproj/project.pbxproj) in Xcode to continue the iPhone client work.

## Early MVP target

The first strong milestone is:

"Show my location, the 20 closest historical places within 10 miles, and let me mark them as visited."

## Security note

Secrets should not live in source control. The app now expects configuration like `DJANGO_SECRET_KEY` to come from environment variables. Use [`.env.example`](/Users/erickupper/Github/BeenThere/.env.example) as a template for local development.

## Local development

This project is still in transition, but the current Django app can still be run in the usual way:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Before doing that in a fresh environment, create a local `.env` file based on [`.env.example`](/Users/erickupper/Github/BeenThere/.env.example).

The backend currently supports three database modes through environment variables:

- `sqlite` for simple local development
- `postgresql` for a standard PostgreSQL deployment path
- `postgis` for the eventual geospatial production path

To load sample national historical sites into the catalog:

```bash
python3 manage.py import_sample_national_sites
```

After running that command, check:

- [http://127.0.0.1:8000/api/sites/](http://127.0.0.1:8000/api/sites/)
- [http://127.0.0.1:8000/api/sources/](http://127.0.0.1:8000/api/sources/)
- [http://127.0.0.1:8000/api/import-runs/](http://127.0.0.1:8000/api/import-runs/)

To import the approved official National Park Service National Register listed-properties spreadsheet:

```bash
python3 manage.py import_nps_nrhp_listed
```

This importer uses the approved NPS primary source from:
- [NPS National Register Data Downloads](https://www.nps.gov/subjects/nationalregister/data-downloads.htm)

Records imported from this spreadsheet may not always include public coordinates, so they can appear in site/detail APIs before they become eligible for nearby-map queries.

To import the approved Kansas state marker source:

```bash
python3 manage.py import_kansas_historical_markers
```

This importer uses the Kansas Historical Society markers page:
- [Kansas Historical Markers](https://www.kansashistory.gov/p/kansas-historical-markers/14999)
