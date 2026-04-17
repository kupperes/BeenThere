import SwiftUI

struct CollectionView: View {
    @EnvironmentObject private var authStore: AuthStore
    @State private var summary: VisitSummaryResponse?
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Group {
                if authStore.user == nil {
                    ContentUnavailableView(
                        "Sign In Required",
                        systemImage: "person.badge.key",
                        description: Text("Sign in to track visited places and grow your collection.")
                    )
                    .overlay(alignment: .bottom) {
                        Button("Sign In") {
                            authStore.showingAuthSheet = true
                        }
                        .buttonStyle(.borderedProminent)
                        .padding()
                    }
                } else if let summary {
                    List {
                        Section("Progress") {
                            Label("\(summary.visitCount) visited places", systemImage: "checkmark.circle.fill")
                        }

                        Section("Recent Visits") {
                            ForEach(summary.recentVisits) { visit in
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(visit.historicSite.name)
                                        .font(.headline)
                                    Text(visit.historicSite.locationSubtitle)
                                        .font(.subheadline)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                } else if let errorMessage {
                    ContentUnavailableView(
                        "Unable to Load Collection",
                        systemImage: "exclamationmark.triangle",
                        description: Text(errorMessage)
                    )
                } else {
                    ProgressView("Loading collection...")
                }
            }
            .navigationTitle("Collection")
            .task(id: authStore.user?.id) {
                await loadSummary()
            }
        }
    }

    private func loadSummary() async {
        guard authStore.user != nil else {
            summary = nil
            return
        }

        do {
            summary = try await APIClient.shared.fetchVisitSummary()
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
