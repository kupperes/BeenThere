import CoreLocation
import Foundation

struct PaginatedResponse<Value: Decodable>: Decodable {
    let count: Int
    let page: Int
    let pageSize: Int
    let totalPages: Int
    let results: [Value]
}

struct SourceFeed: Codable, Identifiable, Hashable {
    let id: Int
    let name: String
    let slug: String
    let jurisdictionLevel: String
    let jurisdictionName: String
    let sourceType: String
    let homepageURL: URL?
    let downloadURL: URL?
    let license: String?
    let refreshStrategy: String?
    let isActive: Bool
}

struct HistoricSite: Codable, Identifiable, Hashable {
    let id: Int
    let name: String
    let summary: String
    let description: String
    let latitude: Double?
    let longitude: Double?
    let address: String
    let city: String
    let state: String
    let category: String
    let designation: String
    let era: String
    let sourceFeed: SourceFeed?
    let sourceName: String
    let sourceID: String
    let wikipediaURL: URL?
    let referenceURL: URL?
    let imageURL: URL?
    let isVerified: Bool
    let distanceMiles: Double?
    let visited: Bool

    var coordinate: CLLocationCoordinate2D? {
        guard let latitude, let longitude else { return nil }
        return CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }

    var locationSubtitle: String {
        [city, state].filter { !$0.isEmpty }.joined(separator: ", ")
    }
}

struct User: Codable, Identifiable, Hashable {
    let id: Int
    let username: String
    let email: String
    let firstName: String
    let lastName: String
}

struct CurrentUserResponse: Codable {
    let user: User?
}

struct AuthResponse: Codable {
    let user: User
}

struct UserVisit: Codable, Identifiable, Hashable {
    let id: Int
    let historicSite: HistoricSite
    let visitedAt: String
}

struct VisitSummaryResponse: Codable {
    let visitCount: Int
    let recentVisits: [UserVisit]
}

struct VisitMutationResponse: Codable {
    let created: Bool?
    let deleted: Bool?
    let visit: UserVisit?
    let site: HistoricSite
}
