// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "BlackRoad",
    platforms: [.macOS(.v13), .iOS(.v16)],
    products: [
        .library(name: "BlackRoad", targets: ["BlackRoad"]),
    ],
    targets: [
        .target(name: "BlackRoad", path: "Sources/BlackRoad"),
        .testTarget(name: "BlackRoadTests", dependencies: ["BlackRoad"], path: "Tests"),
    ]
)
