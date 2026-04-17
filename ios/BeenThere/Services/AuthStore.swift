import Foundation

@MainActor
final class AuthStore: ObservableObject {
    @Published private(set) var user: User?
    @Published var showingAuthSheet = false
    @Published var errorMessage: String?

    func loadCurrentUser() async {
        do {
            let response = try await APIClient.shared.currentUser()
            user = response.user
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func login(username: String, password: String) async -> Bool {
        do {
            let response = try await APIClient.shared.login(username: username, password: password)
            user = response.user
            showingAuthSheet = false
            errorMessage = nil
            return true
        } catch {
            errorMessage = error.localizedDescription
            return false
        }
    }

    func register(username: String, email: String, password: String) async -> Bool {
        do {
            let response = try await APIClient.shared.register(username: username, email: email, password: password)
            user = response.user
            showingAuthSheet = false
            errorMessage = nil
            return true
        } catch {
            errorMessage = error.localizedDescription
            return false
        }
    }

    func logout() async {
        do {
            try await APIClient.shared.logout()
            user = nil
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
