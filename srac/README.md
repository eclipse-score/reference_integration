# SRAC canonical projection and Sphinx-Needs adapter

This directory contains the first production-oriented slice of the Safety Relevance Assertion Capability (SRAC) work.

The implementation reads selected records from an authoritative Sphinx-Needs `needs.json` file and produces a deterministic, validated portability artifact. It does not create, infer, review or approve a safety decision. The lifecycle source remains authoritative.

This draft implementation is intentionally limited to:

- the canonical SRAC projection and validation contract;
- a read-only Sphinx-Needs adapter;
- deterministic example output and an integrity-bound SBOM reference manifest; and
- focused positive and fail-closed tests.

The Eclipse S-CORE proof-of-concept pilots, receiver integrations, signatures and attestations are outside this change. Production adoption is subject to the architecture decision proposed in [eclipse-score/score#3318](https://github.com/eclipse-score/score/pull/3318).

## Run the tests

```bash
bazel test //srac:srac_projection_tests
```

## Generate the example

```bash
bazel run //srac:export_needs -- \
  --needs srac/examples/needs/communication.needs.json \
  --config srac/examples/needs/communication.export.json \
  --output /tmp/communication.srac.json \
  --reference-output /tmp/communication.sbom-reference.json
```

See [NEEDS_EXPORT.md](NEEDS_EXPORT.md) for the mapping boundary and supported S-CORE vocabulary.
