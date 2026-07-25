from guard_core_mcp.docs import get_doc, search_docs


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
