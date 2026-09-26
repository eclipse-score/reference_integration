# CycloneDX 1.6 mapping for the SRAC sidecar PoC

This mapping is experimental and does not claim native SRAC support in CycloneDX 1.6.

| SRAC concept | CycloneDX 1.6 representation in the pilot |
|---|---|
| Component identity | `component.purl` and `bom-ref` |
| Component version | `component.version` and the PURL version |
| SRAC sidecar location | Proposed `externalReferences` entry of type `other` |
| Sidecar integrity | Hash on the external reference when the sidecar is published |
| Safety relevance, rationale and review state | Retained in the SRAC sidecar |
| Requirements and evidence | URI references retained in the SRAC sidecar |
| Trigger, impact analysis, decisions and verification | Retained in the SRAC sidecar; no native CycloneDX 1.6 claim is made |

The PoC first proves a deterministic join using the component PURL and version. It emits a separate enrichment report and does
not mutate the CycloneDX document. A later `sbom-tool` change may publish the external reference after the representation is reviewed.
