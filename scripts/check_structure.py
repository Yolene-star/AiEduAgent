from pathlib import Path


REQUIRED_PATHS = [
    "backend/app/main.py",
    "backend/tests/test_api.py",
    "frontend/app/page.tsx",
    "frontend/package.json",
    "docs/testing-policy.md",
    "tests/behavior/README.md",
    "tests/tts/README.md",
    ".env.example",
    ".gitignore",
    "THIRD_PARTY_NOTICES.md",
]


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not Path(path).exists()]
    if missing:
        for path in missing:
            print(f"missing: {path}")
        return 1
    print("structure check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
