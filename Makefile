sync-docs:
	uv run python scripts/sync_docs.py

check-docs-drift: sync-docs
	git diff --exit-code guard_core_mcp/_docs

.PHONY: sync-docs check-docs-drift
