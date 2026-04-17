# Contributing

## Purpose

This project is evolving from a college prototype into a production-minded app concept. Contributions should move the codebase toward a secure, map-driven, API-first architecture that supports an eventual iPhone client.

## Principles

- keep changes small and understandable
- prefer secure defaults
- document product and architecture decisions as they change
- avoid shipping features that do not align with the roadmap
- preserve room for national and local historical data sources

## Before you start

1. Read [README.md](/Users/erickupper/Github/BeenThere/README.md).
2. Read [ROADMAP.md](/Users/erickupper/Github/BeenThere/ROADMAP.md).
3. Review [docs/architecture.md](/Users/erickupper/Github/BeenThere/docs/architecture.md) and [docs/user-stories.md](/Users/erickupper/Github/BeenThere/docs/user-stories.md).
4. Confirm your work fits one of the current roadmap phases.

## Contribution areas

Good contribution categories:

- backend API design
- geospatial querying and data modeling
- ingestion/import tooling
- authentication and security hardening
- iPhone client planning and integration contracts
- documentation improvements

## Security expectations

- never commit real secrets
- use environment variables for credentials and deployment settings
- avoid logging sensitive user information
- treat account, visit-history, and location features as privacy-sensitive
- favor Django's built-in protections unless there is a strong reason not to

If you spot a security concern, prioritize fixing or documenting it before adding adjacent features.

## Documentation expectations

When a change affects architecture, security, or product scope, update the relevant docs:

- [ROADMAP.md](/Users/erickupper/Github/BeenThere/ROADMAP.md)
- [docs/architecture.md](/Users/erickupper/Github/BeenThere/docs/architecture.md)
- [docs/user-stories.md](/Users/erickupper/Github/BeenThere/docs/user-stories.md)

## Implementation tracking

The checklist in [docs/user-stories.md](/Users/erickupper/Github/BeenThere/docs/user-stories.md) is the current source of truth for staged implementation progress. If you complete a story or materially change its scope, update the checkbox state and wording in the same branch.

## Coding notes

- keep new modules focused
- avoid premature complexity in the MVP
- build API contracts that can support the eventual iPhone app
- prefer normalized data models over source-specific shortcuts

## Pull request guidance

Use pull requests to explain:

- what changed
- which roadmap phase it supports
- whether docs were updated
- any security or migration impact

If a change introduces risk, call it out plainly.
