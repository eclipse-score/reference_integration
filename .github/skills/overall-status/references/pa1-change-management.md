# Process Area 1 — Change Management

| Property | Value |
|---|---|
| sphinx-needs tag | `change_management` |
| Cross-reference label | `overall_status_pa1` |
| Columns | CR approved |
| Progress figure | _none_ (PA1 is issue-based, not file-based) |

PA1 "CR approved" tracks **Feature Request** issues in `eclipse-score/score`
(not RST directives). There are therefore **no path filters** for this PA —
the data comes from the GitHub issues API and the org-level Project V2 board.

For shared conventions (cell layout, source links, rollout-status row, pie
chart row), see [common.md](./common.md#c4-rst-formatting-rules).

---

## PA1-only modules: Diagnostic Services and NM

Both modules have a row in **every** PA table for layout consistency, but only
the **PA1 column carries real data**: they are tracked via `feature_request`
issues in `eclipse-score/score` (see the keyword map below). They have **no own
repository** and **no `known_good.json` key** yet, so
[common.md C2](./common.md#c2-repos-and-pinned-refs) and the per-PA path-filter
tables have no rows for them and their PA2–PA5 cells render as `❌ Open` (zero
directives, zero files). They still contribute `0` to the per-PA progress charts
(see [common.md C6.2](./common.md#c62-metrics--what-each-chart-sums)) and are
excluded from the coverage weighted mean (see
[common.md C7](./common.md#c7-limitations)).

---

## Status criteria

| Deliverable | `✅ Available` | `🔄 …` | `❌ Open` |
|---|---|---|---|
| **PA1** CR approved | At least one matching `feature_request` issue **scoped to milestone v0.5 or v1.0** has Status `Accepted` (or `Done`) in Project V2 #4 "Feature Requests / Modification" (see below); cell lists every matching FR with its individual project status and milestone tag | At least one in-scope FR in `In Progress`/`In Review`/`Ready for Review`/`Changes Requested`/`Draft`/`POC Needed` and none Accepted | No matching FR in scope, or all matching FRs `Rejected` |

---

## Feature Request issue lookup

PA1 "CR approved" tracks **Feature Request** issues in `eclipse-score/score`.
The label name is **`feature_request`** (lowercase, with underscore). Use
`state=all` (some FRs are still open) and combine the topical
`ft:<module>` label with a title-keyword pass; **always union both result
sets** (deduplicated by issue number) so that older FRs which pre-date the
`ft:*` label scheme are still attributed to a module — see the attribution
note below.

**Milestone scope.** Only Feature Requests targeted at the **v0.5** or
**v1.0** release milestones are counted. The GitHub milestone titles that
currently qualify are:

- `SCORE v0.5 Feature Complete`
- `S-CORE v0.5 Certifiable`
- `v1.0`

The match is performed by substring on the milestone title with whitespace
stripped (`"0.5" in title` or `"1.0" in title`, case-insensitive). FRs with
no milestone, or with any other milestone (`v0.6`…`v0.10`), are excluded
from PA1 — even if they carry a matching `ft:*` label. Each rendered FR is
tagged with its short milestone in square brackets (e.g. `[v1.0]`,
`[v0.5 Certifiable]`).

The issues fetch must therefore include the milestone field in the jq
projection.

For each issue, fetch its **`Status`** field from the org-level project
**"Feature Requests / Modification"** (Project V2, id
`PVT_kwDOCy9hX84Auo7w`, number `#4`). The PA1 cell renders **one entry per
Feature Request**, each annotated with its individual project status — not a
single aggregate "Available". The cell headline is the **best** status
across all FRs for that module (so a module with at least one Accepted FR
still shows ✅ in summaries).

```python
# 1. List feature requests via the issue label (incl. milestone).
#    `--paginate` must be a separate CLI flag — embedding it in the URL
#    string sends it as a query parameter and silently truncates results
#    at 100 issues.
def fetch_frs():
    out = subprocess.run(
        ["gh", "api", "--paginate",
         "repos/eclipse-score/score/issues?state=all"
         "&labels=feature_request&per_page=100",
         "--jq",
         '.[] | [(.number|tostring), .title,'
         ' ((.labels // []) | map(.name) | join(",")),'
         ' ((.milestone.title // ""))] | @tsv'],
        capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, f"gh api failed: {out.stderr}"
    return [tuple(line.split("\t")) for line in out.stdout.splitlines() if line]

def in_scope(milestone: str) -> bool:
    s = milestone.lower().replace(" ", "")
    return ("0.5" in s) or ("1.0" in s)

# 2. Pull Status per issue from Project V2 #4
PROJECT_FR_ID = "PVT_kwDOCy9hX84Auo7w"
def fetch_fr_project_status() -> dict[str, str]:
    q = ('query($endCursor:String){node(id:"' + PROJECT_FR_ID + '"){'
         '... on ProjectV2{items(first:100, after:$endCursor){'
         'pageInfo{hasNextPage endCursor} '
         'nodes{content{... on Issue{number repository{nameWithOwner}}} '
         'fieldValues(first:20){nodes{... on ProjectV2ItemFieldSingleSelectValue'
         '{name field{... on ProjectV2SingleSelectField{name}}}}}}}}}}')
    out = subprocess.run(
        ["gh","api","graphql","--paginate","-f", "query="+q,
         "--jq",
         '.data.node.items.nodes[] | '
         'select(.content.repository.nameWithOwner=="eclipse-score/score") | '
         '[(.content.number|tostring), '
         '((.fieldValues.nodes[]|select(.field.name=="Status")|.name) // "—")] | @tsv'],
        capture_output=True, text=True, timeout=120)
    return dict(line.split("\t",1) for line in out.stdout.splitlines() if "\t" in line)
```

Status-field options (from project schema) and the recommended emoji /
ranking the cell uses to pick the headline:

| Project Status      | Emoji | Rank |
|---------------------|:-----:|:----:|
| `Accepted` / `Done` | ✅    | 0    |
| `In Progress`       | 🔄    | 1    |
| `In Review`         | 🔄    | 1    |
| `Ready for Review`  | 🔄    | 1    |
| `Changes Requested` | 🔄    | 1    |
| `Draft`             | 📝    | 2    |
| `POC Needed`        | 🧪    | 3    |
| `Rejected`          | ❌    | 4    |
| _not in project_    | ❔    | 5    |

Cell layout (RST):

```rst
   - ✅ Accepted

     | `#914 <https://github.com/eclipse-score/score/issues/914>`__ — ✅ Accepted [v1.0] — Feature Request for SOME/IP Gateway
     | `#549 <https://github.com/eclipse-score/score/issues/549>`__ — ✅ Accepted [v0.5 Certifiable] — Feature request: common libraries for IPC and Logging
```

Each FR line is `\`#NNN <url>\`__ — <emoji> <Status> [<milestone>] — <issue title>`.
The issue title is taken verbatim from the GitHub `.title` field (already
fetched by `fetch_frs()`).

Module attribution mapping. **Always** combine the label-based hits and
the title-keyword hits (deduplicated by issue number) — do **not** treat
the keyword set as a fallback that only fires when the `ft:*` query is
empty. Older feature requests pre-date the `ft:*` label scheme and only
match by title keyword (e.g. `#69 "Feature Request for IPC"` for
Communication carries `feature_request` + `community:architecture` +
`planned-for:0.5` but no `ft:communication`); skipping the keyword pass
when `ft:*` already produced hits causes such issues to silently disappear
from PA1.

```python
FT_LABEL = {
    "Baselibs":         "ft:baselibs",
    "Communication":    "ft:communication",
    "Logging":          "ft:logging",
    "Persistency":      "ft:persistency",
    "Config Mgmt":      "ft:config_management",
    "Lifecycle":        "ft:health&lifecycle",
    "Security/Crypto":  "ft:security&crypto",
}
KW_FALLBACK = {
    "Baselibs":  ["baselib", "common librar", "abi compatible", "json parser"],
    "Communication": ["ipc", "streaming", "record and replay"],
    "Logging":   ["logging"],
    "Persistency": ["persistency", " kvs"],
    # Leading space is intentional: avoids matching "runtime", "realtime",
    # "datetime" etc. Do NOT "fix" by stripping it.
    "Time":      [" time"],
    "Some/IP":   ["some/ip", "someip", "some_ip"],
    "Diagnostic Services": ["diagnos"],
    "NM":        ["network management"],
}
```

Render up to ~6 hits per cell. If a module has zero matches, render
`❌ Open`. The older label `contribution request` exists too but tracks
formal contribution intent, not feature scope — **do not** use it for PA1.

> **Manual overrides — apply *after* the automated label∪keyword union
> has produced its hit set:**
>
> - **`#549` "common libraries for IPC and Logging"** is rendered **only
>   under Baselibs**, even though its title contains both "IPC" and
>   "Logging" (which would otherwise match Communication and Logging).
>   Drop `#549` from the Communication and Logging cells.
> - **`#757` "Feature request for qualified json-parser"** belongs to
>   **Baselibs** (label `ft:baselibs`). It has **no GitHub milestone**,
>   so the standard milestone filter (`"0.5"|"1.0" in title`) excludes
>   it; force-include it for Baselibs and render it without the `[…]`
>   milestone bracket.
> - **Communication scope is local IPC only.** Drop `#914` (SOME/IP
>   Gateway → Some/IP module) and `#917` (ABI compatible datatypes →
>   Baselibs) from the Communication cell, even though their title
>   keywords (`some/ip`, `abi compatible`) or labels could attribute
>   them. Communication renders only `#69 — Feature Request for IPC`.
