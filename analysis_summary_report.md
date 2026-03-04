# OpenAI Codex Bug Issues Analysis Report

**Generated**: 2026-03-04T21:38:24.985762
**Repository**: openai/codex
**Total Issues Analyzed**: 3938
**Label**: bug (all states)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Bug Issues | 3938 |
| Time Period | All time (state=all) |
| Classification Categories | 7 |
| Top Bug Type | tui/rendering (1161 issues, 29.5%) |

---

## Bug Type Distribution

| Bug Type | Count | Percentage |
|----------|-------|------------|
| tui/rendering | 1161 | 29.48% |
| other | 1019 | 25.88% |
| platform/windows | 526 | 13.36% |
| performance/resource | 406 | 10.31% |
| docs/site | 344 | 8.74% |
| integration/auth/billing | 337 | 8.56% |
| web/desktop-ui | 145 | 3.68% |

---

## Architecture

Same 3-stage pipeline as anomalyco/opencode analysis:
1. **Downloader**: Token-rotating batch fetcher (16+ GitHub PATs)
2. **Analyzer**: Heuristic classification with confidence scoring
3. **Report Generator**: Markdown table + statistics

---

## Key Findings

Analysis of 3938 bug issues from openai/codex repository.
