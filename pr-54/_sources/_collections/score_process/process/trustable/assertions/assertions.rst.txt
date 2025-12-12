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

.. _tsf_assertions:

Assertions
----------

.. assertion:: TA-SUPPLY-CHAIN
   :id: assertion__trust__ta-supply-chain
   :status: valid

   All sources for XYZ and tools are mirrored in our controlled environment

   **Guidance**

   This assertion is satisfied to the extent that we have traced and captured
   source code for XYZ and all of its dependencies (including transitive
   dependencies, all the way down), and for all of the tools used to construct
   XYZ from source, and have mirrored versions of these inputs under our control.

   'Mirrored' in this context means that we have a version of the upstream project
   that we keep up-to-date with additions and changes to the upstream project,
   but which is protected from changes that would delete the project, or remove
   parts of its history.

   Clearly this is not possible for components or tools are provided only in
   binary form, or accessed via online services - in these circumstances we can
   only assess confidence based on attestations made by the suppliers, and on our
   experience with the suppliers' people and processes.

   Keep in mind that even if repositories with source code for a particular
   component or tool are available, not all of it may be stored in version control system as
   plaintext. A deeper analysis is required in TA-INPUTS to assess the impact of any
   binaries present within the repositories of the components and tools used.

   **Evidence**

   - list of all XYZ components including
       - URL of mirrored projects in controlled environment
       - URL of upstream projects
   - successful build of XYZ from source
       - without access to external source projects
       - without access to cached data
   - update logs for mirrored projects
   - mirrors reject history rewrites
   - mirroring is configured via infrastructure under direct control

   **Confidence scoring**

   Confidence scoring for TA-SUPPLY_CHAIN is based on confidence that all inputs and
   dependencies are identified and mirrored, and that mirrored projects cannot be
   compromised.

   **Checklist**

   - Could there be other components, missed from the list?
   - Does the list include all toolchain components?
   - Does the toolchain include a bootstrap?
   - Could the content of a mirrored project be compromised by an upstream change?
   - Are mirrored projects up to date with the upstream project?

.. assertion:: TA-INPUTS
   :id: assertion__trust__ta-inputs
   :status: valid

   Components and tools used to construct and verify XYZ are assessed, to identify
   potential risks and issues


   **Guidance**

   To satisfy this assertion, the components and tools used to construct and verify
   XYZ releases need to be identified and assessed, to identify available sources
   of evidence about these dependencies.

   For components, we need to consider how their potential misbehaviours might
   impact our expectations for XYZ, identify sources of information (e.g. bug
   databases, published CVEs) that can be used to identify known risks or issues,
   and tests that can be used to identify these. These provide the inputs to
   TA-FIXES.

   For the tools we use to construct and verify XYZ, we need to consider how
   their misbehaviour might lead to an unintended change in XYZ, or fail to detect
   misbehaviours of XYZ during testing, or produce incorrect or incomplete data
   that we use when verifying an XYZ release.

   Where impacts are identified, we need to consider both how serious they might be
   (severity) and whether they would be detected by another tool, test or manual
   check (detectability).

   For impacts with a high severity and/or low detectability, additional analysis
   should be done to check whether existing tests are effective at detecting the
   misbehaviours or resulting impacts, and new tests or Expectations should be added
   to prevent or detect misbehaviours or impacts that are not currently addressed.

   **Evidence**

   - List of components used in construction of XYZ including
       - Indication of whether content is provided as source or binary
   - Record of component assessment:
       - Originating project and version
       - Date of assessments and identity of assessors
       -  Role of component in XYZ
       - Sources of bug and risk data for the component
       -  Potential misbehaviours and risks identified and assessed
   - List of tools used in construction and verification
   - Record of tool impact assessments:
       - Originating project and version of tool
       - Date of assessments and identity of assessors
       - Roles of tool in production of XYZ releases
       - Potential tool misbehaviours and impacts
       - Detectability and severity of impacts
   - Record of tool qualification reviews
       - For high impact tools only (low detectability and/or high severity)
       - Link to impact assessment
       -  Date of reviews and identity of reviewers
       - Analysis of impacts and misbehaviours
       - Existing tests or measures (e.g. manual reviews) to address these
       - Additional tests and/or Expectations required

   **Confidence scoring**

   Confidence scoring for TA-INPUTS is based on the set of components and tools
   identified, how many of (and how often) these have been assessed for their risk
   and impact for XYZ, and the sources of risk and issue data identified.

   **Checklist**

   - Are there components that are not on the list?
   - Are there assessments for all components?
   - Has an assessment been done for the current version of the component?
   - Have sources of bug and/or vulnerability data been identified?
   - Have additional tests and/or Expectations been documented and linked to component assessment?
   - Are component tests run when integrating new versions of components?
   - Are there tools that are not on the list?
   - Are there impact assessments for all tools?
   - Have tools with high impact been qualified?
   - Were assessments or reviews done for the current tool versions?
   - Have additional tests and/or Expectations been documented and linked to tool assessments?
   - Are tool tests run when integrating new versions of tools?
   - Are tool and component tests included in release preparation?
   - Can patches be applied, and then upstreamed for long-term maintenance?

