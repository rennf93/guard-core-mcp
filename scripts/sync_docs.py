import json
import re
import shutil
import sys
from pathlib import Path

REPOSITORIES = {
    "fastapi-guard": "https://rennf93.github.io/fastapi-guard/latest/",
    "guard-core": "https://rennf93.github.io/guard-core/latest/",
    "guard-agent": "https://rennf93.github.io/guard-agent/latest/",
}

PACKAGE_ROOT = Path(__file__).parent.parent / "guard_core_mcp"
DOCS_ROOT = PACKAGE_ROOT / "_docs"
VERSION_PATTERN = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)


def read_version(repository: Path) -> str:
    match = VERSION_PATTERN.search((repository / "pyproject.toml").read_text())
    if match is None:
        raise SystemExit(f"no version found in {repository}/pyproject.toml")
    return match.group(1)


def sync(package: str, site_url: str) -> dict[str, str]:
    repository = Path("..") / package
    source = repository / "docs"
    if not source.is_dir():
        raise SystemExit(f"{source} not found; clone {package} next to this repo")

    destination = DOCS_ROOT / package
    shutil.rmtree(destination, ignore_errors=True)
    for markdown in sorted(source.rglob("*.md")):
        target = destination / markdown.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(markdown, target)

    return {"site_url": site_url, "version": read_version(repository)}


def main() -> None:
    DOCS_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {
        package: sync(package, site_url) for package, site_url in REPOSITORIES.items()
    }
    (DOCS_ROOT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(f"vendored docs for {', '.join(manifest)}", file=sys.stderr)


if __name__ == "__main__":
    main()
