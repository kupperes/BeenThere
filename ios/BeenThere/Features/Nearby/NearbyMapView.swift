import MapKit
import SwiftUI

struct NearbyMapView: View {
    @EnvironmentObject private var authStore: AuthStore
    @EnvironmentObject private var locationStore: LocationStore
    @StateObject private var viewModel = NearbyViewModel()
    @State private var cameraPosition: MapCameraPosition = .automatic

    var body: some View {
        NavigationStack {
            Group {
                switch locationStore.authorizationStatus {
                case .notDetermined:
                    permissionState
                case .denied, .restricted:
                    deniedState
                default:
                    mapContent
                }
            }
            .navigationTitle("Nearby History")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(authStore.user == nil ? "Sign In" : "Account") {
                        authStore.showingAuthSheet = true
                    }
                }
            }
            .task(id: locationStore.currentLocation) {
                guard let location = locationStore.currentLocation else { return }
                cameraPosition = .region(
                    MKCoordinateRegion(
                        center: location.coordinate,
                        span: MKCoordinateSpan(latitudeDelta: 0.18, longitudeDelta: 0.18)
                    )
                )
                await viewModel.loadNearbySites(for: location)
            }
            .sheet(item: $viewModel.selectedSite) { site in
                SiteDetailView(site: site)
            }
        }
    }

    private var permissionState: some View {
        ContentUnavailableView(
            "Allow Location Access",
            systemImage: "location.circle",
            description: Text("BeenThere uses your foreground location to show historical places near you.")
        )
        .overlay(alignment: .bottom) {
            Button("Allow Location Access") {
                locationStore.requestWhenInUseAuthorization()
            }
            .buttonStyle(.borderedProminent)
            .padding()
        }
    }

    private var deniedState: some View {
        ContentUnavailableView(
            "Location Needed",
            systemImage: "location.slash",
            description: Text("Enable location in Settings to discover nearby historical sites.")
        )
    }

    private var mapContent: some View {
        ZStack(alignment: .bottom) {
            Map(position: $cameraPosition) {
                ForEach(viewModel.sites) { site in
                    if let coordinate = site.coordinate {
                        Annotation(site.name, coordinate: coordinate) {
                            Button {
                                viewModel.selectedSite = site
                            } label: {
                                VStack(spacing: 4) {
                                    Image(systemName: site.visited ? "checkmark.seal.fill" : "building.columns.fill")
                                        .font(.title3)
                                    Text(site.name)
                                        .font(.caption2)
                                        .lineLimit(1)
                                }
                                .padding(8)
                                .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 12))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }

                UserAnnotation()
            }
            .mapControls {
                MapCompass()
                MapUserLocationButton()
            }

            if viewModel.isLoading {
                ProgressView("Loading nearby places...")
                    .padding()
                    .background(.ultraThinMaterial, in: Capsule())
                    .padding()
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .font(.footnote)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
                    .padding()
            }
        }
        .onAppear {
            locationStore.startUpdatingLocationIfAuthorized()
        }
    }
}