.. assertion:: TA-TESTS
   :id: assertion__trust__ta-tests
   :status: valid

   All tests for XYZ, and its build and test environments, are constructed from
   controlled/mirrored sources and are reproducible, with any exceptions documented

   **Guidance**

   This assertion is satisfied to the extent that we

   - have implemented all of the tests specified in TA-BEHAVIOURS
   - have implemented fault inductions specified in TA-MISBEHAVIOURS
   - have implemented or integrated test tooling and environments for these
   - can demonstrate that all of these are constructed from:
       - change-managed sources (see TA-UPDATES)
       - mirrored sources (see TA-SUPPLY_CHAIN)

   All of the above must ensure that test results are retroactively reproducible,
   which is easily achieved through automated end-to-end test execution alongside
   necessary environment setups. Note that with non-deterministic software, exact
   results may not be reproducible, but high-level takeaways and exact setup should
   still be possible.

   **Evidence**

   - list of tests
   - list of fault inductions
   - list of test environments
   - construction configuration and results

   **Confidence scoring**

   Confidence scoring for TA-TESTS is based on the presence of tests and our
   confidence in their implementation and construction.

   **CHECKLIST**

   - How confident are we that we've implemented all of the specified tests?
   - How confident are we that we've implemented all of the specified fault
     inductions?
   - How confident are we that we have test tooling and environments enabling us
     to execute these tests and fault inductions?
   - How confident are we that all test components are taken from within our
     controlled environment?
   - How confident are we that all of the test environments we are using are also
     under our control?

.. assertion:: TA-RELEASES
   :id: assertion__trust__ta-releases
   :status: valid

   Construction of XYZ releases is fully repeatable and the results are fully
   reproducible, with any exceptions documented and justified.

   **Guidance**

   This assertion is satisfied if the construction of a given iteration of XYZ is
   both *repeatable*, demonstrating that all of the required inputs are controlled,
   and *reproducible*, demonstrating that the construction toolchain and build
   environment(s) are controlled (as described by TA-TESTS).

   This assertion can be most effectively satisfied in a Continuous Integration
   environment with mirrored projects (see TA-SUPPLY_CHAIN), using build servers that have
   no internet access. The aim is to show that all build tools, XYZ components and
   dependencies are built from inputs that we control, that rebuilding leads to
   precisely the same binary fileset, and that builds can be repeated on any
   suitably configured server.

   Again this will not be achievable for components/tools provided in binary form,
   or accessed via an external service - we must consider our confidence in
   attestations made by/for the supply chain.

   All non-reproducible elements, such as timestamps or embedded random values from
   build metadata, are clearly identified and considered when evaluating
   reproducibility.

   **Evidence**

   - list of reproducible SHAs
   - list of non-reproducible elements with:
       - explanation and justification
       - details of what is not reproducible
   - evidence of configuration management for build instructions and infrastructure
   - evidence of repeatable builds

   **Confidence scoring**

   Calculate:

   R = number of reproducible components (including sources which have no build stage)
   N = number of non-reproducible
   B = number of binaries
   M = number of mirrored
   X = number of things not mirrored

   Confidence scoring for TA-RELEASES could possibly be calculated as
   R / (R + N + B + M / (M + X))

   **Checklist**

   - How confident are we that all components are taken from within our
     controlled environment?
   - How confident are we that all of the tools we are using are also under our
     control?
   - Are our builds repeatable on a different server, or in a different context?
   - How sure are we that our builds don't access the internet?
   - How many of our components are non-reproducible?
   - How confident are we that our reproducibility check is correct?

