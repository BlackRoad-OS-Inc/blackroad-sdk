# BlackRoad Swift SDK

Swift SDK for BlackRoad OS. Supports macOS 13+ and iOS 16+.

## Installation

```swift
// Package.swift
.package(url: "https://github.com/BlackRoad-OS-Inc/blackroad-sdk", from: "1.0.0")
```

## Usage

```swift
import BlackRoad

let client = BlackRoadClient()

// Chat with an agent
let response = try await client.chat(agent: "LUCIDIA", message: "What is consciousness?")
print(response.content)

// Store a memory
let memory = try await client.remember("User prefers dark mode", type: "fact")

// Recall memories
let results = try await client.recall(query: "user preferences")
```
