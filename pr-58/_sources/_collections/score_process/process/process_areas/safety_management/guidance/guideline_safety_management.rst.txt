..
   # *******************************************************************************
   # Copyright (c) 2025 Contributors to the Eclipse Foundation
   #
   # See the NOTICE file(s) distributed with this work for additional
   # information regarding copyright ownership.
   #
   # This program and the accompanying materials are made available under the
   # terms of the Apache License Version 2.0 which is available at
   # https://www.apache.org/licenses/LICENSE-2.0
   #
   # SPDX-License-Identifier: Apache-2.0
   # *******************************************************************************

.. _guideline_safety_management:

Safety Management Guideline
===========================

.. gd_guidl:: Safety plan definitions
   :id: gd_guidl__saf_plan_definitions
   :status: valid
   :complies: std_req__iso26262__management_5426, std_req__iso26262__management_6465, std_req__iso26262__management_6466, std_req__iso26262__management_6467, std_req__iso26262__management_6468, std_req__iso26262__management_6469, std_req__iso26262__management_6422, std_req__iso26262__management_6423, std_req__iso26262__management_6424, std_req__iso26262__management_6451, std_req__iso26262__management_6452, std_req__iso26262__management_6453, std_req__iso26262__management_6454, std_req__iso26262__management_6455, std_req__iso26262__management_6456, std_req__iso26262__management_6457, std_req__iso26262__management_6461, std_req__iso26262__management_6462, std_req__iso26262__management_6463, std_req__iso26262__management_64610, std_req__iso26262__management_6472, std_req__iso26262__management_6471, std_req__iso26262__management_64111, std_req__iso26262__management_64112, std_req__iso26262__management_64113, std_req__iso26262__management_64114, std_req__iso26262__management_64121, std_req__iso26262__management_64122, std_req__iso26262__management_64123, std_req__iso26262__management_64124, std_req__iso26262__management_64125, std_req__iso26262__management_64126, std_req__iso26262__management_64127, std_req__iso26262__management_64128, std_req__iso26262__management_6431, std_req__iso26262__management_6432, std_req__iso26262__management_6433, std_req__iso26262__management_6454, std_req__iso26262__management_64129, std_req__iso26262__management_641210, std_req__iso26262__management_641211, std_req__iso26262__management_641212, std_req__iso26262__management_641213, std_req__iso26262__software_747, std_req__iso26262__software_1046, std_req__iso26262__software_1144, std_req__iso26262__support_8441, std_req__iso26262__management_5424, std_req__iso26262__management_5427, std_req__iso26262__management_5432, std_req__iso26262__management_5441, std_req__iso26262__management_5424, std_req__iso26262__management_5427, std_req__iso26262__management_5461

   **Safety culture:**

   Safety culture is planned to grow in the SW platform. This shall be fostered by doing a lessons learned after each feature development completion, using the ISO 26262-2 Table B.1 as a questionnaire.
   This lessons learned is the main input for process improvement managed by :need:`wp__process_impr_report`
   As starting point for safety culture we define a Committer selection process to already have professionals with safety experience in the teams.

   Additionally the SW platform's processes are defined with experience of several companies already performing successful safe SW development. This also improves independence of reviews for the process definitions.

   **Quality Management:**

   ASPICE standard is selected for quality management. Processes will always link to the :ref:`standard_iso26262` standard and to the :ref:`ASPICE PAM4 <standard_aspice_pam4>` standard.

   **Competence management:**
   
   The :need:`rl__project_lead` on SW platform level is responsible to define a competence management for the whole platform.
   Expectation is that the safety competence of the persons nominated for the roles is already given and only has to be checked.
   The exception from this are the committers, for these no safety competence needs to be enforced.
   So the module safety managers shall consult the :need:`module safety plan <wp__module_safety_plan>` and perform accordingly in their module project.

   **Communication:**

   Development teams are interdisciplinary, so the regular planning and review meetings enable communication (as defined in in the project specific :need:`project management plan <wp__project_mgt>`). Another main communication means are the Pull Request reviews.
   Also the standard Eclipse Foundation communication strategies are used (e.g. mailing lists)

   **Safety anomalies:**

   As the SW platform organization does not have own vehicles in the field, it relies on feedback from OEMs and Distributors on bugs discovered in the field. The need for this feedback is part of each safety manual.
   But also during development of change requests to existing features, bug reporting by the Open Source community or integration of existing SW components into new features may lead to the discovery of new safety anomalies.
   Safety anomalies can also be deviations from the development process with impact on safety.
   If these are known at the time of creation of a release they will be part of the :need:`wp__module_safety_package` or :need:`wp__platform_safety_package` for the SEooC.
   Safety anomalies relevant for already delivered releases will be identified as such and communicated (as defined in Problem Resolution part of :need:`wp__platform_mgmt`) via the :need:`wp__issue_track_system` (which is also Open Source).

   **Tailoring Safety Activities:**

   The software platform is developed purely as software and provided as a Safety Element out of Context (SEooC). That is why only software relevant parts of :ref:`standard_iso26262` are used.
   This requires a generic, platform-wide approach to tailoring so that safety processes remain efficient, relevant, and compliant with the software relevant ISO 26262.
   Before any tailoring is performed, an **impact analysis** must be conducted in accordance with ISO 26262. This analysis is performed on element level, not on the item level as previously stated.
   This analysis determines whether the element is a new development, a modification, or an existing element with a modified environment. The results guide the extent and nature of any tailoring.

   If tailoring is necessary, it must be justified and documented. The rationale should demonstrate that the tailored approach is sufficient to achieve the required level of functional safety. Tailoring may be driven by factors such as:

   - Qualification of software components,
   - Confidence in the use of software tools.

   Note: Proven-in-use arguments are generally not applicable for a reusable SEooC platform intended for integration into various target applications and environments.

   For the software platform as a whole, tailoring is achieved by clearly defining which work products are relevant and providing a reasoned argument for omitting others. This is documented in the platform safety plan and the ISO 26262 reference documentation.

   Additional tailoring may apply at the module or feature level, particularly for SEooC developments where reuse of existing qualified components is the main driver. Such tailoring is documented in the respective module safety plans.

   When safety activities are tailored because an element is developed as SEooC:
   a) The SEooC development must be based on a requirements specification derived from well-defined assumptions about its intended use and context, including all relevant external interfaces.
   b) These assumptions must be validated when the SEooC is integrated into its target application.

   This approach ensures that safety activities are focused, efficient, and appropriate to the context of a reusable software platform, while maintaining compliance with ISO 26262 requirements and intent.

   **Planning safety activities:**

   In the safety plan the nomination of the safety manager and the project manager is documented.
   The planning of safety activities is done using issues in the :need:`wp__issue_track_system` as specified in the :need:`wp__platform_mgmt`
   It contains for each issue:

   * objective - as part of the issue description
   * dependencies on other activities or information - by links to the respective issues
   * responsible person for the activity - as issue assignee
   * required resources for the activity - by selecting a team label (or "project") pointing to a team of committers dedicated to the issue resolution
   * duration in time, including start and end point - by selecting a milestone
   * UID of the resulting work products - stated in the issue title

   The planning of safety activities is divided into the

   * platform SEooC planning, dealing with all work products needed only once for the platform. This is included in :need:`wp__platform_safety_plan`
   * module SEooC planning, dealing with all work products needed for each module development (initiated by a change request), included in :need:`wp__module_safety_plan`. This module safety planning also includes the planning of OSS component qualification based on :need:`gd_guidl__component_classification`.

   A template exists to guide this: :need:`gd_temp__module_safety_plan`.

   **Planning supporting processes:**

   Supporting processes (Requirements Management, Configuration Management, Change Management, Documentation Management, Tool Management) are planned within the :need:`wp__platform_mgmt`

   **Planning integration and verification:**

   Integration on the target hardware is not done in the scope of the SW platform project, but SW/SW integration up to the feature level is performed and its test results are part of the :need:`wp__verification_platform_ver_report`.

   The integration on the target hardware done by the user is supported by delivering a set of SW integration tests which were already run successfully on a reference HW platform.
   This is planned by the respective work products:

   * :need:`wp__verification_feat_int_test`
   * :need:`wp__verification_platform_int_test`

   Verification planning is documented in :need:`wp__verification_plan`
   Any unspecified functions, such as code for debugging or instrumentation, must either be deactivated or removed prior to release, unless their presence does not affect safety compliance.

   **Scheduling of formal document reviews, audit and assessment:**

   Scheduling is done in the same way as for all work products definition by issues. The respective work products are :need:`wp__fdr_reports` and  :need:`wp__audit_report`
   A person responsible for carrying out the functional safety audit shall be appointed as part of the scheduling process. This person has to have the required skillset and knowledge.
   The functional safety auditor may appoint one or more assistants to support the audit.
   These assistants may not be fully independent from the developers of the relevant item, elements, or work products, but must possess at least a basic level of independence.
   The assessor is responsible for appraising the input from any assistants to ensure that the assessment remains objective and that an unbiased opinion is provided.
   The planning and follow-up of the audit or assessment shall also take into account the type of report to be issued—whether it is an acceptance, conditional acceptance (with required corrective actions and conditions for acceptance), or a rejection.
   Any conditions or corrective actions identified in the report must be addressed and tracked to completion as part of the Safety Management process.

   **Planning of dependent failures and safety analyses:**

   In cases where the components consist of sub-components there will be more than one architecture level. DFA and Safety analysis will then be done on these multiple levels. See the respective work products:

   * feature level: :need:`wp__feature_fmea` and :need:`wp__feature_dfa`
   * component level: :need:`wp__sw_component_fmea` and :need:`wp__sw_component_dfa`

   **Provision of the confidence in the use of software tools:**

   Tool Management planning is part of the :need:`wp__platform_mgmt`. The respective work product to be planned as an issue  of the generic safety plan is the :need:`wp__tool_verification_report`, which contains tool evaluation and if applicable qualification of the SW platform toolchain.
   Components developed in different programming languages will have different toolchains. They will be qualified once for the SW platform.

   **(OSS) Component qualification planning:**

   Based on the component classification as described in :need:`gd_guidl__component_classification`,
   the qualification of the component is planned as part of the :need:`gd_temp__module_safety_plan`.
   The template contains guidance how to do this and to document in the "OSS (sub-)component <name> Workproducts" list.


.. gd_guidl:: Safety manual generation
   :id: gd_guidl__saf_man
   :status: valid
   :complies: std_req__iso26262__system_6411, std_req__iso26262__system_6412, std_req__iso26262__system_6413, std_req__iso26262__system_6414, std_req__iso26262__system_6421, std_req__iso26262__system_6422, std_req__iso26262__software_641, std_req__iso26262__software_642, std_req__iso26262__software_645, std_req__iso26262__support_12421

   | The safety manual collects several workproducts and adds some additional content mainly to instruct the user of
   | a SEooC (in this project on platform and module level) to safely use it in the context of the user's own safety
   | element.
   | Its main content is described in :need:`wp__platform_safety_manual` and :need:`wp__module_safety_manual`
   | A template exists to guide the definition of the safety manual on platform and module level (:need:`gd_temp__safety_manual`).

.. gd_guidl:: Safety package automated generation
   :id: gd_guidl__saf_package
   :status: valid
   :complies: std_req__iso26262__management_6481, std_req__iso26262__management_6482

   | The safety package shall be generated progressively and automatically compiling the work products.
   | One of the checks to perform on the platform safety package is to check completeness of the
   | process compliance to standards, which can be seen from standard linkage charts in :ref:`external_standards`.
