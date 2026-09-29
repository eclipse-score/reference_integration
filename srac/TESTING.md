# Testing the SRAC sidecar proof of concept

This guide provides a single reproducible procedure for independently testing the experimental SRAC sidecar in the S-CORE
reference integration. The tests demonstrate assertion validation, deterministic SBOM correlation, integrity protection and
fail-closed behavior. They do not approve a safety classification or replace an S-CORE safety review.

## Test environment

Use a clean Linux or WSL2 checkout. Record the operating system, commit and Bazel version in the test report.

Required:

- Git
- Bazelisk or Bazel 8.6.0, as selected by the repository `.bazelversion`
- `jq` and `sha256sum` for the manual checks

Node.js, npm and `@cyclonedx/cdxgen` are required only for the optional fresh-SBOM test.

## Check out the change

Using the GitHub CLI:

```bash
gh repo clone eclipse-score/reference_integration
cd reference_integration
gh pr checkout 370
git status --short
git rev-parse HEAD
bazel --version
```

The working tree should be clean before testing.

## 1. Run the automated test suite

```bash
bazel test //srac:srac_tests --test_output=errors
```

All tests must pass. The suite covers:

- assertion and enrichment-report validation;
- SPDX and CycloneDX component matching;
- incorrect-version and missing-component rejection;
- known-good repository and commit resolution;
- impact-analysis vocabulary validation;
- referential integrity and duplicate identifier rejection;
- classification and SPDX safety-integrity-level consistency;
- deterministic `needs.json` projection, source provenance, fail-closed safety mapping and carrier-reference integrity;
- checked-in pilot output, checksum and provenance integrity; and
- KVS matched and Lifecycle Health Monitor fail-closed behavior.

### Generate the Sphinx-needs projection

```bash
mkdir -p /tmp/srac-manual

bazel run //srac:export_needs -- \
  --needs srac/examples/needs/communication.needs.json \
  --config srac/examples/needs/communication.export.json \
  --output /tmp/srac-manual/communication.srac.json \
  --reference-output /tmp/srac-manual/communication.sbom-reference.json

diff -u srac/examples/generated/communication.srac.json \
  /tmp/srac-manual/communication.srac.json
diff -u srac/examples/generated/communication.sbom-reference.json \
  /tmp/srac-manual/communication.sbom-reference.json
```

Both comparisons must be empty. Confirm that the safety classification, source lifecycle status, Feature, Component and
Assumption of Use trace back to the selected Sphinx-needs records. The export configuration must contain no safety decision.

## 2. Run the matched Persistency KVS pilot

Create a temporary output directory, then apply the KVS assertion to the checked-in official SPDX input:

```bash
mkdir -p /tmp/srac-manual

bazel run //srac:enrich_sbom -- \
  --assertion srac/examples/persistency-kvs.srac.json \
  --sbom srac/pilot/persistency-kvs/input/reference-integration.spdx.json \
  --known-good known_good.json \
  --output /tmp/srac-manual/persistency-kvs.srac-report.json \
  --checksum-output /tmp/srac-manual/persistency-kvs.srac-report.sha256

echo "Exit code: $?"
```

Expected exit code: `0`.

Inspect the result:

```bash
jq '{
  matchStatus,
  matchedComponents,
  bindingEvidence,
  safetyAssessment,
  integrity
}' /tmp/srac-manual/persistency-kvs.srac-report.json
```

Expected values:

| Field | Expected value |
|---|---|
| `matchStatus` | `matched` |
| matched identifier | `SPDXRef-score-persistency-unknown` |
| binding strategy | `score-known-good` |
| known-good module | `score_persistency` |
| known-good commit | `9ae529ba9f413976ff5c9948c6490afa51bbfdc3` |
| safety relevance | `undetermined` |
| classification | `not-assigned` |
| assertion status | `draft` |
| reviewer | `null` |

The last four values must be copied unchanged from the assertion. The tool must not infer or strengthen them.

## 3. Verify output integrity and reproducibility

```bash
(
  cd /tmp/srac-manual
  sha256sum -c persistency-kvs.srac-report.sha256
)

cmp \
  /tmp/srac-manual/persistency-kvs.srac-report.json \
  srac/pilot/persistency-kvs/output/persistency-kvs.srac-report.json

sha256sum srac/pilot/persistency-kvs/input/reference-integration.spdx.json
```

