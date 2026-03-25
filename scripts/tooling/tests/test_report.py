# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
import json
import re

from cli.misc.html_report import TEMPLATE_DIR, generate_report, write_report
from lib.known_good import KnownGood
from lib.known_good.module import Module

# ---------------------------------------------------------------------------
# generate_report – return type and structure
# ---------------------------------------------------------------------------


class TestGenerateReportStructure:
    def test_returns_string(self, minimal_known_good):
        assert isinstance(generate_report(minimal_known_good, TEMPLATE_DIR), str)

    def test_is_html(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert html.strip().startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_contains_title(self, minimal_known_good):
        assert "Known Good Status" in generate_report(minimal_known_good, TEMPLATE_DIR)

    def test_contains_timestamp(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "2026-01-01T00:00:00+00:00Z" in html

    def test_contains_module_json(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "score_baselibs" in html
        assert "eclipse-score/baselibs" in html

    def test_embedded_json_is_valid(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        # Extract the JS array assigned to MODULES
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        assert match, "MODULES array not found in HTML"
        data = json.loads(match.group(1))
        assert isinstance(data, list)
        assert len(data) == 1

    def test_module_entry_fields(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        entry = json.loads(match.group(1))[0]
        assert entry["name"] == "score_baselibs"
        assert entry["group"] == "target_sw"
        assert entry["repo"] == "https://github.com/eclipse-score/baselibs.git"
        assert entry["owner_repo"] == "eclipse-score/baselibs"
        assert entry["hash"] == "abc123def456abc123def456abc123def456abc123"
        assert entry["branch"] == "main"
        assert entry["version"] is None


# ---------------------------------------------------------------------------
# generate_report – GitHub API integration in HTML
# ---------------------------------------------------------------------------


class TestGenerateReportGitHubIntegration:
    def test_github_api_url_pattern_present(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "api.github.com" in html

    def test_compare_endpoint_referenced(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "/compare/" in html

    def test_commits_endpoint_referenced(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "/commits/" in html

    def test_ahead_by_field_referenced(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "ahead_by" in html

    def test_token_stored_in_localstorage(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "gh_token" in html
        assert "localStorage" in html

    def test_cache_ttl_present(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "CACHE_TTL_MS" in html

    def test_cache_functions_present(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "loadFromCache" in html
        assert "saveToCache" in html

    def test_no_unauthenticated_api_calls(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        # Token is always attached — no conditional empty headers
        assert "headers: {}" not in html
        assert "authHeaders()" in html

    def test_no_token_shows_requires_pat(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "requires PAT" in html

    def test_token_input_always_present(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "gh-token" in html

    def test_no_cooldown_logic(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "remainingCooldownMs" not in html
        assert "startCooldownUI" not in html

    def test_no_oauth_code(self, minimal_known_good):
        html = generate_report(minimal_known_good, TEMPLATE_DIR)
        assert "CLIENT_ID" not in html
        assert "startOAuth" not in html
        assert "sha256base64url" not in html
        assert "pkce_state" not in html


# ---------------------------------------------------------------------------
# generate_report – multi-group
# ---------------------------------------------------------------------------


class TestGenerateReportMultiGroup:
    def test_all_modules_in_json(self, multi_group_known_good):
        html = generate_report(multi_group_known_good, TEMPLATE_DIR)
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        data = json.loads(match.group(1))
        names = {e["name"] for e in data}
        assert "score_baselibs" in names
        assert "score_crates" in names

    def test_both_groups_present(self, multi_group_known_good):
        html = generate_report(multi_group_known_good, TEMPLATE_DIR)
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        data = json.loads(match.group(1))
        groups = {e["group"] for e in data}
        assert groups == {"target_sw", "tooling"}

    def test_filter_buttons_in_html(self, multi_group_known_good):
        html = generate_report(multi_group_known_good, TEMPLATE_DIR)
        assert "target_sw" in html
        assert "tooling" in html


# ---------------------------------------------------------------------------
# generate_report – edge cases
# ---------------------------------------------------------------------------


class TestGenerateReportEdgeCases:
    def test_module_with_no_metadata(self):
        module = Module.from_dict(
            "score_crates",
            {
                "repo": "https://github.com/eclipse-score/score-crates.git",
                "hash": "deadbeef",
            },
        )
        kg = KnownGood(modules={"tooling": {"score_crates": module}}, timestamp="")
        html = generate_report(kg, TEMPLATE_DIR)
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        entry = json.loads(match.group(1))[0]
        assert entry["owner_repo"] == "eclipse-score/score-crates"

    def test_non_github_repo_owner_repo_is_none(self):
        module = Module.from_dict(
            "custom_mod",
            {
                "repo": "https://gitlab.com/some/repo.git",
                "hash": "abc",
            },
        )
        kg = KnownGood(modules={"g": {"custom_mod": module}}, timestamp="")
        html = generate_report(kg, TEMPLATE_DIR)
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        entry = json.loads(match.group(1))[0]
        assert entry["owner_repo"] is None

    def test_empty_modules(self):
        kg = KnownGood(modules={}, timestamp="2026-01-01")
        html = generate_report(kg, TEMPLATE_DIR)
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        assert json.loads(match.group(1)) == []


# ---------------------------------------------------------------------------
# write_report
# ---------------------------------------------------------------------------


class TestWriteReport:
    def test_creates_file(self, tmp_path, minimal_known_good):
        out = tmp_path / "report.html"
        write_report(minimal_known_good, out, TEMPLATE_DIR)
        assert out.exists()

    def test_file_content_matches_generate(self, tmp_path, minimal_known_good):
        out = tmp_path / "report.html"
        write_report(minimal_known_good, out, TEMPLATE_DIR)
        assert out.read_text(encoding="utf-8") == generate_report(minimal_known_good, TEMPLATE_DIR)

    def test_creates_parent_dirs_via_path(self, tmp_path, minimal_known_good):
        out = tmp_path / "sub" / "report.html"
        out.parent.mkdir(parents=True)
        write_report(minimal_known_good, out, TEMPLATE_DIR)
        assert out.exists()


# ---------------------------------------------------------------------------
# Integration: real known_good.json
# ---------------------------------------------------------------------------


class TestReportFromRealFile:
    def test_generates_without_error(self, real_known_good):
        html = generate_report(real_known_good, TEMPLATE_DIR)
        assert len(html) > 1000

    def test_all_modules_embedded(self, real_known_good):
        html = generate_report(real_known_good, TEMPLATE_DIR)
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        data = json.loads(match.group(1))
        total = sum(len(g) for g in real_known_good.modules.values())
        assert len(data) == total

    def test_all_entries_have_required_fields(self, real_known_good):
        html = generate_report(real_known_good, TEMPLATE_DIR)
        match = re.search(r"const MODULES\s*=\s*(\[.*?\]);", html, re.DOTALL)
        for entry in json.loads(match.group(1)):
            assert "name" in entry
            assert "group" in entry
            assert "repo" in entry
            assert "hash" in entry
            assert "branch" in entry
            assert "owner_repo" in entry
