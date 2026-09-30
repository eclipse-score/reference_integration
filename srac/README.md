# SRAC sidecar proof of concept

This directory contains an experimental Safety Relevance Assertion Capability (SRAC) profile for evaluation in the S-CORE
reference integration. It is not an approved S-CORE specification, does not assign a safety classification, and does not replace
the safety case or existing lifecycle work products.

For S-CORE, the authoritative safety model is Sphinx-needs and its generated `needs.json`. The PoC includes a read-only exporter
that projects selected source records into portable safety metadata; it does not introduce a second authoring workflow. See
[`NEEDS_EXPORT.md`](NEEDS_EXPORT.md) for the flow, generated example and identified SPDX Functional Safety mapping gaps.

The `0.2-draft` profile also carries an optional system-impact workflow. It records the trigger, analysis status and scope,
impact outcome, per-element decisions, requirement verification and publication bundle. The enrichment tool copies that workflow
without calculating, approving or changing any decision.

## Goal

The pilot tests whether a small, versioned assertion can be matched deterministically to a component in an SPDX or CycloneDX
SBOM while the authoritative requirements, analyses, reviews and verification evidence remain in their existing systems.

The first example targets the KVS path in the pinned `score_persistency` revision from `known_good.json`. Its safety relevance is
deliberately `undetermined`, its classification is `not-assigned`, and its assertion state is `draft` until the responsible S-CORE
component owner and safety reviewer provide a decision.

## Contents

- `schema/srac.schema.json`: draft JSON Schema for the minimum profile.
- `schema/srac-report.schema.json`: draft JSON Schema for the generated enrichment report.
- `examples/persistency-kvs.srac.json`: non-authoritative KVS example.
- `examples/lifecycle-health-monitor.srac.json`: draft transcription of the pinned Health Monitor's public ASIL-B metadata.
- `examples/synthetic-safety-related.srac.json`: wholly synthetic, illustrative example showing a populated
  `safety-related` / `ASIL-B` / `reviewed` assertion and all seven impact-analysis workflow steps. It is not a claim about any
  real component or product.
- `tools/profile.py`: self-contained core validation and PURL/version matching.
- `tools/enrich_sbom.py`: CLI that emits a separate enrichment report without changing the source SBOM.
- `tools/export_needs.py`: deterministic `needs.json` exporter that preserves source provenance and never makes a safety decision.
- `tools/receive_srac.py`: receiving-side discovery, SHA-256 verification, assertion validation and SBOM correlation.
- `examples/needs/` and `examples/generated/`: reduced Sphinx-needs input, transport-only configuration, generated projection and
  illustrative SPDX/CycloneDX carrier SBOMs and reference fragments.
- `TESTING.md`: consolidated independent test procedure, expected results and reporting template.
- `mappings/`: proposed SPDX 2.3 and CycloneDX 1.6 carrier mappings.
- `pilot/persistency-kvs/`: real official SBOM input, provenance, reproducible commands, enrichment output and an
  unapproved component-classification evidence draft.
- `pilot/lifecycle-health-monitor/`: second real-component pilot demonstrating fail-closed behavior because the current
  official product SBOM does not contain Lifecycle, plus the evidence gaps that must be resolved before approval.
- `tests/`: validation and matching tests.

## Run the tests

See [`TESTING.md`](TESTING.md) for the complete independent test procedure, manual positive and negative scenarios, integrity
checks and the test-report template.

```bash
bazel test //srac:srac_tests
```

## Match the example to an SBOM

Build the repository SBOM and run the enrichment tool:

```bash
bazel build //:product_sbom
bazel run //srac:enrich_sbom -- \
  --assertion srac/examples/persistency-kvs.srac.json \
  --sbom bazel-bin/product_sbom.spdx.json \
  --known-good known_good.json \
  --output /tmp/persistency-kvs.srac-report.json \
  --checksum-output /tmp/persistency-kvs.srac-report.sha256
```

The command returns `0` when at least one component matches and `1` when the assertion remains unmatched. An unmatched result is
expected unless the assertion PURL/version matches directly or `known_good.json` securely resolves an `unknown` S-CORE module
identity. See `pilot/persistency-kvs/README.md` for the completed end-to-end example.

The report copies the safety relevance, classification, assertion status and reviewer from the assertion. It does not calculate,
approve or strengthen those values. SHA-256 digests bind the report to the exact assertion, SBOM and known-good inputs; a separate
checksum file protects the serialized report itself.

The `needs.json` example also demonstrates the complete transport boundary. The generated SRAC sidecar is referenced from
synthetic SPDX 2.3 and CycloneDX 1.6 carrier SBOMs. `receive_srac` discovers exactly one reference, requires its SHA-256,
verifies the local artifact before parsing, validates the assertion and then performs component correlation. Missing, ambiguous
or digest-mismatched references fail closed. Network retrieval is deliberately outside this PoC.

When present, `impactAnalysis` is also copied verbatim for both matched and unmatched reports. This preserves the distinction
between component matching and an engineering decision: the tool can bind records, but it never supplies the trigger conclusion,
impact level, decision authority, verification result or completion status.

All identifiers used by impact scope, decisions, verification and publication roots must resolve within the assertion to a
requirement, evidence item, impact analysis, decision or requirement verification. IDs share one namespace and duplicate IDs are
invalid.

`safetyRelevance` describes **functional-safety relevance only**. Security relevance is an independent dimension represented by
`impactAnalysis.impactLevel` values such as `securityImpact` or `safetyAndSecurityImpact` and by the existing SBOM/VEX security
model. A value such as `security-related` is therefore invalid in `safetyRelevance.status`.

The generic sidecar schema retains the portable SPDX/ISO 26262 vocabulary, including ASIL-A through ASIL-D, while the S-CORE
`needs.json` exporter implements the narrower S-CORE source profile: `QM`, `ASIL_B` and `ASIL_D` only. Missing source
classification fails closed to `undetermined` / `not-assigned`; an explicitly unsupported ASIL, SIL, DAL or security value is
rejected. The exporter never emits SIL or DAL.

`safetyRelevance.classification` uses the human-facing spelling (`ASIL-B`), while
`impactAnalysis.safetyIntegrityLevel` uses SPDX `SafetyIntegrityLevelType` spelling (`asilB`). The portable validator enforces
their exact mapping when the latter is present; neither field can silently override the other.

## Deliberate limitations

- The PoC does not modify `sbom-tool` or the generated SPDX/CycloneDX document.
- The join is module-level. `subject.componentPath` preserves the intended KVS scope until target-level identities are available.
- A module emitted with version `unknown` is never matched by name alone; its repository and commit must resolve exactly through
  `known_good.json`.
- `tools/profile.py` enforces the schema's core constraints without adding a runtime dependency. A production integration should
  use a complete JSON Schema Draft 2020-12 validator.
- No safety relevance or classification becomes authoritative without review through the existing S-CORE process.
- The KVS example intentionally has no `impactAnalysis` entry yet. Its current known-good pin is a baseline, not evidence that a
  pin bump occurred. A real configuration-change trigger should be added when such a bump is proposed and linked to its actual PR.

## Proposed follow-up

After the profile and join are reviewed, the smallest possible `sbom-tool` change can add a stable, integrity-protected external
reference to the sidecar. Any process or cross-repository architecture change remains subject to the FEP and design-record decision.
