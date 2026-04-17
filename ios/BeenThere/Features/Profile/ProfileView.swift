import SwiftUI

struct ProfileView: View {
    @EnvironmentObject private var authStore: AuthStore

    var body: some View {
        NavigationStack {
            List {
                if let user = authStore.user {
                    Section("Account") {
                        LabeledContent("Username", value: user.username)
                        if !user.email.isEmpty {
                            LabeledContent("Email", value: user.email)
                        }
                    }

                    Section {
                        Button("Sign Out", role: .destructive) {
                            Task {
                                await authStore.logout()
                            }
                        }
                    }
                } else {
                    Section {
                        Button("Sign In or Create Account") {
                            authStore.showingAuthSheet = true
                        }
                    }
                }
            }
            .navigationTitle("Profile")
        }
    }
}