.. assertion:: TA-ITERATIONS
   :id: assertion__trust__ta-iterations
   :status: valid

   All constructed iterations of XYZ include source code, build instructions,
   tests, results and attestations.

   **Guidance**

   This assertion is best satisfied by checking generated documentation to confirm
   that:

   - all components, dependencies and tools are identified in a manifest
   - the manifest includes links to source code
   - where source is unavailable, the supplier is identified

   **Evidence**

   - list of components with source
       - source code
       - build instructions
       - test code
       - test results summary
       - attestations
   - list of components where source code is not available
       - risk analysis
       - attestations

   **Confidence scoring**

   Confidence scoring for TA-ITERATIONS based on

   - number and importance of source components
   - number and importance of non-source components
   - assessment of attestations

   **Checklist**

   - How much of the software is provided as binary only, expressed as a fraction of the BoM list?
   - How much is binary, expressed as a fraction of the total storage footprint?
   - For binaries, what claims are being made and how confident are we in the people/organisations making the claims?
   - For third-party source code, what claims are we making, and how confident are we about these claims?
   - For software developed by us, what claims are we making, and how confident are we about these claims?

.. assertion:: TA-FIXES
   :id: assertion__trust__ta-fixes
   :status: valid

   Known bugs or misbehaviours are analysed and triaged, and critical fixes or
   mitigations are implemented or applied.

   **Guidance**

   This assertion is satisfied to the extent that we have identified, triaged
   and applied fixes and/or mitigations to the faults identified in XYZ and the
   bugs and CVEs identified by upstream component projects.

   We can increase confidence by assessing known faults, bugs and vulnerabilities,
   to establish their relevance and impact for XYZ.

   In principle this should involve not just the code in XYZ, but also its
   dependencies (all the way down), and the tools used to construct the release.
   However we need to weigh the cost/benefit of this work, taking into account

   - the volume and quality of available bug and CVE reports
   - likelihood that our build/configuration/usecase is actually affected

   **Evidence**

   - List of known bugs fixed since last release
   - List of outstanding bugs still not fixed, with triage/prioritisation based on severity/relevance/impact
   - List of known CVEs fixed since last release
   - List of outstanding CVEs still not fixed, with triage/prioritisation based on severity/relevance/impact
   - List of XYZ component versions, showing where a newer version exists upstream
   - List of component version updates since last release
   - List of fixes applied to developed code since last release
   - List of fixes for developed code that are outstanding, not applied yet
   - List of XYZ faults outstanding (O)
   - List of XYZ faults fixed since last release (F)
   - List of XYZ faults mitigated since last release (M)

   **Confidence scoring**

   Confidence scoring for TA-FIXES can be based on

   - some function of [O, F, M] for XYZ
   - number of outstanding relevant bugs from components
   - bug triage results, accounting for undiscovered bugs
   - number of outstanding CVEs
   - CVE triage results, accounting for undiscovered bugs CVEs
   - confidence that known fixes have been applied
   - confidence that known mitigations have been applied
   - previous confidence score for TA-FIXES

   Each iteration, we should improve the algorithm based on measurements

   **Checklist**

   - How many faults have we identified in XYZ?
   - How many unknown faults remain to be found, based on the number that have been processed so far?
   - Is there any possibility that people could be motivated to manipulate the lists (e.g. bug bonus or pressure to close).
   - How many faults may be unrecorded (or incorrectly closed, or downplayed)?
   - How do we collect lists of bugs and CVEs from components?
   - How (and how often) do we check these lists for relevant bugs and CVEs?
   - How confident can we be that the lists are honestly maintained?
   - Could some participants have incentives to manipulate information?
   - How confident are we that the lists are comprehensive?
   - Could there be whole categories of bugs/CVEs still undiscovered?
   - How effective is our triage/prioritisation?
   - How many components have never been updated?
   - How confident are we that we could update them?
   - How confident are we that outstanding fixes do not impact our expectations?
   - How confident are we that outstanding fixes do not address misbehaviours?

