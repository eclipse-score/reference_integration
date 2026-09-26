# SPDX 2.3 mapping for the SRAC sidecar PoC

This mapping is experimental and does not modify the S-CORE safety process or claim native SRAC support in SPDX 2.3.

| SRAC concept | SPDX 2.3 representation in the pilot |
|---|---|
| Component identity | Package URL in `Package.externalRefs` |
| Component version | `Package.versionInfo` and the PURL version |
| SRAC sidecar location | Proposed `OTHER` external reference from the matched package |
| Sidecar integrity | SHA-256 recorded with the published sidecar artifact |
| Safety relevance, rationale and review state | Retained in the SRAC sidecar |
| Requirements and evidence | URI references retained in the SRAC sidecar |
| System impact workflow | Optional `impactAnalysis` retained in the SRAC sidecar |

The PoC first proves a deterministic join using the package PURL and version. It emits a separate enrichment report and does
not mutate the SPDX document. A later `sbom-tool` change may publish the external reference after the representation is reviewed.

## SPDX 3.1-dev semantic alignment

SPDX 2.3 cannot serialize the FunctionalSafety and Core model terms below. The sidecar therefore preserves their semantics while
S-CORE continues to emit SPDX 2.3. These mappings target the current names in the SPDX 3.1 development work; proposed terms remain
subject to upstream review.

| Workflow step | SRAC 0.2-draft | SPDX 3.1-dev representation |
|---|---|---|
| Receive trigger | `impactAnalysis[].trigger` | FunctionalSafety `AnalysisTrigger`, or an existing source artifact such as Security `Vulnerability`; `SystemImpactAnalysis hasInput` the trigger/source ([#1442](https://github.com/spdx/spdx-3-model/pull/1442), [#1453](https://github.com/spdx/spdx-3-model/pull/1453)) |
| Open analysis | `id`, `impactAnalysisStatus` | FunctionalSafety `SystemImpactAnalysis` and `SystemImpactAnalysisStatusType` ([#1442](https://github.com/spdx/spdx-3-model/pull/1442)) |
| Scope and safety context | `impactedElement`, `safetyIntegrityLevel` | `impactedElement`; FunctionalSafety `SafetyContextRelationship.safetyIntegrityLevel` and `SafetyIntegrityLevelType` ([#1436](https://github.com/spdx/spdx-3-model/pull/1436)) |
| Analyze and classify | `impactLevel`, `addedElement`, `modifiedElement`, `removedElement`, `rationale` | Corresponding `SystemImpactAnalysis` properties and `SystemImpactLevelType` ([#1442](https://github.com/spdx/spdx-3-model/pull/1442)) |
| Decide per element | `decisions[]`; `appliesTo` | Core `Decision`; `SystemImpactAnalysis hasOutput Decision`; each `Decision hasInput` the `appliesTo` elements; `originatedBy` identifies the agent ([#1458](https://github.com/spdx/spdx-3-model/pull/1458)) |
| Verify | `requirementVerification[]`; `verifies`; `evidence` | FunctionalSafety `RequirementVerification`; requirement `verifiedBy` verification; evaluation/evidence elements remain independently addressable |
| Close and publish | `impactAnalysisStatus: complete`; `bundle.rootElement` | Completed `SystemImpactAnalysis`; Core `Bundle.rootElement` identifies the published graph roots ([#1443](https://github.com/spdx/spdx-3-model/pull/1443)) |

`trigger.type` remains a compact sidecar label because SPDX `AnalysisTrigger` intentionally has no trigger-type vocabulary.
`decisions[].appliesTo` is the compact sidecar form of one or more Core `hasInput` relationships. The enrichment report copies the
entire block as-is and never infers a status, impact level, decision, reviewer or verification outcome.
