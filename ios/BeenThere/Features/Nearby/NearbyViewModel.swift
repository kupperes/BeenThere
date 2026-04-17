import CoreLocation
import Foundation

@MainActor
final class NearbyViewModel: ObservableObject {
    @Published private(set) var sites: [HistoricSite] = []
    @Published private(set) var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedSite: HistoricSite?

    func loadNearbySites(for location: CLLocation) async {
        isLoading = true
        defer { isLoading = false }

        do {
            let response = try await APIClient.shared.fetchNearbySites(
                latitude: location.coordinate.latitude,
                longitude: location.coordinate.longitude
            )
            sites = response.results
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