.. assertion:: TA-UPDATES
   :id: assertion__trust__ta-updates
   :status: valid

   XYZ components, configurations and tools are updated under specified change and
   configuration management controls.

   **Guidance**

   This assertion requires that that we have control over all changes to XYZ,
   including changes to the configurations, components and tools we use to build
   it, and the versions of dependencies that we use.

   This means, the trustable controlled process is the only path to production for constructed target
   software.

   **Evidence**

   - change management process and configuration artifacts

   **Confidence scoring**

   Confidence scoring for TA-UPDATES is based on confidence that we have
   control over the changes that we make to XYZ, including its configuration and
   dependencies.

   **Checklist**

   - Where are the change and configuration management controls specified?
   - Are these controls enforced for all of components, tools and configurations?
   - Are there any ways in which these controls can be subverted, and have we mitigated them?

.. assertion:: TA-BEHAVIOURS
   :id: assertion__trust__ta-behaviours
   :status: valid

   Expected or required behaviours for XYZ are identified, specified, verified and
   validated based on analysis.

   Although it is practically impossible to specify all of the necessary behaviours
   and required properties for complex software, we must clearly specify the most
   important of these (e.g. where harm could result if given criteria are not met),
   and verify that these are correctly provided by XYZ.

   **Guidance**

   This assertion is satisfied to the extent that we have:

   - Determined which Behaviours are critical for consumers of XYZ and recorded them as Expectations.
   - Verified these Behaviours are achieved.

   Expectations could be verified by:

   - Functional testing for the system.
   - Functional soak testing for the system.
   - Specifying architecture and verifying its implementation with pre-merge integration testing for components.
   - Specifying components and verifying their implementation using pre-merge unit testing.

   The number and combination of the above verification strategies will depend on
   the scale of the project. For example, unit testing is more suitable for the
   development of a small library than of an OS.

   **Evidence**

   - List of expectations

   **Confidence scoring**

   Confidence scoring for TA-BEHAVIOURS is based on our confidence that the list of
   Expectations is accurate and complete, that Expectations are verified by tests,
   and that the effectiveness of these tests is validated by appropriate
   strategies.

   **Checklist**

   - How has the list of expectations varied over time?
   - How confident can we be that this list is comprehensive?
   - Could some participants have incentives to manipulate information?
   - Could there be whole categories of expectations still undiscovered?
   - Can we identify expectations that have been understood but not specified?
   - Can we identify some new expectations, right now?
   - How confident can we be that this list covers all critical requirements?
   - How comprehensive is the list of tests?
   - Is every Expectation covered by at least one implemented test?
   - Are there any Expectations where we believe more coverage would help?

