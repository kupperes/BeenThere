import SwiftUI

struct SiteDetailView: View {
    @EnvironmentObject private var authStore: AuthStore
    @State private var site: HistoricSite
    @State private var isLoading = false
    @State private var errorMessage: String?

    init(site: HistoricSite) {
        _site = State(initialValue: site)
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(site.name)
                            .font(.title2.bold())

                        Text(site.locationSubtitle)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)

                        if let distanceMiles = site.distanceMiles {
                            Label("\(distanceMiles.formatted()) miles away", systemImage: "location")
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                        }
                    }

                    if !site.summary.isEmpty {
                        Text(site.summary)
                            .font(.body)
                    }

                    if !site.description.isEmpty {
                        Text(site.description)
                            .font(.callout)
                            .foregroundStyle(.secondary)
                    }

                    VStack(alignment: .leading, spacing: 10) {
                        Label(site.designation, systemImage: "building.columns")
                        Label(site.category.capitalized, systemImage: "tag")

                        if let sourceFeed = site.sourceFeed {
                            Label(sourceFeed.name, systemImage: "link")
                        } else {
                            Label(site.sourceName, systemImage: "link")
                        }
                    }
                    .font(.subheadline)

                    if let referenceURL = site.referenceURL {
                        Link(destination: referenceURL) {
                            Label("Open Source", systemImage: "arrow.up.right.square")
                        }
                    }

                    if let wikipediaURL = site.wikipediaURL {
                        Link(destination: wikipediaURL) {
                            Label("Open Wikipedia", systemImage: "book")
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
            }
            .navigationTitle("Place Details")
            .navigationBarTitleDisplayMode(.inline)
            .safeAreaInset(edge: .bottom) {
                visitButton
            }
            .alert("Request Failed", isPresented: Binding(
                get: { errorMessage != nil },
                set: { shouldShow in
                    if !shouldShow {
                        errorMessage = nil
                    }
                }
            ), actions: {
                Button("OK") { errorMessage = nil }
            }, message: {
                Text(errorMessage ?? "")
            })
        }
    }

    private var visitButton: some View {
        Button {
            Task {
                await toggleVisited()
            }
        } label: {
            HStack {
                if isLoading {
                    ProgressView()
                }
                Text(site.visited ? "Mark as Not Visited" : "Mark as Visited")
            }
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(.borderedProminent)
        .padding()
        .disabled(authStore.user == nil || isLoading)
    }

    private func toggleVisited() async {
        guard authStore.user != nil else {
            authStore.showingAuthSheet = true
            return
        }

        isLoading = true
        defer { isLoading = false }

        do {
            let response: VisitMutationResponse
            if site.visited {
                response = try await APIClient.shared.unmarkVisited(siteID: site.id)
            } else {
                response = try await APIClient.shared.markVisited(siteID: site.id)
            }
            site = response.site
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
