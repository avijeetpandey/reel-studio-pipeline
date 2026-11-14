// face_boxes.swift — Apple Vision face rectangles for a list of images: prints JSON {path: [x,y,w,h in PIXELS, top-left origin]}
// build:  swiftc -O face_boxes.swift -o face_boxes      run:  ./face_boxes a.png b.png
import Foundation
import Vision
import AppKit

var out: [String: [Double]] = [:]
for p in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: p), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let req = VNDetectFaceRectanglesRequest()
    let h = VNImageRequestHandler(cgImage: cg, options: [:])
    try? h.perform([req])
    let W = Double(cg.width), H = Double(cg.height)
    if let best = (req.results ?? []).max(by: { $0.boundingBox.width * $0.boundingBox.height < $1.boundingBox.width * $1.boundingBox.height }) {
        let b = best.boundingBox
        out[p] = [b.minX * W, (1 - b.maxY) * H, b.width * W, b.height * H]
    }
}
let d = try! JSONSerialization.data(withJSONObject: out)
print(String(data: d, encoding: .utf8)!)
