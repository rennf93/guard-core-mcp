import json
from pathlib import Path

DOCS_ROOT = Path(__file__).parent.parent / "guard_core_mcp" / "_docs"


def test_every_package_is_vendored_with_markdown() -> None:
    manifest = json.loads((DOCS_ROOT / "manifest.json").read_text())

    assert set(manifest) == {"fastapi-guard", "guard-core", "guard-agent"}
    for package, entry in manifest.items():
        assert entry["site_url"].startswith("https://")
        assert entry["version"]
        assert list((DOCS_ROOT / package).rglob("*.md"))


def test_only_markdown_is_vendored() -> None:
    assert not [
        path
        for path in DOCS_ROOT.rglob("*")
        if path.is_file() and path.suffix not in {".md", ".json"}
    ]
