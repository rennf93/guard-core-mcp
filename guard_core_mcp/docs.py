import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DOCS_ROOT = Path(__file__).parent / "_docs"


@lru_cache(maxsize=1)
def manifest() -> dict[str, dict[str, str]]:
    loaded: dict[str, dict[str, str]] = json.loads(
        (DOCS_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    return loaded


def document_url(package: str, relative_path: str) -> str:
    site_url = manifest()[package]["site_url"]
    slug = Path(relative_path).with_suffix("")
    if slug.name == "index":
        slug = slug.parent
    return site_url if str(slug) == "." else f"{site_url}{slug}/"


def _score(text: str, tokens: list[str]) -> tuple[int, str, str]:
    heading = ""
    best_score = 0
    best_heading = ""
    best_line = ""
    total = 0
    for line in text.splitlines():
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        lowered = line.lower()
        hits = sum(lowered.count(token) for token in tokens)
        total += hits
        if hits > best_score:
            best_score, best_heading, best_line = hits, heading, line.strip()
    return total, best_heading, best_line


def search_docs(
    query: str, package: str | None = None, limit: int = 5
) -> dict[str, Any]:
    tokens = query.lower().split()
    packages = [package] if package else sorted(manifest())
    results: list[dict[str, Any]] = []
    for name in packages:
        root = DOCS_ROOT / name
        for markdown in sorted(root.rglob("*.md")):
            relative = markdown.relative_to(root)
            score, heading, snippet = _score(
                markdown.read_text(encoding="utf-8"), tokens
            )
            if score:
                results.append(
                    {
                        "package": name,
                        "path": str(relative),
                        "heading": heading,
                        "snippet": snippet[:300],
                        "url": document_url(name, str(relative)),
                        "score": score,
                    }
                )
    results.sort(key=lambda result: -int(result["score"]))
    return {"query": query, "results": results[:limit]}


def get_doc(package: str, path: str) -> dict[str, Any]:
    if package not in manifest():
        return {"error": "unknown doc path"}
    root = (DOCS_ROOT / package).resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        return {"error": "unknown doc path"}
    return {
        "package": package,
        "path": path,
        "url": document_url(package, path),
        "content": target.read_text(encoding="utf-8"),
    }