.. assertion:: TA-MISBEHAVIOURS
   :id: assertion__trust__ta-misbehaviours
   :status: valid

   Prohibited misbehaviours for XYZ are identified, and mitigations are specified,
   verified and validated based on analysis.

   The goal of TA-MISBEHAVIOURS is to force engineers to think critically about their work.
   This means understanding and mitigating as many of the situations that cause the
   software to deviate from Expected Behaviours as possible. This is not limited to
   the contents of the final binary.

   **Guidance**

   This assertion is satisfied to the extent that we can:

   - Show we have identified all of the ways in which XYZ could deviate from its Expected Behaviours.
   - Demonstrate that mitigations have been specified, verified and validated for all Misbehaviours.

   Once Expected Behaviours have been identified in TA-BEHAVIOURS, there are at
   least four classes of Misbehaviour that can be identified:

   - Reachable vulnerable system states that cause deviations from Expected
     Behaviour. These can be identified by stress testing, failures in functional
     and soak testing in TA-BEHAVIOURS and reporting in TA-FIXES. Long run trends
     in both test and production data should also be used to identify these states.
   - Potentially unreachable vulnerable system states that could lead to deviations
     from Expected Behaviour. These can be identified using risk/hazard analysis
     techniques including HAZOP, FMEDA and STPA.
   - Vulnerabilities in the development process that could lead to deviations from
     Expected Behaviour. This includes those that occur as a result of misuse,
     negligence or malintent. These can be identified by incident investigation,
     random sampling of process artifacts and STPA of processes.
   - Configurations in integrating projects (including the computer or embedded
     system that is the final product) that could lead to deviations from Expected
     Behaviour.

   Identified Misbehaviours must be mitigated. Mitigations include patching,
   re-designing components, re-designing architectures, removing components,
   testing, static analysis etc. They explicitly *do not* include the use of AWIs
   to return to a known-good state. These are treated specifically and in detail in
   TA-INDICATORS.

   Mitigations could be verified by:

   - Specifying and repeatedly executing false negative tests to confirm that
     functional tests detect known classes of misbehaviour.
   - Specifying fault induction tests or stress tests to demonstrate that the
     system continues providing the Expected Behaviour after entering a vulnerable
     system state.
   - Performing statistical analysis of test data, including using statistical path
     coverage to demonstrate that the vulnerable system state is never reached.
   - Conducting fault injections in development processes to demonstrate that
     vulnerabilities cannot be exploited (knowingly or otherwise) to affect either
     output binaries or our analysis of it, whether this is by manipulating the
     source code, build environment, test cases or any other means.
   - Stress testing of assumptions of use. That is, confirming assumptions of use
     are actually consistent with the system and its Expected Behaviours by
     intentionally misinterpreting or liberally interpreting them in a test
     environment. For example, we could consider testing XYZ on different pieces of
     hardware that satisfy its assumptions of use.

   Remember that a Misbehaviour is *anything* that could lead to a deviation from
   Expected Behaviour. The specific technologies in and applications of XYZ should
   always be considered in addition to the guidance above.

   **Suggested evidence**

   - List of identified Misbehaviours
   - List of Expectations for mitigations addressing identified Misbehaviours
   - Risk analysis
   - Test analysis, including:
       - False negative tests
       - Exception handling tests
       - Stress tests
       - Soak tests

   **Confidence scoring**

   Confidence scoring for TA-MISBEHAVIOURS is based on confidence that
   identification and coverage of misbehaviours by tests is complete when
   considered against the list of Expectations.

   **Checklist**

   - How has the list of misbehaviours varied over time?
   - How confident can we be that this list is comprehensive?
   - How well do the misbehaviours map to the expectations?
   - Could some participants have incentives to manipulate information?
   - Could there be whole categories of misbehaviours still undiscovered?
   - Can we identify misbehaviours that have been understood but not specified?
   - Can we identify some new misbehaviours, right now?
   - Is every misbehaviour represented by at least one fault induction test?
   - Are fault inductions used to demonstrate that tests which usually pass can
     and do fail appropriately?
   - Are all the fault induction results actually collected?
   - Are the results evaluated?

