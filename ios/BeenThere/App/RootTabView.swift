import SwiftUI

struct RootTabView: View {
    @EnvironmentObject private var authStore: AuthStore

    var body: some View {
        TabView {
            NearbyMapView()
                .tabItem {
                    Label("Nearby", systemImage: "map")
                }

            CollectionView()
                .tabItem {
                    Label("Collection", systemImage: "checklist")
                }

            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.crop.circle")
                }
        }
        .sheet(isPresented: Binding(
            get: { authStore.showingAuthSheet && authStore.user == nil },
            set: { authStore.showingAuthSheet = $0 }
        )) {
            LoginView()
        }
    }
}
