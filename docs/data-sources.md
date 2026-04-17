# Data Sources

This document is the canonical inventory of historical-place data sources for BeenThere.

Use it to answer:

- what source layers we have approved
- which sources have already been imported
- which sources are only proposed
- how each source fits the product
- where overlap or deduplication needs attention

## Status meanings

- `proposed`: identified as a candidate source but not yet approved
- `approved`: accepted for future implementation but not yet imported
- `imported`: an importer exists and data has been loaded into the normalized catalog
- `deprecated`: no longer recommended for active use

## Current source inventory

| Source | Owner / Publisher | URL | Jurisdiction | Format | Status | Importer | Notes |
|---|---|---|---|---|---|---|---|
| National Register Sample Dataset | Local project seed data | local repo seed file | national | JSON | imported | `python3 manage.py import_sample_national_sites` | Development/test-only sample dataset |
| NPS National Register Listed Properties | National Park Service | [NPS National Register Data Downloads](https://www.nps.gov/subjects/nationalregister/data-downloads.htm) | national | XLSX | imported | `python3 manage.py import_nps_nrhp_listed` | Official National Register listed-properties layer; some records may not include public coordinates |
| Kansas Historical Markers | Kansas Historical Society | [Kansas Historical Markers](https://www.kansashistory.gov/p/kansas-historical-markers/14999) | state | HTML | imported | `python3 manage.py import_kansas_historical_markers` | Official Kansas state marker layer |
| National Park System Unit Catalog | National Park Service | [NPS National Park System](https://www.nps.gov/aboutus/national-park-system.htm) | national | HTML | approved | not yet implemented | Distinct from National Register listings; adds NPS-managed unit/designation coverage and will need deduplication against overlapping sites |

## Source details

### National Register Sample Dataset

- Status: `imported`
- Purpose: local development and test seed data
- Storage shape: normalized into `HistoricSite` rows
- Raw source file:
  - [pages/data/sample_national_register.json](/Users/erickupper/Github/BeenThere/pages/data/sample_national_register.json)
- Import command:
  - `python3 manage.py import_sample_national_sites`

### NPS National Register Listed Properties

- Status: `imported`
- Purpose: official national preservation-register layer
- Storage shape: normalized into `HistoricSite` rows
- Source metadata is tracked in:
  - `SourceFeed`
  - `ImportRun`
- Import command:
  - `python3 manage.py import_nps_nrhp_listed`
- Notes:
  - This is a National Register listing source, not a full “all stop-and-read places” source.
  - Some imported records may not include public map-ready coordinates.

### Kansas Historical Markers

- Status: `imported`
- Purpose: official state-level historical marker layer
- Storage shape: normalized into `HistoricSite` rows
- Import command:
  - `python3 manage.py import_kansas_historical_markers`
- Notes:
  - This is closer to the product’s “marker-like things people can stop and read” goal than the register listing layer.

### National Park System Unit Catalog

- Status: `approved`
- Purpose: add NPS-managed units and designation types such as:
  - national battlefields
  - national historical parks
  - national historic sites
  - memorials
  - monuments
- Proposed source:
  - [NPS National Park System](https://www.nps.gov/aboutus/national-park-system.htm)
- Notes:
  - This is not fully duplicative of the National Register import.
  - It should be treated as a distinct national source layer.
  - It will need overlap handling and deduplication against existing NPS/NRHP-backed records.

## Operational record

The live operational source record is currently stored in the database via:

- `SourceFeed`: source identity and metadata
- `ImportRun`: import history and run status
- `HistoricSite`: normalized final records tied back to a source

This file is the human-readable companion to that runtime metadata.

## Raw source files

Raw downloaded files are not required for every source.

When used, they may exist as local working artifacts in:

- `/Users/erickupper/Github/BeenThere/data-imports`

Important:

- `data-imports/` is a local cache/work area, not the system of record
- normalized SQL rows are the real runtime catalog
- source files only appear there when we intentionally save a local copy for reproducibility, parser development, or import debugging