.. assertion:: TA-INDICATORS
   :id: assertion__trust__ta-indicators
   :status: valid

   Advance warning indicators for misbehaviours are identified, and monitoring
   mechanisms are specified, verified and validated based on analysis.

   Not all deviations from Expected Behaviour can be associated with a specific
   condition. Therefore, we must have a strategy for managing deviations that
   arise from unknown system states, process vulnerabilities or configurations.

   This is the role of *Advanced Warning Indicators (AWI)*. These are specific
   metrics which correlate with deviations from Expected Behaviour and can be
   monitored in real time. The system should return to a defined known-good
   state when AWIs exceed defined tolerances.

   **Guidance**

   This assertion is met to the extent that:

   - We have identified indicators that are strongly correlated with observed
     deviations from Expected Behaviour in testing and/or production.
   - The system returns to a defined known-good state when AWIs exceed
     defined tolerances.
   - The mechanism for returning to the known-good state is verified.
   - The selection of Advance Warning Indicators is validated against the set of
     possible deviations from Expected behaviour.

   Note, the set of possible deviations from Expected behaviour *is not* the same
   as the set of Misbehaviours identified in TA-MISBEHAVIOURS, as it includes
   deviations due to unknown causes.

   Deviations are easily determined by negating recorded Expectations. Potential
   AWIs could be identified using source code analysis, risk analysis or incident
   reports. A set of AWIs to be used in production should be identified by
   monitoring candidate signals in all tests (functional, soak, stress) and
   measuring correlation with deviations.

   The known-good state should be chosen with regard to the system's intended
   consumers and/or context. Canonical examples are mechanisms like reboots,
   resets, relaunches and restarts. The mechanism for returning to a known-good
   state can be verified using fault induction tests. Incidences of AWIs triggering
   a return to the known-good state in either testing or production should be
   considered as a Misbehaviour in TA-MISBEHAVIOURS. Relying on AWIs alone is not
   an acceptable mitigation strategy. TA-MISBEHAVIOURS and TA-INDICATORS are
   treated separately for this reason.

   The selection of AWIs can be validated by analysing failure data. For instance,
   a high number of instances of deviations with all AWIs in tolerance implies the
   set of AWIs is incorrect, or the tolerance is too lax.

   **Evidence**

   - Risk analyses
   - List of advance warning indicators
   - List of Expectations for monitoring mechanisms
   - List of implemented monitoring mechanisms
   - List of identified misbehaviours without advance warning indicators
   - List of advance warning indicators without implemented monitoring mechanisms
   - Advance warning signal data as time series (see TA-DATA)

   **Confidence scoring**

   Confidence scoring for TA-INDICATORS is based on confidence that the list of
   indicators is comprehensive / complete, that the indicators are useful, and that
   monitoring mechanisms have been implemented to collect the required data.

   **Checklist**

   - How appropriate/thorough are the analyses that led to the indicators?
   - How confident can we be that the list of indicators is comprehensive?
   - Could there be whole categories of warning indicators still missing?
   - How has the list of advance warning indicators varied over time?
   - How confident are we that the indicators are leading/predictive?
   - Are there misbehaviours that have no advance warning indicators?
   - Can we collect data for all indicators?
   - Are the monitoring mechanisms used included in our Trustable scope?
   - Are there gaps or trends in the data?
   - If there are gaps or trends, are they analysed and addressed?
   - Is the data actually predictive/useful?

.. assertion:: TA-CONSTRAINTS
   :id: assertion__trust__ta-constraints
   :status: valid

   Constraints on adaptation and deployment of XYZ are specified.

   **Guidance**

   Constraints on reuse, reconfiguration, modification, and deployment are
   specified to enhance the trustability of outputs. To ensure clarity,
   scoping boundaries regarding what the output cannot do - especially where common
   assumptions from applied domains may not hold - must be explicitly documented.
   These constraints are distinct from measures that mitigate misbehaviours; rather,
   they define the boundaries within which the system is designed to operate.
   This upfront documentation clarifies the intended use of specified Statements,
   highlights known limitations, and prevents misinterpretation.

   These constraints - categorized into explicit limitations and assumptions of
   use - serve as a guide for both stakeholders and users. They define the intended
   scope and provide a clear interface for how upstream and downstream systems can
   integrate, modify, install, reuse, or reconfigure to achieve the desired output.
   Additionally, the documentation explicitly defines the contexts in which the
   integrity of existing Statements is preserved and whether any reimplementation
   is necessary.

   Crucially, these limitations are not unresolved defects resulting from triage
   decisions but deliberate exclusions based on design choices. Each omission
   should be accompanied by a clear rationale, ensuring transparency for future
   scope expansion and guiding both upstream and downstream modifications.

   **Suggested evidence**

   - Installation manuals with worked examples
   - Configuration manuals with worked examples
   - Specification documentation with a clearly defined scope
   - User guides detailing limitations in interfaces designed for expandability or
     modularity
   - Documented strategies used by external users to address constraints and
     work with existing Statements

   **Confidence scoring**

   The reliability of these constraints should be assessed based on the absence of
   contradictions and obvious pitfalls within the defined Statements.

   **Checklist**

   - Are the constraints grounded in realistic expectations, backed by real-world
     examples?
   - Do they effectively guide downstreams in expanding upon existing Statements?
   - Do they provide clear guidance for upstreams on reusing components with
     well-defined claims?
   - Are any Statements explicitly designated as not reusable or adaptable?
   - Are there worked examples from downstream or upstream users demonstrating
     these constraints in practice?
   - Have there been any documented misunderstandings from users, and are these
     visibly resolved?
   - Do external users actively keep up with updates, and are they properly
     notified of any changes?

