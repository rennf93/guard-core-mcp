from pathlib import Path

from guard_core_mcp.docs import get_doc, knowledge_manifest, search_docs

KNOWLEDGE_ROOT = (
    Path(__file__).resolve().parent.parent / "guard_core_mcp" / "_knowledge"
)


def test_search_finds_a_page_and_cites_its_url() -> None:
    results = search_docs("rate limiting")["results"]

    assert results
    assert results[0]["url"].startswith("https://rennf93.github.io/")
    assert results[0]["path"].endswith(".md")
    assert results[0]["snippet"]


def test_search_can_be_scoped_to_one_package() -> None:
    results = search_docs("detection", package="guard-core")["results"]

    assert {result["package"] for result in results} == {"guard-core"}


def test_search_respects_the_limit() -> None:
    assert len(search_docs("the", limit=3)["results"]) <= 3


def test_index_pages_collapse_to_their_directory_url() -> None:
    from guard_core_mcp.docs import document_url

    assert (
        document_url("guard-core", "index.md")
        == "https://rennf93.github.io/guard-core/latest/"
    )
    assert document_url("guard-core", "api/models.md") == (
        "https://rennf93.github.io/guard-core/latest/api/models/"
    )


def test_get_doc_returns_the_page_text() -> None:
    result = get_doc("guard-core", "index.md")

    assert result["content"].strip()
    assert result["url"] == "https://rennf93.github.io/guard-core/latest/"


def test_get_doc_rejects_path_traversal() -> None:
    assert get_doc("guard-core", "../../../etc/passwd")["error"] == "unknown doc path"


def test_get_doc_rejects_an_unknown_package() -> None:
    assert get_doc("django-guard", "index.md")["error"] == "unknown doc path"


def test_search_covers_the_knowledge_corpus() -> None:
    results = search_docs("INGEST_MAX_PAYLOAD_BYTES")["results"]

    assert any(result["package"] == "guard-core-app" for result in results)
    app_result = next(
        result for result in results if result["package"] == "guard-core-app"
    )
    assert app_result["url"] == "https://github.com/rennf93/guard-core-app"


def test_search_can_be_scoped_to_one_knowledge_package() -> None:
    results = search_docs("engine_commit", package="guard-core-go")["results"]

    assert results
    assert {result["package"] for result in results} == {"guard-core-go"}


def test_search_for_an_unknown_package_silently_matches_nothing() -> None:
    assert search_docs("rate limiting", package="django-guard")["results"] == []


def test_get_doc_returns_a_knowledge_page() -> None:
    result = get_doc("guard-core-app", "index.md")

    assert "ingestion contract" in result["content"]
    assert result["url"] == "https://github.com/rennf93/guard-core-app"
    assert result["package"] == "guard-core-app"


def test_get_doc_rejects_path_traversal_in_knowledge() -> None:
    assert get_doc("guard-core-app", "../../_docs/manifest.json")["error"] == (
        "unknown doc path"
    )


def test_knowledge_manifest_covers_every_handwritten_repo() -> None:
    expected = {
        "guard-core-app",
        "guard-core-go",
        "guard-core-php",
        "guard-core-rs",
        "guard-agent-go",
        "guard-agent-php",
        "guard-agent-rs",
        "guard-agent-ts",
    }

    manifest = knowledge_manifest()

    assert set(manifest) == expected
    for name, entry in manifest.items():
        assert entry["site_url"].startswith("https://github.com/rennf93/")
        assert entry["version"]
        assert (KNOWLEDGE_ROOT / name / "index.md").is_file()
