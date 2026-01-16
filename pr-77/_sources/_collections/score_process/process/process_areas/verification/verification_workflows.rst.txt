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

.. _verification_workflows:

Verification Workflows
######################

For a detailed explanation of workflows and their role within the process model, please refer to the :ref:`processes_introduction`.

.. workflow:: Create/Perform Unit Test
   :id: wf__verification_unit_test
   :status: valid
   :tags: implementation
   :responsible: rl__contributor
   :approved_by: rl__committer
   :supported_by: rl__safety_manager
   :input: wp__sw_implementation, wp__verification_plan
   :output: wp__verification_sw_unit_test
   :contains: gd_req__verification_link_tests, gd_req__verification_link_tests_cpp, gd_req__verification_link_tests_python, gd_req__verification_link_tests_rust, gd_req__verification_independence
   :has: doc_concept__verification_process, doc_getstrt__verification_process,
         doc_concept__imp_concept, doc_getstrt__imp_getstrt

   Every Unit shall have at least one Unit Test. They verify the detailed design of the implementation.
   Unit tests are automatically executed as part of the CI after PR merge.
   In case of changes at inputs, the workflow need to be executed again as part of maintenance.
   Any contributor can create a component test and create a PR for it.
   During the review process the test cases will be approved by a committer.
   Committer and contributor need to differ.
   The actual :need:`rl__committer` of the implementation can also be the creator of the unit tests.
   Independence is achieved by different approver at PRs and by the :need:`wp__verification_module_ver_report`.

   The typical steps when creating a unit tests are:

   #. Check the detailed design of the component. Create a test for every interface of the unit
      showing at least every flow in dynamic diagrams.
   #. Follow the detailed design to the component requirements and test these requirements.
   #. Fill in the test attributes based on the previous steps and provide a description.
   #. Link the test against detailed design or component requirement.

.. workflow:: Create/Maintain Component Integration Test
   :id: wf__verification_comp_int_test
   :status: valid
   :tags: verification
   :responsible: rl__contributor
   :approved_by: rl__committer, rl__testing_community
   :supported_by: rl__safety_manager
   :input: wp__component_arch, wp__sw_implementation, wp__requirements_comp, wp__requirements_comp_aou, wp__verification_plan
   :output: wp__verification_comp_int_test
   :contains: gd_req__verification_link_tests, gd_req__verification_link_tests_cpp, gd_req__verification_link_tests_python, gd_req__verification_link_tests_rust, gd_req__verification_independence, gd_guidl__verification_specification
   :has: doc_concept__verification_process, doc_getstrt__verification_process

   Component Integration test cases are based on component architecture and component requirements.
   They also cover the detailed design and integration of units forming a component.
   The integration testing of component architecture is optional in case a component is standalone
   and has no (sub-)components.
   Any contributor can create a component integration test and create a PR for it.
   During the review process the test cases will be approved by a committer.
   Committer and contributor need to differ.
   The tests are automatically executed as part of the CI after PR merge.
   In case of changes at inputs, the workflow need to be executed again as part of maintenance.


.. workflow:: Create/Maintain Feature Integration Test
   :id: wf__verification_feat_int_test
   :status: valid
   :tags: verification
   :responsible: rl__contributor
   :approved_by: rl__committer, rl__testing_community
   :supported_by: rl__safety_manager
   :input: wp__feature_arch, wp__requirements_feat, wp__requirements_feat_aou,
           wp__verification_plan
   :output: wp__verification_feat_int_test
   :contains: gd_req__verification_link_tests, gd_req__verification_link_tests_cpp, gd_req__verification_link_tests_python, gd_req__verification_link_tests_rust, gd_req__verification_independence, gd_guidl__verification_specification
   :has: doc_concept__verification_process, doc_getstrt__verification_process

   Feature Integration test cases are based on feature requirements and architecture of a specific feature.
   Any contributor can create a feature integration test and create a PR for it.
   During the review process the test cases will be approved by a committer.
   Committer and contributor need to differ.
   The tests are automatically executed as part of the CI after PR merge.
   In case of changes at inputs, the workflow need to be executed again as part of maintenance.

.. workflow:: Create/Maintain Platform Integration Test
   :id: wf__verification_platform_int_test
   :status: valid
   :tags: verification
   :responsible: rl__contributor
   :approved_by: rl__committer, rl__testing_community
   :supported_by: rl__safety_manager
   :input: wp__requirements_stkh, wp__verification_plan
   :output: wp__verification_platform_int_test
   :contains: gd_req__verification_link_tests, gd_req__verification_link_tests_cpp, gd_req__verification_link_tests_python, gd_req__verification_link_tests_rust, gd_req__verification_independence, gd_guidl__verification_specification
   :has: doc_concept__verification_process, doc_getstrt__verification_process

   Platform Integration Test cases are based on Stakeholder requirements. This is the highest test level.
   Any contributor can create a platform integration test and create a PR for it.
   During the review process the test cases will be approved by a committer.
   Committer and contributor need to differ.
   The tests are automatically executed as part of the CI after PR merge.
   In case of changes at inputs, the workflow need to be executed again as part of maintenance.

