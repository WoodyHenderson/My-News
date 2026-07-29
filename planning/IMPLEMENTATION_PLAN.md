# My News: Implementation Plan

## 1. Objective

Build a local, headless service that:

- Collects recent stories from trusted sources.
- Groups duplicate reports into one story with multiple outlet links.
- Ranks stories by user interests and recency.
- Labels restricted links (PAYWALLED/RESTRICTED).
- Generates a PDF digest with clickable links.
- Persists run history and cache state locally.

This plan defines the build order, implementation checkpoints, and acceptance criteria.

## 2. Delivery Strategy

Use a vertical-slice approach:

1. Prove an end-to-end flow with fixtures first.
2. Add validation and CLI controls.
3. Add real collection and persistence.
4. Add enrichment, grouping quality, and reporting.
5. Harden and document.

Guiding principle: use trusted dependencies where they reduce risk and complexity.

## 3. Recommended Stack

Runtime dependencies:

- typer
- pydantic
- pyyaml
- httpx
- feedparser
- trafilatura
- jinja2
- weasyprint
- platformdirs

Dev dependencies:

- pytest
- pytest-cov
- respx
- pypdf
- ruff
- mypy or pyright

## 4. Repository Setup Order

1. Create baseline project files.
2. Add package structure and modules.
3. Add test scaffolding and fixtures.
4. Add tool configuration (lint, type check, tests).
5. Add lockfile and dependency pinning.

Target structure:

- pyproject.toml
- README.md
- config/example.yaml
- src/my_news/*
- tests/unit/*
- tests/integration/*
- tests/fixtures/*
- output/.gitkeep

## 5. Phase-by-Phase Implementation

### Phase 0: Bootstrapping and Tooling

Tasks:

1. Initialize project metadata and dependencies.
2. Configure linting, typing, and test settings.
3. Add basic CLI entrypoint skeleton.
4. Add .gitignore for .venv, output artifacts, caches.

Deliverables:

- Installable package skeleton.
- Passing empty test suite.
- CLI help command works.

Exit criteria:

- my-news --help works.
- ruff check passes.
- pytest passes.

### Phase 1: Vertical Slice (Offline)

Goal: prove a full run without real network.

Tasks:

1. Implement minimal models:
   - ArticleCandidate
   - RankedStory
   - SourceResult
2. Implement fixture feed parser path.
3. Implement simple grouping:
   - exact normalized canonical URL grouping
4. Implement simple ranking:
   - title and summary keyword scoring
5. Render HTML template.
6. Generate PDF with WeasyPrint.
7. Add one integration test from fixture feed to parseable PDF.

Deliverables:

- One deterministic fixture-based digest.

Exit criteria:

- Integration test confirms:
  - grouped stories
   - clickable links
  - valid PDF output

### Phase 2: Config Schema and CLI Behavior

Tasks:

1. Implement full YAML schema with pydantic.
2. Add commands:
   - init
   - validate
   - run --dry-run
3. Add cross-reference validation:
   - source IDs unique
   - interest IDs unique
   - source interests must exist
4. Add path safety validation for output filename and directory.

Deliverables:

- config/example.yaml
- reliable validation errors with field paths

Exit criteria:

- validate command rejects malformed configs.
- dry-run prints ranked stories without PDF write.

### Phase 3: HTTP Layer and Feed Collector

Tasks:

1. Build shared HTTP client with:
   - explicit timeouts
   - retries
   - response size limits
   - redirect policy
2. Add conditional requests with ETag and Last-Modified.
3. Implement feed collector with source-level diagnostics.
4. Add sources check and discover-feed commands.

Deliverables:

- feed collection pipeline for real feeds.

Exit criteria:

- tests cover 200, 304, retry, and failure handling.
- one failing source does not fail whole run.

### Phase 4: Persistence and Run History

Tasks:

1. Implement SQLite schema and migrations:
   - source_state
   - articles
   - runs
   - run_stories
   - story_outlets
2. Persist cache validators and run outcomes.
3. Persist story/outlet mappings and emitted history.
4. Implement repeat suppression window.

Deliverables:

- durable stateful runs.

Exit criteria:

- second run uses cache validators.
- recently emitted stories suppressed by default.

### Phase 5: Full Grouping Logic

Tasks:

1. Strengthen normalization:
   - URL canonicalization
   - tracking parameter stripping
   - whitespace normalization
2. Implement grouped-story assembly with source diversity retained.
3. Define primary article selection rules for a story.
4. Preserve all outlet links for each story.

Deliverables:

- robust multi-outlet story grouping.

Exit criteria:

- integration tests verify:
  - grouped duplicates
  - all outlet URLs preserved
  - deterministic primary headline selection

### Phase 6: Paywall and Restriction Labeling

Tasks:

1. Add access_status classification per outlet:
   - free
   - restricted
   - unknown
2. Add detection heuristics:
   - JSON-LD isAccessibleForFree=false
   - known premium markers
   - HTTP 401/402/403 indicators
   - content markers like subscriber-only
3. Persist access_reason and access_evidence.
4. Render PAYWALLED/RESTRICTED badge in PDF for restricted links.

Deliverables:

- restricted-link labeling in output and report.

Exit criteria:

- tests verify restricted links show badge.
- unknown links remain unlabeled.

### Phase 7: Ranking and Explainability

Tasks:

1. Implement full scoring formula from DETAILED_PLAN.
2. Add phrase-first matching and overlap suppression.
3. Add exclusion and required-term gates.
4. Add recency and source-priority contributions.
5. Persist score breakdown per story.
6. Implement explain command by run_id and story_id.

Deliverables:

- deterministic, explainable ranking.

Exit criteria:

- table-driven ranking tests pass with exact expected contributions.

### Phase 8: Enrichment Pipeline

Tasks:

1. Add preliminary ranking before enrichment.
2. Build bounded enrichment queue.
3. Use trafilatura for metadata extraction.
4. Re-run normalization and grouping after enrichment.
5. Use body text for ranking in-memory where helpful, but do not persist full body text by default.
6. Ensure body text is not rendered in digest.

Deliverables:

- higher metadata quality without uncontrolled crawl cost.

Exit criteria:

- enrichment tests verify bounded requests and improved metadata completeness.

### Phase 9: Reporting and PDF Production Quality

Tasks:

1. Add JSON run report with:
   - counts and timings
   - source diagnostics
   - ranking outputs
   - free/restricted/unknown counts
2. Add atomic file write for PDF output.
3. Add formatting polish:
   - page footer
   - URL wrapping
   - badge styling

Deliverables:

- production-quality digest output and diagnostics.

Exit criteria:

- parseable PDF
- link annotations present
- report and output remain consistent

### Phase 10: Real Sources and Hardening

Tasks:

1. Add initial trusted feed sources.
2. Add one HTML adapter only if a source lacks feed coverage.
3. Add contract tests per adapter.
4. Add interruption-safe cleanup.
5. Finalize README usage and troubleshooting.

Deliverables:

- first usable real-world run with configured sources.

Exit criteria:

- end-to-end run succeeds on real configuration.
- lint, typing, tests, and smoke checks all pass.

## 6. Cross-Cutting Quality Gates

Apply in every phase:

1. Add tests with each behavior change.
2. Keep deterministic outputs for fixed fixtures and clock.
3. Never bypass access controls.
4. Continue on partial source failures.
5. Prefer trusted dependencies to custom reinvention.

## 7. Implementation Order Summary

Build in this exact order:

1. Tooling and project skeleton.
2. Offline vertical slice to PDF.
3. Config and CLI.
4. Real feed collection and HTTP resilience.
5. SQLite state and repeat suppression.
6. Robust grouping with multi-outlet links.
7. Access restriction labeling.
8. Full ranking and explainability.
9. Enrichment and re-grouping.
10. Reporting, polish, and hardening.
11. Real source onboarding.

## 8. Immediate Next Action

Start with Phase 0 and Phase 1 in one sprint:

- Create the project scaffold.
- Implement fixture-only feed -> grouped stories -> ranked stories -> PDF.
- Add one integration test that proves grouped outlet links and clickable PDF output.

This gives a validated core before spending effort on network edge cases and persistence.
