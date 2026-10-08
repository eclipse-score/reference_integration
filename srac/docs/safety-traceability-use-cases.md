# Policy-Aware Safety Traceability and Evidence Exchange Use Cases

## Purpose

This document defines use cases for maintaining machine-verifiable safety
traceability across software changes and transfers of responsibility. The goal
is to preserve authoritative engineering evidence while minimizing unnecessary
manual checkpoints during routine feature development.

The intended approach is to:

- evaluate the affected portion of the traceability graph for each change;
- periodically perform a full re-evaluation to confirm completeness;
- preserve authoritative sources, provenance, and approval responsibility;
- activate policy checks according to product context, jurisdiction, legal
  entity, and lifecycle stage;
- require human checkpoints when defined safety, organizational, or regulatory
  boundaries are crossed; and
- package the resulting traceability and evidence for downstream assessment.

Success should be measured using:

- the percentage of changes completed without a human checkpoint;
- the time required to identify affected artifacts;
- false-negative and false-positive impact-analysis results;
- stale or unresolved evidence detected before release; and
- the time required to assemble assessment evidence.

## Responsibility boundary

The originating engineering and safety lifecycle remains authoritative. An
exporter creates a deterministic projection of those records; it does not make
or approve a safety decision. Receiving tools may validate, correlate, query,
and display the supplied context, but they do not become the safety authority.

An SPDX, CycloneDX, or SRAC artifact demonstrates what was exported, from which
source revision, and under which mapping and policy versions. The artifact does
not independently certify the software.

## Use-case matrix

| Use case | Trigger | Responsible parties | Applicable policy context | Automated support | Human checkpoint | Generated evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Tier 1 to OEM to independent assessor or approval authority | Component release, version update, changed assumption, vulnerability, or safety finding | The Tier 1 provides component evidence; the OEM performs the contextual assessment; an independent assessor reviews the safety case; an approval authority acts where regulatory approval applies | Supplier and OEM policies, the product safety process, and applicable regulatory requirements | Verify schema, provenance, digest, component identity, assumption coverage, traceability completeness, and stale evidence | OEM safety approval, independent assessment, and any applicable regulatory approval | Supplier evidence, OEM impact analysis, decisions, approvals, and a safety-case or assessment evidence package |
| Internal feature development | Code, architecture, requirement, or configuration change | Developer, component owner, feature team, and safety authority | Engineering, safety, release, and product-specific policies | Traverse the affected graph and check linked requirements, tests, inspections, evidence, and approvals | Required when a safety boundary, baseline, assumption, or required evidence changes | Impact analysis, changed requirements and tests, verification results, and decisions |
| Internal responsibility transfer | Responsibility moves between teams, repositories, or legal entities | Outgoing owner, incoming owner, and approving authority | Organizational ownership, engineering, and release policies | Check baseline completeness, provenance, unresolved obligations, and accepted evidence | The incoming owner formally accepts the baseline and open obligations | Handover record, accepted baseline, unresolved-obligation list, and approval |
| Country, jurisdiction, or legal-entity transfer | Software deployment, maintenance, or responsibility moves to another jurisdiction or entity | Product owner and legal, compliance, security, and safety representatives | Potentially applicable laws, regulations, and organizational policies, identified by jurisdiction, entity, product, lifecycle stage, and effective date | Propose potentially applicable policies for legal or compliance confirmation and identify additional checks or controls | Legal or compliance confirms applicability; the relevant safety or regulatory authority approves where required | Confirmed applicability decision, control results, exceptions, and accountable-party approval |
| OSS component intake | A new or updated OSS component enters a safety-related product | The OSS project is not a responsible supplier and has no contractual obligation to provide safety evidence; the OEM or integrator assumes responsibility for assessment and use | OEM or integrator intake, security, licensing, and safety policies | Correlate the component, identify available upstream information, and evaluate assumptions and evidence gaps | The OEM or integrator determines whether additional analysis, controls, or evidence are required | Undetermined upstream state, OEM assessment, compensating evidence, and contextual decision |

## Checkpoint triggers

A human checkpoint is required when:

