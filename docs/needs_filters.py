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

"""
Custom filter functions for use with sphinx-needs :filter-func: option.
"""


def std_req_status_for_area(needs, results, arg1=""):
    """
    filter_func for needpie: counts the tag-based compliance status distribution
    of std_req needs referenced via `complies` from gd_req needs tagged with the
    given process area tag.

    Recognized tags (in priority order): ok, recommendation, open, action,
    deviation, n/a. Needs with none of these tags are counted as "other".

    arg1 = process area tag (e.g. requirements_engineering)
    """
    area_tag = arg1.strip()
    std_req_ids = set()
    needs_by_id = {n["id"]: n for n in needs}
    for need in needs:
        if need.get("type") == "gd_req" and not need.get("is_external", False) and area_tag in need.get("tags", []):
            for ref_id in need.get("complies", []):
                if ref_id.startswith("std_req__iso26262__"):
                    std_req_ids.add(ref_id)
    ok = recommendation = open_ = action = deviation = na = other = 0
    for sid in std_req_ids:
        n = needs_by_id.get(sid)
        if n:
            t = set(n.get("tags", []))
            if "deviation" in t:
                deviation += 1
            elif "action" in t:
                action += 1
            elif "open" in t:
                open_ += 1
            elif "ok" in t:
                ok += 1
            elif "recommendation" in t:
                recommendation += 1
            elif "n/a" in t:
                na += 1
            else:
                other += 1
    results += [ok, recommendation, open_, action, deviation, na, other]


def wp_tag_status(needs, results, arg1=""):
    """
    filter_func for needpie: counts the tag-based verification status distribution
    of gd_req needs associated with one or more workflows (pipe-separated in arg1).

    Tags (in priority order):
    - done_automation → Automated
    - prio_<X>_automation → Waiting for automation
    - manual_prio_<X> → Inspection list
    - (none of the above) → Other

    arg1 = workflow id(s), pipe-separated (e.g. wf__foo or wf__foo|wf__bar)
    """
    workflow_ids = [w.strip() for w in arg1.split("|") if w.strip()]
    automated = waiting = inspection = other = 0
    for need in needs:
        if need.get("type") == "gd_req" and not need.get("is_external", False):
            satisfies = need.get("satisfies", [])
            if any(wf in satisfies for wf in workflow_ids):
                tags = set(need.get("tags", []))
                if "done_automation" in tags:
                    automated += 1
                elif any(t.startswith("prio_") and t.endswith("_automation") for t in tags):
                    waiting += 1
                elif any(t.startswith("manual_prio_") for t in tags):
                    inspection += 1
                else:
                    other += 1
    results += [automated, waiting, inspection, other]


def area_verification_status(needs, results, arg1=""):
    """
    filter_func for needpie: counts the tag-based verification status distribution
    of gd_req needs tagged with the given process area tag, aggregated across all
    workflows for that area.

    Tags (in priority order):
    - done_automation → Automated
    - prio_<X>_automation → Waiting for automation
    - manual_prio_<X> → Inspection list
    - (none of the above) → Other

    arg1 = process area tag (e.g. requirements_engineering)
    """
    area_tag = arg1.strip()
    automated = waiting = inspection = other = 0
    for need in needs:
        if need.get("type") == "gd_req" and not need.get("is_external", False) and area_tag in need.get("tags", []):
            tags = set(need.get("tags", []))
            if "done_automation" in tags:
                automated += 1
            elif any(t.startswith("prio_") and t.endswith("_automation") for t in tags):
                waiting += 1
            elif any(t.startswith("manual_prio_") for t in tags):
                inspection += 1
            else:
                other += 1
    results += [automated, waiting, inspection, other]


def wp_done_automation_status(needs, results, arg1=""):
    """
    filter_func for needpie: counts gd_req needs associated with one or more
    workflows and splits them into done_automation vs. remaining requirements.

    arg1 = workflow id(s), pipe-separated (e.g. wf__foo or wf__foo|wf__bar)
    """
    workflow_ids = [w.strip() for w in arg1.split("|") if w.strip()]
    done = rest = 0
    for need in needs:
        if need.get("type") == "gd_req" and not need.get("is_external", False):
            satisfies = need.get("satisfies", [])
            if any(wf in satisfies for wf in workflow_ids):
                tags = set(need.get("tags", []))
                if "done_automation" in tags:
                    done += 1
                else:
                    rest += 1
    results += [done, rest]
