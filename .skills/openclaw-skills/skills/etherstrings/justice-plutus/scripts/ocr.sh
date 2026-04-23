#!/bin/bash
# 用法：./ocr.sh image1.jpg [image2.jpg ...]
# 输出：识别出的股票代码（6位数字），逗号分隔

set -euo pipefail

extract_codes() {
    local text="$1"
    echo "$text" | grep -oE '\b[0-9]{6}\b' | sort -u | tr '\n' ',' | sed 's/,$//'
}

ocr_macos() {
    local image="$1"
    # 使用 macOS Vision 框架通过 swift 内联脚本识别
    swift - "$image" <<'SWIFT' 2>/dev/null
import Vision
import Foundation

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path)
guard let cgImage = NSImage(contentsOf: url)?.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    exit(1)
}
let request = VNRecognizeTextRequest { req, _ in
    let results = req.results as? [VNRecognizedTextObservation] ?? []
    let text = results.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
    print(text)
}
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
try? VNImageRequestHandler(cgImage: cgImage).perform([request])
SWIFT
}

ocr_tesseract() {
    local image="$1"
    tesseract "$image" stdout -l chi_sim+eng 2>/dev/null
}

all_codes=""

for image in "$@"; do
    if [[ ! -f "$image" ]]; then
        echo "警告: 文件不存在: $image" >&2
        continue
    fi

    text=""
    if [[ "$(uname)" == "Darwin" ]]; then
        text=$(ocr_macos "$image" 2>/dev/null) || true
    fi

    if [[ -z "$text" ]] && command -v tesseract &>/dev/null; then
        text=$(ocr_tesseract "$image") || true
    fi

    if [[ -z "$text" ]]; then
        echo "错误: 无法识别图片 $image（需要 macOS 或 tesseract）" >&2
        continue
    fi

    codes=$(extract_codes "$text")
    if [[ -n "$codes" ]]; then
        if [[ -n "$all_codes" ]]; then
            all_codes="$all_codes,$codes"
        else
            all_codes="$codes"
        fi
    fi
done

# 去重并输出
echo "$all_codes" | tr ',' '\n' | sort -u | tr '\n' ',' | sed 's/,$//'