.. assertion:: TA-VALIDATION
   :id: assertion__trust__ta-validation
   :status: valid

   All specified tests are executed repeatedly, under defined conditions in
   controlled environments, according to specified objectives.

   **Guidance**

   This assertion is satisfied to the extent that all of the tests specified in
   TA-BEHAVIOURS and constructed in TA-TESTS are correctly executed in a controlled
   environment on a defined cadence (e.g. daily) or for each proposed change, and
   on all candidate release builds for XYZ.

   Note that correct behaviour of tests may be confirmed using fault induction
   (e.g. by introducing an error or misconfiguration into XYZ).

   **Evidence**

   - Test results from per-change tests
   - Test results from scheduled tests as time series

   **Confidence scoring**

   Confidence scoring for TA-VALIDATION is based on verification that we have
   results for all tests (both pass / fail and performance)

   **Checklist**

   - How confident are we that all test results are being captured?
   - Can we look at any individual test result, and establish what it relates to?
   - Can we trace from any test result to the expectation it relates to?
   - Can we identify precisely which environment (software and hardware) were used?
   - How many pass/fail results would be expected, based on the scheduled tests?
   - Do we have all of the expected results
   - Do we have time-series data for all of those results?
   - If there are any gaps, do we understand why?
   - Are the test validation strategies credible and appropriate?
   - What proportion of the implemented tests are validated?

.. assertion:: TA-DATA
   :id: assertion__trust__ta-data
   :status: valid

   Data is collected from tests, and from monitoring of deployed software,
   according to specified objectives.

   **Guidance**

   This assertion is satisfied if results from all tests and monitored deployments are captured accurately, ensuring:

   - Sufficient precision for meaningful analysis
   - Enough contextual information to reproduce the test setup, though not necessarily the exact results (e.g., runner ID, software version SHA)

   To prevent misinterpretation, all data storage mechanisms and locations must be documented, along with long-term storage strategies, ensuring historical analyses can be reliably replicated.

   **Evidence**

   - Time-series results for each test.
   - List of monitored indicators.
   - Time-series test data for each indicator.
   - Time-series production data for each indicator.

   **Confidence scoring**

   Confidence scoring for TA-DATA is based on comparison of actual failure
   rates with targets, and analysis of spikes and trends

   **Checklist**

   - Is all test data stored with long-term accessibility?
   - Is all monitoring data stored with long-term accessibility?
   - Are extensible data models implemented?
   - Is sensitive data handled correctly (broadcasted, stored, discarded, or anonymised) with appropriate encryption and redundancy?
   - Are proper backup mechanisms in place?
   - Are storage and backup limits tested?
   - Are all data changes traceable?
   - Are concurrent changes correctly managed and resolved?
   - Is data accessible only to intended parties?
   - Are any subsets of our data being published?

.. assertion:: TA-ANALYSIS
   :id: assertion__trust__ta-analysis
   :status: valid

   Collected data from tests and monitoring of deployed software is analysed
   according to specified objectives.

   **Guidance**

   This assertion is satisfied to the extent that test data, and data collected
   from monitoring of deployed versions of XYZ, has been analysed, and the results
   used to inform the refinement of expectations and risk analysis.

   The extent of the analysis is with sufficient precision to confirm that:

   - all expectations (TA-BEHAVIOURS) are met
   - all misbehaviours (TA-MISBEHAVIOURS) are detected or mitigated
   - all advance warning indicators (TA-INDICATORS) are monitored
   - misbehaviour/failure rates (calculated directly or inferred by statistics) are
     within acceptable tolerance

   Where test results expose misbehaviours not identified in our analysis (TA-ANALYSIS),
   we add the new misbehaviours to our Expectations (TA-BEHAVIOURS and TA-MISBEHAVIOURS). Where
   necessary, as informed by our ongoing confidence evaluation (TA-CONFIDENCE), we improve
   and repeat the analysis (TA-ANALYSIS).

   **Evidence**

   - Analysis of test data vs thresholds
   - Analysis of failures
   - Analysis of spikes and trends

   **Confidence scoring**

   Confidence scoring for TA-ANALYSIS is based on Key Performance Indicators (KPIs)
   that may indicate problems in development, test, or production

   **CHECKLIST**

   - What fraction of expectations are covered by the test data?
   - What fraction of misbehaviours are covered by the monitored indicator data?
   - How confident are we that the indicator data are accurate and timely?
   - How reliable is the monitoring process?
   - How well does the production data correlate with our test data?
   - Are we publishing our data analysis?
   - Are we comparing and analysing production data vs test?
   - Are our results getting better, or worse?
   - Are we addressing spikes/regressions?
   - Do we have sensible/appropriate target failure rates?
   - Do we need to check the targets?
   - Are we achieving the targets?

