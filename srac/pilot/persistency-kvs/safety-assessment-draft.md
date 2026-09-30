# Persistency KVS component-classification evidence draft

This document prepares evidence for the S-CORE `Create Component Classification` workflow. It is not a component
classification, safety assessment or approval. A Persistency component expert/committer must determine the results, and an
appointed S-CORE Safety Manager must approve the classification.

## Assessment baseline

- Component: Persistency Key-Value Storage (`score/kvs`)
- Repository: https://github.com/eclipse-score/persistency
- Revision: `9ae529ba9f413976ff5c9948c6490afa51bbfdc3`
- SRAC assertion: `srac-score-persistency-kvs-9ae529ba-draft-001`
- Intended decision: S-CORE component-classification outcome `Q`, `QR` or `NQ`
- Current SRAC state: relevance `undetermined`, classification `not-assigned`, status `draft`, reviewer unassigned

All evidence links below are pinned to the assessed revision.

## Step 1 — process evidence (P)

| ID | Indicator | Located evidence | HE/PE/NE | Component-expert rationale |
|---|---|---|---|---|
| P1 | State-of-the-art design, implementation and verification process | [KVS documentation](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs), [module safety planning](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/docs/features/persistency/safety_planning) | Pending | Pending component expert |
| P2 | Requirements available | [KVS requirements](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/requirements), [requirements inspection checklist](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/requirements/chklst_req_inspection.rst) | Pending | Pending component expert |
| P3 | Functional and architectural specification available | [component architecture](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/architecture), [architecture inspection checklist](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/architecture/chklst_arc_inspection.rst) | Pending | Pending component expert |
| P4 | Design specification available | [KVS detailed design](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/detailed_design), [implementation inspection checklist](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/detailed_design/chklst_impl_inspection.rst) | Pending | Pending component expert |
| P5 | Configuration specification and data available where applicable | [KVS Bazel definition](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/BUILD), [integration-test configuration](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/tests/test_cases/config) | Pending | Applicability and completeness pending component expert |
| P6 | Verification measures, tests and reports available | [C++ tests](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/tests), [Rust tests](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/rust_kvs/tests), [successful pinned coverage run](https://github.com/eclipse-score/persistency/actions/runs/32867923248) | Pending | Effective coverage: 87.89% lines (3934/4476), 93.51% branches (404/432); configured threshold is currently 0% |

Proposed `P` result: **Pending component expert**.

## Step 2 — complexity evidence (C)

KVS contains C++ and Rust implementations. The responsible expert and Safety Manager must confirm whether they require separate
complexity determinations or one conservative combined outcome. The current S-CORE template states that the C++ measure table is
still to be defined.

| Measure | C++ evidence/value | Rust evidence/value | NH/HM/NM | Owner |
|---|---|---|---|---|
| Non-comment source lines | 964 production lines across 10 files | 3,078 library lines across 11 files | Pending | Measured with pygount 3.2.0; component expert to confirm scope |
| Unsafe Rust with and without safety notes | Not applicable | 0 `unsafe` keyword occurrences across all 29 Rust files under `score/kvs` | Pending | Textual scan with ripgrep 15.2.0; not a memory-safety proof |
| Function and line coverage | Combined workflow result: 92.31% functions; 87.89% effective lines | Combined workflow result: 92.31% functions; 87.89% effective lines | Pending | Workflow reports a combined C++/Rust/tool scope; per-language values are not established |
| Public function interfaces | 46 callables in public root headers | 46 exported functions/public-trait methods | Pending | Component expert to confirm inclusions and exclusions |
| Function parameters | 42 total; maximum 4; mean 0.91 | 77 total including receivers; maximum 3; mean 1.67 | Pending | Parsed with tree-sitter; component expert to confirm metric interpretation |

Proposed `C` result: **Pending component expert**.

The raw measurements and their scopes are recorded in `evidence-metrics.json`. A component expert must confirm which source and
interface boundaries apply to the official complexity determination before assigning `NH`, `HM` or `NM`.

## Requirements-to-test traceability snapshot

At the pinned revision, the requirements document defines 35 `comp_req__kvs__*` component requirements. The Python component
integration-test metadata directly references 15 distinct component requirements through `fully_verifies` or
`partially_verifies`; 20 requirements have no direct reference in that metadata. This is a source-level trace scan, not a claim
that those 20 requirements are completely unverified: inspections, unit tests or other verification mechanisms may apply.

The 21 trace-decorated Python test classes exercise both the C++ and Rust scenarios. The source tree also contains 94 C++
GoogleTest macro occurrences, 248 Rust test-attribute occurrences and 44 Python test functions. These are inventory counts, not
independent test-result counts.

The complete 35-row result, including every full and partial test-class reference, is recorded in
`requirements-traceability.md`. Four requirements have at least one full-verification trace, 11 additional requirements have only
partial traces, and 20 have no direct integration-test metadata trace.

The existing [requirements inspection record](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/requirements/chklst_req_inspection.rst#L105)
states that the inspection stopped because the requirement set needed rework. That open finding must be resolved or dispositioned
before the requirements evidence can support an approved classification.

## Step 3 — classification outcome

| Item | Status |
|---|---|
| `P` | Pending |
| `C` | Pending |
| `CLAS_OUT` (`Q`, `QR` or `NQ`) | Pending |
| Component expert/committer | Unassigned |
| Safety Manager approver | Unassigned |
| Formal review record | Not started |

No SRAC field may be changed from `undetermined` or `not-assigned`, and no assertion may move beyond `draft`, until the official
classification and approval are linked as evidence.

## Additional safety evidence already located

- [KVS assumptions-of-use requirements](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/safety_analysis/aou_requirements.rst)
- [KVS FMEA](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/safety_analysis/fmea.rst)
- [KVS DFA](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/safety_analysis/dfa.rst)
- [Persistency safety manual](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/docs/module/manuals/safety_manual.rst)
- [Module safety plan](https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/docs/module/safety_mgt/module_safety_plan.rst)

## Evidence gaps to close

1. Confirm the assessment scope and intended safety context.
2. Name the responsible Persistency component expert/committer and Safety Manager.
3. Resolve or disposition the recorded requirements-inspection findings and review the 20 direct trace gaps.
4. Confirm the measured source and interface scopes and decide how constructors, receivers and trait methods affect `C`.
5. Decide the required coverage threshold and whether combined coverage is sufficient or per-language evidence is required.
6. Determine `P`, `C` and `CLAS_OUT` with rationale.
7. Record Safety Manager approval and the formal review artifact.
8. Update and regenerate the SRAC assertion and report only after approval.