Expected results:

- `sha256sum` prints `persistency-kvs.srac-report.json: OK`;
- `cmp` produces no output; and
- the input SBOM digest is `e147f5db23d35c97c8c779c217d6edb9977d01cddf7683e2c46d45cf09737243`.

These checks demonstrate that the generated report is reproducible and the source SBOM remains unchanged.

## 4. Verify fail-closed behavior without known-good evidence

Run the same assertion without `known_good.json`:

```bash
bazel run //srac:enrich_sbom -- \
  --assertion srac/examples/persistency-kvs.srac.json \
  --sbom srac/pilot/persistency-kvs/input/reference-integration.spdx.json \
  --output /tmp/srac-manual/kvs-without-known-good.json

echo "Exit code: $?"

jq '{matchStatus, matchedComponents}' \
  /tmp/srac-manual/kvs-without-known-good.json
```

Expected results:

- process exit code: `1`;
- `matchStatus`: `unmatched`; and
- `matchedComponents`: `[]`.

This is an expected successful negative test. A component whose SBOM version is `unknown` must not match by name alone.

## 5. Verify the Lifecycle Health Monitor fail-closed pilot

The checked-in product SBOM does not contain `score_lifecycle`. Apply the Health Monitor assertion to the same SBOM:

```bash
bazel run //srac:enrich_sbom -- \
  --assertion srac/examples/lifecycle-health-monitor.srac.json \
  --sbom srac/pilot/persistency-kvs/input/reference-integration.spdx.json \
  --known-good known_good.json \
  --output /tmp/srac-manual/health-monitor.srac-report.json \
  --checksum-output /tmp/srac-manual/health-monitor.srac-report.sha256

echo "Exit code: $?"

jq '{
  matchStatus,
  matchedComponents,
  safetyAssessment
}' /tmp/srac-manual/health-monitor.srac-report.json
```

Expected results:

- process exit code: `1`;
- `matchStatus`: `unmatched`;
- `matchedComponents`: `[]`;
- safety relevance: `safety-related`;
- classification: `ASIL-B`;
- assertion status: `draft`; and
- reviewer: `null`.

This is an expected successful negative test. The report preserves the externally authored record but does not bind it to an
absent or similarly named SBOM component.

## 6. Optional: generate a fresh product SBOM

Install the CycloneDX generator, then build the current product SBOM:

```bash
npm install -g @cyclonedx/cdxgen

bazel build \
  --lockfile_mode=error \
  --config=linux-x86_64 \
  //:product_sbom
```

Expected outputs:

```text
bazel-bin/product_sbom.spdx.json
bazel-bin/product_sbom.cdx.json
```

Apply the KVS assertion to the newly generated SPDX document:

```bash
bazel run //srac:enrich_sbom -- \
  --assertion srac/examples/persistency-kvs.srac.json \
  --sbom bazel-bin/product_sbom.spdx.json \
  --known-good known_good.json \
  --output /tmp/srac-manual/generated-kvs-report.json \
  --checksum-output /tmp/srac-manual/generated-kvs-report.sha256
```

The regenerated SBOM can have a different byte digest because generation timestamps are expected to change. Its component graph
and KVS correlation should remain equivalent.

## Report the result

Include the following information in an independent test report:

```text
Tester:
Date:
Operating system:
Commit tested:
Bazel version:

Automated suite: PASS / FAIL
KVS matched pilot: PASS / FAIL
KVS missing-known-good negative test: PASS / FAIL
Health Monitor absent-component negative test: PASS / FAIL
Sphinx-needs projection and reference comparison: PASS / FAIL
Checksum verification: PASS / FAIL
Fresh SBOM test, if performed: PASS / FAIL / NOT RUN

Unexpected behavior:
Documentation issues:
Attached logs and generated reports:
```

Do not report an `unmatched` negative scenario as a defect when it returns the documented exit code and empty match set. Report
any incorrect match, unexpected safety-state change, digest mismatch, validation bypass or source-SBOM modification as a defect.