.. workflow:: Create Verification Plan
   :id: wf__verification_plan
   :status: valid
   :tags: verification
   :responsible: rl__committer, rl__testing_community
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__infrastructure_tooling_community
   :input: wp__requirements_stkh, wp__platform_mgmt, wp__tool_verification_report
   :output: wp__verification_plan
   :contains: gd_guidl__verification_guide, gd_temp__verification_plan
   :has: doc_concept__verification_process, doc_getstrt__verification_process

   The verification plan is created by :need:`rl__committer`. It clearly
   outlines all aspects of the verification activities, provide a roadmap for the verification
   efforts throughout the software development lifecycle. The plan should be dynamic and updated
   as needed throughout the project lifecycle by :need:`wf__verification_plan_maintain`.

.. workflow:: Maintain Verification Plan
   :id: wf__verification_plan_maintain
   :status: valid
   :tags: verification
   :responsible: rl__committer, rl__testing_community
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__infrastructure_tooling_community
   :input: wp__verification_plan, wp__requirements_stkh, wp__platform_mgmt,
           wp__feature_arch, wp__requirements_feat, wp__requirements_feat_aou,
           wp__component_arch, wp__requirements_comp, wp__requirements_comp_aou,
           wp__tool_verification_report
   :output: wp__verification_plan
   :contains: gd_guidl__verification_guide, gd_temp__verification_plan
   :has: doc_concept__verification_process, doc_getstrt__verification_process

   The verification plan is maintained by :need:`rl__committer`. The plan should be dynamic and updated
   as needed throughout the project lifecycle, as verification activities may be impacted, by new
   requirements, architectural decisions, introduction of tools.

   Note that during the initial creation of the verification plan in :need:`wf__verification_plan`
   not every input down to component level may be available.

.. workflow:: Create Module Verification Report
   :id: wf__verification_mod_ver_report
   :status: valid
   :tags: verification
   :responsible: rl__committer, rl__testing_community
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__infrastructure_tooling_community, rl__contributor
   :input: wp__verification_plan, wp__requirements_comp, wp__requirements_comp_aou,
           wp__component_arch, wp__module_sw_release_note, wp__platform_mgmt,
           wp__sw_component_fmea, wp__sw_component_dfa,
           wp__sw_arch_verification, wp__sw_implementation_inspection, wp__requirements_inspect,
           wp__verification_comp_int_test, wp__verification_sw_unit_test
   :output: wp__verification_module_ver_report
   :contains: gd_temp__mod_ver_report
   :has: doc_concept__verification_process, doc_getstrt__verification_process

   The verification report is created and maintained by a :need:`rl__committer`.
   It is based on the :need:`wp__verification_plan` and covers all the components of a developed module.
   This includes their requirements, AoUs, Architecture, Detailed Design, Units, DFA, Safety Analyses,
   Unit Code coverage. The respective necessary test methods and rigor of their application is
   defined in the :need:`wp__verification_plan`.

   In case of externally provided pre-existing software maintained outside of the project,
   the Module Verification Report also applies as documentation for the Qualification Verification
   Report. The respective component(s) are verified with the same methods and deviation techniques
   as mentioned in the :need:`wp__verification_plan`. The report will be filled by the :need:`rl__committer`
   responsible for integration of the external component and will get support by the :need:`rl__contributor`
   who proposed the component to the added to the project scope.

   The report is valid for ONE version of a module.

.. workflow:: Create Platform Verification Report
   :id: wf__verification_platform_ver_report
   :status: valid
   :tags: verification
   :responsible: rl__committer, rl__testing_community
   :approved_by: rl__project_lead
   :supported_by: rl__safety_manager, rl__infrastructure_tooling_community
   :input: wp__verification_plan, wp__requirements_stkh, wp__requirements_feat, wp__requirements_feat_aou,
           wp__feature_arch, wp__platform_sw_release_note, wp__platform_mgmt,
           wp__feature_fmea, wp__feature_dfa, wp__platform_dfa,
           wp__sw_arch_verification, wp__requirements_inspect,
           wp__verification_feat_int_test, wp__verification_platform_int_test
   :output: wp__verification_platform_ver_report
   :contains: gd_temp__platform_ver_report
   :has: doc_concept__verification_process, doc_getstrt__verification_process

   The verification report is created and maintained by a :need:`rl__committer`.
   It is based on the :need:`wp__verification_plan` and covers all the selected features of a SW platform.
   This includes their requirements, AoUs, Architecture, DFA, Safety Analyses,
   The respective necessary test methods and rigor of their application is
   defined in the :need:`wp__verification_plan` and :need:`wp__platform_mgmt`.

   The report is valid for ONE specific platform version baseline.

RAS(IC) for Verification:
*************************

.. needtable:: RASIC Overview for Problem Resolution
   :tags: verification_process
   :filter: "verification_process" in tags and type == "workflow" and is_external == False
   :style: table
   :sort: status
   :columns: id as "Activity";responsible as "Responsible";approved_by as "Approver";supported_by as "Supporter"
   :colwidths: 30,30,30,30
