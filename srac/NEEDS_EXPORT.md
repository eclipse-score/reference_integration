# Exporting S-CORE safety metadata from `needs.json`

This experiment treats the S-CORE Sphinx-needs model as the single source of truth. It does not ask a component team to copy its
safety classification, rationale, requirements, evidence or review state into a second hand-authored file.

```text
authoritative Sphinx-needs model
           needs.json
               |
               | read-only, deterministic projection
               v
 portable SRAC safety metadata
               |
               | SPDX/CycloneDX external reference
               v
      SPDX or CycloneDX SBOM
               |
               | discovery and SHA-256 verification
               v
          receiving tool
```

## What is authored and what is derived

`communication.export.json` contains only transport configuration: the root need ID, explicitly included need IDs, component
PURL/version/repository, publication URI and reproducible creation timestamp. It contains no safety classification or engineering
decision.

The exporter reads the following values from `needs.json`:

- `safety` and `safety_relevant` for the projected relevance and classification;
- `status` as source lifecycle provenance, without translating `valid` into an SRAC approval;
- `id`, `type`, `docname` and `external_url` for stable source references; and
- the Sphinx-needs version and exact input digest.

The generated assertion remains `draft` because the export itself has not received a separate approval. The source need and its
S-CORE review process remain authoritative. Missing or contradictory safety fields fail closed as `undetermined` or an error;
the exporter never infers safety relevance from a title, path or relationship.

The exporter accepts only the S-CORE source vocabulary `QM`, `ASIL_B` and `ASIL_D`. It does not emit ASIL-A, ASIL-C, SIL or DAL.
An absent classification is exported as `undetermined` / `not-assigned`; an explicitly unsupported value is rejected rather than
silently translated. Functional-safety relevance and security relevance remain separate: security belongs in the impact-analysis
or SBOM/VEX security model, not in `safetyRelevance`.

## Run the minimal example

The checked-in `communication.needs.json` is a reduced fixture taken from the public S-CORE `needs.json` shape. It includes a
Feature, Component and Assumption of Use so the mapping gap is visible without checking in the full generated site artifact.

```bash
bazel run //srac:export_needs -- \
  --needs srac/examples/needs/communication.needs.json \
  --config srac/examples/needs/communication.export.json \
  --output /tmp/communication.srac.json \
  --reference-output /tmp/communication.sbom-reference.json
```

The expected outputs are checked in under `examples/generated/`. The reference manifest shows the proposed SPDX 2.3 `OTHER`
external reference and CycloneDX 1.6 `other` external reference. The synthetic carrier SBOMs in that directory demonstrate the
same references in context. `receive_srac` discovers the reference, resolves a previously retrieved local artifact, verifies its
SHA-256 before parsing, validates the assertion and only then correlates it to the referenced component. It does not perform
network retrieval or modify an SBOM.

## Mapping and feedback for SPDX Functional Safety

| S-CORE source concept | Export behavior | Standards feedback |
|---|---|---|
| Feature (`feat`) | Preserved as a typed Sphinx-needs evidence reference | A portable model needs an explicit Feature/Dependable Element level or a documented mapping. |
| Component (`comp`) | Used as the projection root and preserved by ID/type/URI | Component identity must remain distinct from an SBOM package and from a source folder. |
| Unit | Not present in this reduced public example | The SPDX mapping needs an unambiguous Unit level below Component. |
| Assumption of Use (`aou_req`) | Preserved as a typed requirement reference | SEooC exchanges need first-class AoU semantics, applicability and satisfaction/verification links. |
| `safety: QM`, `ASIL_B` or `ASIL_D` | Projected exactly to the corresponding S-CORE functional-safety value | Safety integrity is contextual and must not become a global package property. |
| Unsupported ASIL/SIL/DAL or security value | Export rejected | The S-CORE exporter must not imply support for a vocabulary the source model does not use. |
| `status: valid` | Recorded in `sourceOfTruth.rootElementStatus` | Source lifecycle state must not be silently reinterpreted as an external approval. |
| Sphinx-needs relationships | Source IDs remain resolvable; no new relation is inferred | Dependable Element / Feature / Component / Unit and AoU relationships need lossless standardized predicates. |

This makes the PoC useful as a standards feedback vehicle: it demonstrates transport from an existing safety model while making
the semantic gaps explicit, rather than creating a parallel safety argumentation system.
