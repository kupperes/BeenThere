import SwiftUI

@main
struct BeenThereApp: App {
    @StateObject private var authStore = AuthStore()
    @StateObject private var locationStore = LocationStore()

    var body: some Scene {
        WindowGroup {
            RootTabView()
                .environmentObject(authStore)
                .environmentObject(locationStore)
                .task {
                    await authStore.loadCurrentUser()
                }
        }
    }
}
