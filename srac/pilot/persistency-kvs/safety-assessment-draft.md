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
| P6 | Verification measures, tests and reports available | [C++ tests](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/tests), [Rust tests](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/rust_kvs/tests), [coverage configuration](https://github.com/eclipse-score/persistency/tree/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/quality/coverage) | Pending | Test results and coverage values must be attached |

Proposed `P` result: **Pending component expert**.

## Step 2 — complexity evidence (C)

KVS contains C++ and Rust implementations. The responsible expert and Safety Manager must confirm whether they require separate
complexity determinations or one conservative combined outcome. The current S-CORE template states that the C++ measure table is
still to be defined.

| Measure | C++ evidence/value | Rust evidence/value | NH/HM/NM | Owner |
|---|---|---|---|---|
| Non-comment source lines | Measurement pending | Measurement pending | Pending | Component expert |
| Unsafe Rust with and without safety notes | Not applicable | Measurement and review pending | Pending | Component expert |
| Function and line coverage | Report attachment pending | Report attachment pending | Pending | Verification owner |
| Public function interfaces | Measurement pending | Measurement pending | Pending | Component expert |
| Function parameters | Measurement pending | Measurement pending | Pending | Component expert |

Proposed `C` result: **Pending component expert**.

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
3. Attach revision-specific test and coverage results for both implementations.
4. Measure the complexity indicators and review unsafe Rust safety notes.
5. Determine `P`, `C` and `CLAS_OUT` with rationale.
6. Record Safety Manager approval and the formal review artifact.
7. Update and regenerate the SRAC assertion and report only after approval.
