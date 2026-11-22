// person_matte.swift — Apple Vision person segmentation for a whole video, streamed as raw 8-bit grey frames to stdout.
// Round 14 (22 Nov 2026, research/refs_2026-11-22): the "word behind the head" / depth look needs a per-frame person matte.
//   build:  swiftc -O person_matte.swift -o person_matte
//   run:    ./person_matte <video> <W> <H> [accurate|balanced|fast] | ffmpeg -f rawvideo -pix_fmt gray -s WxH -r <fps> -i - ...
// person_matte.py wraps this (alphamerge with the cut -> VP9+alpha webm the composition plays above the "behind" layer).
// VNSequenceRequestHandler keeps the matte temporally stable (less edge flicker than independent per-image requests).
import Foundation
import AVFoundation
import Vision
import CoreImage

let a = CommandLine.arguments
guard a.count >= 4, let W = Int(a[2]), let H = Int(a[3]) else {
    FileHandle.standardError.write("usage: person_matte <video> <W> <H> [accurate|balanced|fast]\n".data(using: .utf8)!); exit(2)
}
let q = a.count > 4 ? a[4] : "accurate"
let asset = AVURLAsset(url: URL(fileURLWithPath: a[1]))
let sem = DispatchSemaphore(value: 0)
var track: AVAssetTrack?
Task { track = try? await asset.loadTracks(withMediaType: .video).first; sem.signal() }
sem.wait()
guard let vt = track, let reader = try? AVAssetReader(asset: asset) else { FileHandle.standardError.write("cannot read video\n".data(using: .utf8)!); exit(1) }
let out = AVAssetReaderTrackOutput(track: vt, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
out.alwaysCopiesSampleData = false
reader.add(out)
reader.startReading()

let req = VNGeneratePersonSegmentationRequest()
req.qualityLevel = q == "fast" ? .fast : q == "balanced" ? .balanced : .accurate
req.outputPixelFormat = kCVPixelFormatType_OneComponent8
let seq = VNSequenceRequestHandler()
let ctx = CIContext(options: [.workingColorSpace: NSNull()])
var buf = [UInt8](repeating: 0, count: W * H)
let stdout = FileHandle.standardOutput
var n = 0
while let sb = out.copyNextSampleBuffer(), let pb = CMSampleBufferGetImageBuffer(sb) {
    autoreleasepool {
        try? seq.perform([req], on: pb)
        if let m = req.results?.first?.pixelBuffer {
            var ci = CIImage(cvPixelBuffer: m)
            ci = ci.transformed(by: CGAffineTransform(scaleX: CGFloat(W) / ci.extent.width, y: CGFloat(H) / ci.extent.height))
            ctx.render(ci, toBitmap: &buf, rowBytes: W, bounds: CGRect(x: 0, y: 0, width: W, height: H), format: .L8, colorSpace: nil)
        } else {
            for i in 0..<buf.count { buf[i] = 0 }
        }
        stdout.write(Data(buf))
        n += 1
    }
}
FileHandle.standardError.write("person_matte: \(n) frames (\(q))\n".data(using: .utf8)!)
