from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = PROJECT_ROOT / "frontend" / "public" / "vendor" / "sherpa-onnx-tts"
REQUIRED_FILES = [
    "sherpa-onnx-tts.worker.js",
    "sherpa-onnx-tts.js",
    "sherpa-onnx-wasm-main-tts.js",
    "sherpa-onnx-wasm-main-tts.wasm",
]


def main() -> int:
    print(f"SHERPA_TTS_ASSET_DIR={ASSET_DIR}")
    missing = []
    for filename in REQUIRED_FILES:
        path = ASSET_DIR / filename
        if path.exists():
            print(f"OK {filename} {path.stat().st_size} bytes")
        else:
            print(f"MISSING {filename}")
            missing.append(filename)

    extra_assets = [
        path
        for path in ASSET_DIR.iterdir()
        if path.is_file() and path.name not in {".gitkeep", "README.md", *REQUIRED_FILES}
    ]
    if extra_assets:
        print("MODEL_OR_DATA_ASSETS=")
        for path in sorted(extra_assets):
            print(f"- {path.name} {path.stat().st_size} bytes")

    if missing:
        print("RESULT=missing_required_runtime_files")
        return 1

    print("RESULT=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
