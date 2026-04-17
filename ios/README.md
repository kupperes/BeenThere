# iOS Client Scaffold

This folder contains the first Xcode-facing scaffold for the BeenThere iPhone app.

What is included:

- a native SwiftUI app target
- a location manager for foreground nearby discovery
- an API client aligned with the Django backend routes
- a nearby map screen backed by live `/api/sites/nearby/` responses
- a detail sheet with summary, source links, and visited state
- a collection/profile screen backed by `/api/visits/summary/`

## Open in Xcode

Open:

- `ios/BeenThere.xcodeproj`

Then run the `BeenThere` scheme in the iPhone Simulator.

## Local backend

The app defaults to:

- `http://127.0.0.1:8000`

That works for local simulator development when the Django server is running on the same machine.

If you need to point at a different backend, edit:

- `ios/BeenThere/App/AppEnvironment.swift`

## Current scope

This is a starter scaffold, not the finished iPhone product. It is meant to give us:

- a real Xcode opening point
- stable Swift models for the API
- a map-first mobile loop we can iterate on next
