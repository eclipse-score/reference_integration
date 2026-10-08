# Lifecycle Health Monitor SRAC pilot

This second real-component pilot applies an SRAC sidecar to the Health Monitor at the Lifecycle revision pinned by
`known_good.json`. The pinned public documents label the component, architecture, requirements and FMEA as `ASIL_B`, so the
sidecar transcribes `safety-related` / `ASIL-B`. The assertion remains `draft` with no reviewer: SRAC transports the source
metadata but does not turn draft work products into an approved safety decision.

The evidence also exposes useful readiness information. At this revision, the component, requirements, architecture and FMEA
documents are marked `draft`; the requirements document contains dummy placeholder requirements; and the architecture notes
an unresolved requirements-linkage TODO. A qualified Lifecycle safety reviewer must assess these gaps before approving the
assertion.

## Check behavior against the current product SBOM

The official SPDX 2.3 input used by the Persistency pilot does not contain a `score_lifecycle` package. Apply the Health Monitor
sidecar to that same immutable SBOM:

```bash
python -m srac.tools.enrich_sbom \
  --assertion srac/examples/lifecycle-health-monitor.srac.json \
  --sbom srac/pilot/persistency-kvs/input/reference-integration.spdx.json \
  --known-good known_good.json \
  --output srac/pilot/lifecycle-health-monitor/output/current-product.srac-report.json \
  --checksum-output srac/pilot/lifecycle-health-monitor/output/current-product.srac-report.sha256
```

Expected result:

```text
process exit: 1
matchStatus: unmatched
matchedComponents: []
safety relevance: safety-related (copied from assertion)
classification: ASIL-B (copied from assertion)
assertion status: draft (copied from assertion)
reviewer: null (copied from assertion)
```

This is the intended fail-closed behavior: safety metadata is never attached to a similarly named or absent SBOM component.
The checked-in report records this result and retains SHA-256 digests of all three inputs.

## Obtain a matched result

Generate an SPDX SBOM from `sbom-tool` with either of the public Health Monitor targets in its target closure:

```text
@score_lifecycle//score/health_monitor:health_monitoring_cc
@score_lifecycle//score/health_monitor:health_monitoring_rust
```

When the SBOM contains `score_lifecycle`, the join additionally verifies that `known_good.json` resolves the module repository
and exact commit `85da2168328d17a3cf53791ebf93534e5ed921fc`. The expected binding strategy is `score-known-good`. A generated
Lifecycle-containing SBOM should replace, not be simulated inside, the pilot before claiming a successful real match.