.. assertion:: TA-METHODOLOGIES
   :id: assertion__trust__ta-methodologies
   :status: valid

   Manual methodologies applied for XYZ by contributors, and their results, are
   managed according to specified objectives.

   **Guidance**

   To satisfy this assertion, the manual processes applied in the verification of
   XYZ must be documented, together with the methodologies used, the results of
   applying these processes to specific aspects and iterations of XYZ or its
   components, and evidence that they have been reviewed using documented criteria.

   Any data analysis for TA-ANALYSIS should ideally be mostly automated to establish
   continuous feedback mechanisms. However, specifically, manual processes - such
   as those used for quality control assurances and the appropriate assignment of
   responsibilities - must be documented as evidence for TA-METHODOLOGIES.

   **Evidence**

   - Manual process documentation
   - References to methodologies applied as part of these processes
   - Results of applying the processes
   - Criteria used to confirm that the processes were applied correctly
   - Review records for results

   **Confidence scoring**

   Confidence scoring for TA-METHODOLOGIES is based on identifying areas of need for
   manual processes, assessing the clarity of proposed processes, analysing the
   results of their implementation, and evaluating the evidence of effectiveness
   in comparison to the analysed results

   **Checklist**

   - Are the identified gaps documented clearly to justify using a manual process?
   - Are the goals for each process clearly defined?
   - Is the sequence of procedures documented in an unambiguous manner?
   - Can improvements to the processes be suggested and implemented?
   - How frequently are processes changed?
   - How are changes to manual processes communicated?
   - Are there any exceptions to the processes?
   - How is evidence of process adherence recorded?
   - How is the effectiveness of the process evaluated?
   - Is ongoing training required to follow these processes?

.. assertion:: TA-CONFIDENCE
   :id: assertion__trust__ta-confidence
   :status: valid

   Confidence in XYZ is measured based on results of analysis

   **Guidance**

   To quantify confidence, either a subjective assessment or a statistical argument must be presented for each statement and then systematically and repeatably aggregated to assess whether the final deliverable is fit for purpose.

   To improve the accuracy of confidence evaluations in reflecting reality, the following steps are necessary:

   - Breaking down high-level claims into smaller, recursive requests.
   - Providing automated evaluations whenever possible, and using subjective assessments from appropriate parties when automation is not feasible.
   - Aggregating confidence scores from evidence nodes.
   - Continuously adjusting previous confidence measures based on new evidence, using previously established confidence values.

   As subjective assessments are progressively replaced with statistical arguments and past confidence evaluations are refined against new evidence, the accuracy of evaluations improves over time. When project circumstances inevitably change, existing statements are repurposed, with their associated confidence scores eventually offering insights into the systematic capability of the project to deliver according to set objectives. This process should itself be analysed to determine the maturity of any given confidence score. A suitable meta-analysis can assess long-term trends in score sourcing, score accumulation, and weighting mechanisms.

   **Evidence**

   - Confidence scores from other TA items

   **Confidence scoring**

   Confidence scoring for TA-CONFIDENCE is based on quality of the confidence
   scores given to Statements

   **Checklist**

   - What is the algorithm for combining/comparing the scores?
   - How confident are we that this algorithm is fit for purpose?
   - What are the trends for each score?
   - How well do our scores correlate with external feedback signals?
