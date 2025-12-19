.. SPDX-License-Identifier: CC-BY-SA-4.0

..
   note::
   This document is based on work by Codethink available at
   https://gitlab.com/CodethinkLabs/trustable/trustable.
   This modified version is licensed under CC-BY-SA-4.0
   in compliance with the original license.

   Changes from original:
   - levels have been removed
   - separated files are aggregated into a single file
   - transferred from markdown to rst
   - sphinx-needs meta data is added

.. _tsf_tenets:

Tenets
------

.. tenet:: TT-PROVENANCE
   :id: tenet__trust__tt-provenance
   :status: valid
   :links: assertion__trust__ta-supply-chain, assertion__trust__ta-inputs

   All source code (and attestations for claims) for XYZ are provided with
   known provenance.

   **Guidance**

   Our trust in XYZ is informed by both the individuals and organisations
   contributing to it, and by the software tools and components used to develop
   and maintain it.

   Ideally we want all XYZ contributors to be expert, motivated, reliable,
   transparent and ethical. Unfortunately this is not always achievable in
   practice:

   - Given the scale, complexity and evolution of modern software systems it is
     impossible for engineers to be expert in all topics.
   - Even the most competent engineers have bad days.
   - Many engineers are unable to share information due to commercial secrecy
     agreements.
   - Individuals and teams may be motivated or manipulated by external pressures,
     e.g. money and politics.

   We can and should, however, consider who produced XYZ and its components,
   their motivations and practices, the assertions they make, supporting
   evidence for these assertions, and feedback from users of XYZ if available.

   Similarly, we want existing software used to create XYZ to be well
   documented, actively maintained, thoroughly tested, bug-free and well
   suited to its use in XYZ. In practice, we will rarely have all of this, but
   we can at least evaluate the software components of XYZ, and the tools used to
   construct it.

.. tenet:: TT-CONSTRUCTION
   :id: tenet__trust__tt-construction
   :status: valid
   :links: assertion__trust__ta-tests, assertion__trust__ta-releases, assertion__trust__ta-iterations

   Tools are provided to build XYZ from trusted sources (also provided) with
   full reproducibility.

   **Guidance**

   Where possible we prefer to build, configure and install XYZ from source
   code, because this reduces (but does not eliminate) the possibility of supply
   chain tampering.

   When constructing XYZ we aspire to a set of best practices including:

   - reproducible builds
       - construction from a given set of input source files and build instructions leads to a specific fileset
       - re-running the build leads to exactly the same fileset, bit-for-bit
   - ensuring that all XYZ dependencies are known and controlled (no reliance on
     external/internet resources, or unique/golden/blessed build server); and
   - automated build, configuration and deployment of XYZ based on declarative
     instructions, kept in version control (e.g. no engineer laptop in the loop
     for production releases)

   Some of these constraints may be relaxed during XYZ development/engineering
   phases, but they must all be fully applied for production releases. Note that
   when we receive only binaries, without source code, we must rely much more
   heavily on Provenance; who supplied the binaries, and how can we trust their
   agenda, processes, timescales and deliveries?

.. tenet:: TT-CHANGES
   :id: tenet__trust__tt-changes
   :status: valid
   :links: assertion__trust__ta-fixes, assertion__trust__ta-updates

   XYZ is actively maintained, with regular updates to dependencies, and changes
   are verified to prevent regressions.

   **Guidance**

   We expect that XYZ will need to be modified many times during its
   useful/production lifetime, and therefore we need to be sure that we can make
   changes without breaking it. In practice this means being able to deal with
   updates to dependencies and tools, as well as updates to XYZ itself.

   Note that this implies that we need to be able to:

   - verify that updated XYZ still satisfies its expectations (see below), and
   - understand the behaviour of upstream/suppliers in delivering updates (e.g.
     frequency of planned updates, responsiveness for unplanned updates such as
     security fixes).

   We need to consider the maturity of XYZ, since new software is likely to
   contain more undiscovered faults/bugs and thus require more changes. To
   support this we need to be able to understand, quantify and analyse changes
   made to XYZ (and its dependencies) on an ongoing basis, and to assess the XYZ
   approach to bugs and breaking changes.

   We also need to be able to make modifications to any/all third-party
   components of XYZ and dependencies of XYZ, unless we are completely confident
   that suppliers/upstream will satisfy our needs throughout XYZ's production
   lifecycle.

.. tenet:: TT-EXPECTATIONS
   :id: tenet__trust__tt-expectations
   :status: valid
   :links: assertion__trust__ta-behaviours, assertion__trust__ta-misbehaviours, assertion__trust__ta-indicators, assertion__trust__ta-constraints

   Documentation is provided, specifying what XYZ is expected to do, and what
   it must not do, and how this is verified.

   **Guidance**

   While most modern software is developed without a formal
   requirement/specification process, we need to be clear about what we expect
   from XYZ, communicate these expectations, and verify that they are met.

   In most (almost all?) cases, we need to verify our expectations by
   tests. These tests must be automated and applied for every candidate release
   of XYZ.

   It is not sufficient to demonstrate that the software does what we expect. We
   also need to analyse the potential risks in our scenario, identify
   unacceptable and/or dangerous misbehaviours and verify that they are absent,
   prevented or mitigated.

   In most cases it is not sufficient to demonstrate behaviours and mitigations
   only in a factory/laboratory environment. We also need to establish methods for
   monitoring critical behaviours and misbehaviours in production, and methods for
   taking appropriate action based on advance warning signals of potential
   misbehaviour.

.. tenet:: TT-RESULTS
   :id: tenet__trust__tt-results
   :status: valid
   :links: assertion__trust__ta-validation, assertion__trust__ta-data, assertion__trust__ta-analysis

   Evidence is provided to demonstrate that XYZ does what it is supposed to
   do, and does not do what it must not do.

   **Guidance**

   We need to perform tests to verify expected behaviours and properties of XYZ
   in advance of every candidate release.

   We also need to validate these tests, to confirm that they do actually test
   for the expected behaviours or properties, and that test failures are
   properly detected. Usually this can be done by inducting software faults to
   exercise the tests and checking that the results record the expected failure.

   Similarly we need to verify that prevention measures and mitigations continue
   to work for each XYZ candidate release, and in production.

   All these validated test results and monitored advance warning signal data from production
   must be collected and analysed on an ongoing basis. We need to notice when
   results or trends in advance warning signals change, and react appropriately.

.. tenet:: TT-CONFIDENCE
   :id: tenet__trust__tt-confidence
   :status: valid
   :links: assertion__trust__ta-methodologies, assertion__trust__ta-confidence

   Confidence in XYZ is measured by analysing actual performance in tests and in
   production.

   **Guidance**

   Our overall objective is to deliver releases of XYZ that meet our
   expectations and do not cause harm. By collecting and assessing evidence for
   all of the factors above, we aim to assess (ideally measure) confidence in
   each release candidate, to support go/nogo decision-making, In assessing
   confidence we need to consider various categories of evidence including:

   - subjective (e.g. provenance, reviews and approvals)
   - binary (e.g. test pass/fail)
   - stochastic (e.g. scheduling test results over time)
   - empirical (e.g. advance warning signal monitoring data from production deployments)
