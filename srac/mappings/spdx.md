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

The PoC first proves a deterministic join using the package PURL and version. It emits a separate enrichment report and does
not mutate the SPDX document. A later `sbom-tool` change may publish the external reference after the representation is reviewed.
