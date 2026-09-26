# SRAC sidecar proof of concept

This directory contains an experimental Safety Relevance Assertion Capability (SRAC) profile for evaluation in the S-CORE
reference integration. It is not an approved S-CORE specification, does not assign a safety classification, and does not replace
the safety case or existing lifecycle work products.

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
- `examples/synthetic-safety-related.srac.json`: wholly synthetic, illustrative example showing a populated
  `safety-related` / `ASIL-B` / `reviewed` assertion flow. It is not a claim about any real component or product.
- `tools/profile.py`: self-contained core validation and PURL/version matching.
- `tools/enrich_sbom.py`: CLI that emits a separate enrichment report without changing the source SBOM.
- `mappings/`: proposed SPDX 2.3 and CycloneDX 1.6 carrier mappings.
- `pilot/persistency-kvs/`: real official SBOM input, provenance, reproducible commands, enrichment output and an
  unapproved component-classification evidence draft.
- `tests/`: validation and matching tests.

## Run the tests

```bash
bazel test //srac:tests
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

## Deliberate limitations

- The PoC does not modify `sbom-tool` or the generated SPDX/CycloneDX document.
- The join is module-level. `subject.componentPath` preserves the intended KVS scope until target-level identities are available.
- A module emitted with version `unknown` is never matched by name alone; its repository and commit must resolve exactly through
  `known_good.json`.
- `tools/profile.py` enforces the schema's core constraints without adding a runtime dependency. A production integration should
  use a complete JSON Schema Draft 2020-12 validator.
- No safety relevance or classification becomes authoritative without review through the existing S-CORE process.

## Proposed follow-up

After the profile and join are reviewed, the smallest possible `sbom-tool` change can add a stable, integrity-protected external
reference to the sidecar. Any process or cross-repository architecture change remains subject to the FEP and design-record decision.
