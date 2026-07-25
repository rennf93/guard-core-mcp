import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "sync_docs.py"
_SPEC = importlib.util.spec_from_file_location("sync_docs", SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
sync_docs = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sync_docs)


def test_read_version_reads_the_pyproject_version(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "9.9.9"\n')

    assert sync_docs.read_version(tmp_path) == "9.9.9"


def test_read_version_raises_when_no_version_line_matches(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "no-version"\n')

    with pytest.raises(SystemExit, match="no version found"):
        sync_docs.read_version(tmp_path)


def test_sync_raises_when_sibling_docs_directory_is_missing(
    tmp_path, monkeypatch
) -> None:
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    (tmp_path / "example-package").mkdir()
    monkeypatch.chdir(workdir)

    with pytest.raises(SystemExit, match="not found"):
        sync_docs.sync("example-package", "https://example.invalid/")


def test_sync_copies_markdown_and_mirrors_directory_structure(
    tmp_path, monkeypatch
) -> None:
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    repository = tmp_path / "example-package"
    docs = repository / "docs"
    (docs / "nested").mkdir(parents=True)
    (docs / "index.md").write_text("# Index\n")
    (docs / "nested" / "page.md").write_text("# Page\n")
    (docs / "nested" / "image.png").write_bytes(b"not markdown")
    (repository / "pyproject.toml").write_text('version = "1.2.3"\n')
    monkeypatch.chdir(workdir)
    monkeypatch.setattr(sync_docs, "DOCS_ROOT", tmp_path / "_docs")

    entry = sync_docs.sync("example-package", "https://example.invalid/")

    destination = tmp_path / "_docs" / "example-package"
    assert entry == {"site_url": "https://example.invalid/", "version": "1.2.3"}
    assert (destination / "index.md").read_text() == "# Index\n"
    assert (destination / "nested" / "page.md").read_text() == "# Page\n"
    assert not (destination / "nested" / "image.png").exists()


def test_sync_is_idempotent_and_drops_files_removed_from_the_source(
    tmp_path, monkeypatch
) -> None:
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    repository = tmp_path / "example-package"
    docs = repository / "docs"
    docs.mkdir(parents=True)
    (docs / "index.md").write_text("# Index\n")
    (docs / "stale.md").write_text("# Stale\n")
    (repository / "pyproject.toml").write_text('version = "1.2.3"\n')
    monkeypatch.chdir(workdir)
    monkeypatch.setattr(sync_docs, "DOCS_ROOT", tmp_path / "_docs")
    destination = tmp_path / "_docs" / "example-package"

    sync_docs.sync("example-package", "https://example.invalid/")
    first_run = {
        path.relative_to(destination): path.read_bytes()
        for path in destination.rglob("*.md")
    }

    sync_docs.sync("example-package", "https://example.invalid/")
    second_run = {
        path.relative_to(destination): path.read_bytes()
        for path in destination.rglob("*.md")
    }
    assert second_run == first_run

    (docs / "stale.md").unlink()
    sync_docs.sync("example-package", "https://example.invalid/")

    assert {path.name for path in destination.rglob("*.md")} == {"index.md"}
