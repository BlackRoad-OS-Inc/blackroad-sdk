// Copyright (c) 2025-2026 BlackRoad OS, Inc. All Rights Reserved.
import Foundation

/// BlackRoad Swift SDK — tokenless gateway client
public final class BlackRoadClient: @unchecked Sendable {
    public let baseURL: URL
    private let session: URLSession

    public init(baseURL: URL = URL(string: "http://127.0.0.1:8787")!, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    // MARK: - Health

    public func health() async throws -> HealthResponse {
        try await get("/v1/health")
    }

    // MARK: - Agents

    public func agents() async throws -> AgentsResponse {
        try await get("/v1/agents")
    }

    // MARK: - Chat

    public func chat(agent: String? = nil, message: String, model: String? = nil) async throws -> ChatResponse {
        let body = ChatRequest(agent: agent, message: message, model: model, stream: false)
        return try await post("/v1/chat", body: body)
    }

    // MARK: - Memory

    public func remember(_ content: String, type: String = "fact") async throws -> MemoryEntry {
        let body = MemoryRequest(content: content, type: type)
        return try await post("/v1/memory", body: body)
    }

    public func recall(query: String, limit: Int = 10) async throws -> [MemoryEntry] {
        let response: MemorySearchResponse = try await get("/v1/memory/search?q=\(query.urlEncoded)&limit=\(limit)")
        return response.results
    }

    // MARK: - Private Helpers

    private func get<T: Decodable>(_ path: String) async throws -> T {
        let url = baseURL.appendingPathComponent(path)
        let (data, response) = try await session.data(from: url)
        try validate(response)
        return try JSONDecoder().decode(T.self, from: data)
    }

    private func post<B: Encodable, T: Decodable>(_ path: String, body: B) async throws -> T {
        var req = URLRequest(url: baseURL.appendingPathComponent(path))
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try JSONEncoder().encode(body)
        let (data, response) = try await session.data(for: req)
        try validate(response)
        return try JSONDecoder().decode(T.self, from: data)
    }

    private func validate(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw BlackRoadError.httpError((response as? HTTPURLResponse)?.statusCode ?? 0)
        }
    }
}

// MARK: - Models

public struct HealthResponse: Codable {
    public let status: String
    public let version: String
    public let uptime: Double
}

public struct AgentsResponse: Codable {
    public let agents: [Agent]
}

public struct Agent: Codable, Identifiable {
    public let id: String
    public let name: String
    public let title: String
    public let role: String
    public let color: String
    public let capabilities: [String]
}

public struct ChatRequest: Codable {
    public let agent: String?
    public let message: String
    public let model: String?
    public let stream: Bool
}

public struct ChatResponse: Codable {
    public let content: String
    public let agent: String?
    public let model: String
    public let usage: TokenUsage?
}

public struct TokenUsage: Codable {
    public let promptTokens: Int
    public let completionTokens: Int
    public let totalTokens: Int
}

public struct MemoryRequest: Codable {
    public let content: String
    public let type: String
}

public struct MemoryEntry: Codable, Identifiable {
    public let id: String
    public let hash: String
    public let content: String
    public let type: String
    public let truthState: Int
    public let timestamp: Date
}

public struct MemorySearchResponse: Codable {
    public let results: [MemoryEntry]
}

// MARK: - Error

public enum BlackRoadError: Error, LocalizedError {
    case httpError(Int)
    case decodingError(String)

    public var errorDescription: String? {
        switch self {
        case .httpError(let code): return "HTTP error: \(code)"
        case .decodingError(let msg): return "Decoding error: \(msg)"
        }
    }
}

private extension String {
    var urlEncoded: String {
        addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? self
    }
}
