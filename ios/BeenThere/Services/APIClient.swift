import Foundation

enum APIError: LocalizedError {
    case invalidResponse
    case server(String)
    case decoding(Error)
    case transport(Error)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "The server returned an invalid response."
        case let .server(message):
            return message
        case let .decoding(error):
            return "Failed to decode the server response: \(error.localizedDescription)"
        case let .transport(error):
            return error.localizedDescription
        }
    }
}

final class APIClient {
    static let shared = APIClient()

    private let baseURL: URL
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    private let session: URLSession

    init(baseURL: URL = AppEnvironment.apiBaseURL) {
        self.baseURL = baseURL

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        self.decoder = decoder

        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        self.encoder = encoder

        let configuration = URLSessionConfiguration.default
        configuration.httpCookieStorage = .shared
        configuration.httpShouldSetCookies = true
        configuration.requestCachePolicy = .reloadIgnoringLocalCacheData
        self.session = URLSession(configuration: configuration)
    }

    func fetchNearbySites(latitude: Double, longitude: Double, radiusMiles: Double = 10) async throws -> PaginatedResponse<HistoricSite> {
        var components = URLComponents(url: baseURL.appending(path: "/api/sites/nearby/"), resolvingAgainstBaseURL: false)
        components?.queryItems = [
            URLQueryItem(name: "lat", value: String(latitude)),
            URLQueryItem(name: "lng", value: String(longitude)),
            URLQueryItem(name: "radius", value: String(radiusMiles)),
            URLQueryItem(name: "page_size", value: "50"),
        ]

        guard let url = components?.url else {
            throw APIError.invalidResponse
        }

        return try await sendRequest(url: url)
    }

    func fetchSiteDetail(siteID: Int) async throws -> HistoricSite {
        try await sendRequest(url: baseURL.appending(path: "/api/sites/\(siteID)/"))
    }

    func register(username: String, email: String, password: String) async throws -> AuthResponse {
        try await sendRequest(
            url: baseURL.appending(path: "/api/auth/register/"),
            method: "POST",
            body: ["username": username, "email": email, "password": password]
        )
    }

    func login(username: String, password: String) async throws -> AuthResponse {
        try await sendRequest(
            url: baseURL.appending(path: "/api/auth/login/"),
            method: "POST",
            body: ["username": username, "password": password]
        )
    }

    func logout() async throws {
        struct LogoutResponse: Decodable {
            let success: Bool
        }

        _ = try await sendRequest(
            url: baseURL.appending(path: "/api/auth/logout/"),
            method: "POST"
        ) as LogoutResponse
    }

    func currentUser() async throws -> CurrentUserResponse {
        try await sendRequest(url: baseURL.appending(path: "/api/auth/me/"))
    }

    func markVisited(siteID: Int) async throws -> VisitMutationResponse {
        try await sendRequest(
            url: baseURL.appending(path: "/api/sites/\(siteID)/visit/"),
            method: "POST"
        )
    }

    func unmarkVisited(siteID: Int) async throws -> VisitMutationResponse {
        try await sendRequest(
            url: baseURL.appending(path: "/api/sites/\(siteID)/visit/"),
            method: "DELETE"
        )
    }

    func fetchVisitSummary() async throws -> VisitSummaryResponse {
        try await sendRequest(url: baseURL.appending(path: "/api/visits/summary/"))
    }

    private func sendRequest<ResponseType: Decodable>(
        url: URL,
        method: String = "GET",
        body: [String: String]? = nil
    ) async throws -> ResponseType {
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        if let body {
            request.httpBody = try encoder.encode(body)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }

        do {
            let (data, response) = try await session.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }

            guard (200 ..< 300).contains(httpResponse.statusCode) else {
                if
                    let payload = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                    let message = payload["error"] as? String
                {
                    throw APIError.server(message)
                }
                throw APIError.server("The server returned status code \(httpResponse.statusCode).")
            }

            do {
                return try decoder.decode(ResponseType.self, from: data)
            } catch {
                throw APIError.decoding(error)
            }
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError.transport(error)
        }
    }
}