- safety relevance or an assurance level changes;
- an assumption of use becomes invalid;
- ownership or legal responsibility changes;
- deployment jurisdiction changes;
- a candidate legal or regulatory requirement may become applicable;
- required evidence is missing, stale, contradictory, or invalid;
- the computed impact boundary is incomplete or ambiguous;
- a certification or assessment baseline changes; or
- a vulnerability or security finding affects a safety-relevant component.

Automated tools may identify candidate policy applicability, but legal and
compliance representatives confirm whether a law or regulation applies.

## Completeness and tool confidence

Incremental analysis must include transitive dependencies rather than only
directly linked elements. An incomplete or ambiguous impact boundary is itself
a checkpoint condition.

A full re-evaluation is required periodically and when:

- the assessment baseline changes;
- the metamodel or a mapping overlay changes;
- an applicable policy version changes;
- a release reaches a defined assurance milestone; or
- incremental and baseline results disagree.

Every automated result records the tool name, tool version, configuration,
input digest, mapping version, and policy version. The adopter evaluates tool
confidence for the intended use and determines whether qualification or other
confidence measures are required.

## Packaging concept

```text
Authoritative engineering sources
        |
        v
Versioned metamodel, mapping overlays, and policy references
        |
        v
Incremental checks and periodic full re-evaluation
        |
        v
Portable SRAC / SPDX / CycloneDX projection
        |
        v
Digest verification (signature where available)
        |
        v
OEM contextual decisions
(identity, policy version, provenance, and digest)
        |
        v
Safety-case or assessment evidence package
        |
        v
Independent assessment
(and regulatory approval where applicable)
```

The metamodel rules and relationship constraints are maintained in one
versioned source. Source-specific systems, such as Sphinx-Needs, Dependable
Elements, or TRLC/Lobster, use mapping overlays to project their records into a
common graph. Exporters consume that graph rather than reimplementing the
rules.

Producer-side automation validates schema conformance, references,
traceability, mapping coverage, source digests, and reproducibility.
Receiver-side automation verifies the artifact digest or signature,
provenance, and deterministic correlation with SBOM components. Neither side
autonomously creates or approves a safety decision.

OEM decisions and approvals are recorded with the responsible identity,
timestamp, policy version, source references, and digest before the evidence
package is assembled.

## End-to-end demonstrator

The initial demonstrator should exercise the Tier 1, OEM, and independent
assessment flow:

1. A Tier 1 supplies a component SBOM and a component-level safety manifest.
2. The OEM verifies the package and deterministically correlates it with the
   component used in a product.
3. The OEM maps the supplied evidence into the product and system context.
4. One supplier assumption is satisfied and another requires additional
   evidence.
5. An OEM policy activates a human safety checkpoint.
6. The OEM records its contextual decision with identity, policy version,
   provenance, and digest.
7. The supplier-to-OEM evidence chain is packaged for independent assessment.
8. A later component update marks the affected decision and evidence as stale.
9. A tampered package or mismatched digest is rejected without importing its
   assertions.
10. A baseline-triggered full evaluation confirms that the incremental result
    is contained within the complete affected set.

## Demonstrator acceptance criteria

The demonstrator passes when:

- every component reference resolves deterministically without name-only
  matching;
- all required traceability edges are complete;
- supplier and OEM assertions and decisions remain distinguishable;
- candidate policy applicability remains provisional until confirmed by an
  authorized person;
- an invalid digest, invalid signature, or invalid provenance fails closed;
- stale evidence is detected after the component update;
- the incremental affected set is contained within the full evaluation result;
- every automated result identifies its tool, configuration, mapping, policy,
  and input versions; and
- no exporter or receiving tool autonomously creates or approves a safety
  decision.

## Open design questions

- What is the minimum common set of node, relationship, provenance, and
  constraint types required by all supported source models?
- Which policies are enforceable automated checks, and which are advisory
  candidates requiring human confirmation?
- Which events require a full evaluation rather than an incremental one?
- How are mapping and policy versions selected, distributed, and retired?
- What evidence is required at each responsibility-transfer boundary?
- Which tool-confidence measures are required for each intended safety use?
