..
   # *******************************************************************************
   # Copyright (c) 2026 Contributors to the Eclipse Foundation
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

.. raw:: html

   <script>document.body.classList.add("wide-content-page");</script>

Feature and Process Status
##########################

This page tracks the completion status of all 5 process areas per module.
Update the status column for each module after completing the respective deliverable.

**Process Status chart legend:**

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Process req. status
     - ISO 26262 std_req status
     - Req. verification status
   * - 🟢 Valid

       🟡 Draft

       🔴 Invalid

       ⬜ Other
     - 🟢 Ok

       🔵 Recommendation

       🟡 Open

       🟠 Action

       🔴 Deviation

       ⬜ N/A · ◻ Other
     - 🟢 Automated

       🟡 Waiting for automation

       🔵 Inspection list

       ⬜ Other

**Implementation Status Values:**

- ``✅ Available`` — Work product created, reviewed and approved
- ``🔄 NN%`` — In Progress: artifact exists with at least one valid element, percentage shows valid/total
- ``❌ Open`` — Not yet started, not found, or 0% valid
- ``—`` — Not applicable for this module

Process Area 1 — Change Management
***********************************

A Change Request must be created and approved by the Architecture Community before module
development begins.
See :ref:`chm_change_workflows`.

.. rubric:: Process Status

.. list-table::
   :header-rows: 1
   :class: compact-overview-table

   * - Process req. status
     - ISO 26262 std_req status
     - Req. verification status
   * -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Valid, Draft, Invalid, Other
          :colors: LimeGreen, Gold, LightCoral, LightGray

          type == 'gd_req' and is_external == False and status == 'valid' and 'change_management' in tags
          type == 'gd_req' and is_external == False and status == 'draft' and 'change_management' in tags
          type == 'gd_req' and is_external == False and status == 'invalid' and 'change_management' in tags
          type == 'gd_req' and is_external == False and status not in ['valid', 'draft', 'invalid'] and 'change_management' in tags
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Ok, Recommendation, Open, Action, Deviation, N/A, Other
          :colors: LimeGreen, LightBlue, Gold, Orange, LightCoral, LightGray, Silver
          :filter-func: needs_filters.std_req_status_for_area(change_management)
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Automated, Waiting for automation, Inspection list, Other
          :colors: LimeGreen, Gold, LightBlue, LightGray
          :filter-func: needs_filters.area_verification_status(change_management)

.. rubric:: Implementation status: ✅ Available (9/9 deliverables complete)

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :class: module-phase-tracker-table

   * - **Module**
     - **CR approved**

   * - Baselibs
     - ✅ Available

   * - Communication
     - ✅ Available

   * - Logging
     - ✅ Available

   * - Orchestrator
     - ✅ Available

   * - Persistency
     - ✅ Available

   * - Time
     - ✅ Available

   * - Config Mgmt
     - ✅ Available

   * - Lifecycle
     - ✅ Available

   * - Security/Crypto
     - ✅ Available

Process Area 2 — Requirements Engineering
*****************************************

Feature and component requirements must be written and inspected.
Work products: ``wp__requirements_feat``, ``wp__requirements_comp``, ``wp__requirements_inspect``.
See :ref:`requirements_workflows`.

.. rubric:: Process Status

.. list-table::
   :header-rows: 1
   :class: compact-overview-table

   * - Process req. status
     - ISO 26262 std_req status
     - Req. verification status
   * -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Valid, Draft, Invalid, Other
          :colors: LimeGreen, Gold, LightCoral, LightGray

          type == 'gd_req' and is_external == False and status == 'valid' and 'requirements_engineering' in tags
          type == 'gd_req' and is_external == False and status == 'draft' and 'requirements_engineering' in tags
          type == 'gd_req' and is_external == False and status == 'invalid' and 'requirements_engineering' in tags
          type == 'gd_req' and is_external == False and status not in ['valid', 'draft', 'invalid'] and 'requirements_engineering' in tags
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Ok, Recommendation, Open, Action, Deviation, N/A, Other
          :colors: LimeGreen, LightBlue, Gold, Orange, LightCoral, LightGray, Silver
          :filter-func: needs_filters.std_req_status_for_area(requirements_engineering)
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Automated, Waiting for automation, Inspection list, Other
          :colors: LimeGreen, Gold, LightBlue, LightGray
          :filter-func: needs_filters.area_verification_status(requirements_engineering)

.. rubric:: Implementation status: 🔄 22% (6/27 deliverables complete)

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :class: module-phase-tracker-table

   * - **Module**
     - **Feature Requirements**
     - **Component Requirements**
     - **Req. Inspection**

   * - Baselibs
     - 🔄 97% (37/38)
     - 🔄 92% (124/134)
     - 🔄 20% (2/10)

       | `bitmanipulation <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/bitmanipulation/docs/requirements/chklst_req_inspection.rst>`__
       | `concurrency <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/concurrency/docs/requirements/chklst_req_inspection.rst>`__
       | `containers <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/containers/docs/requirements/chklst_req_inspection.rst>`__
       | `filesystem <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/filesystem/docs/requirements/chklst_req_inspection.rst>`__
       | `json <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/json/docs/requirements/chklst_req_inspection.rst>`__
       | `safecpp <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/language/safecpp/docs/requirements/chklst_req_inspection.rst>`__
       | `result <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/result/docs/requirements/chklst_req_inspection.rst>`__
       | `srs <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/static_reflection_with_serialization/docs/requirements/chklst_req_inspection.rst>`__
       | `utils <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/utils/docs/requirements/chklst_req_inspection.rst>`__
       | `feature-level <https://github.com/eclipse-score/score/blob/main/docs/features/baselibs/docs/requirements/chklst_req_inspection.rst>`__

   * - Communication
     - ✅ Available (60/60)
     - 🔄 97% (34/35)
     - ❌ Open

   * - Logging
     - ✅ Available (46/46)
     - ❌ Open
     - ❌ Open

   * - Orchestrator
     - 🔄 83% (26/31)
     - 🔄 0% (0/2)
     - 🔄 0% (0/2)

       | `executor <https://github.com/eclipse-score/score/blob/main/docs/modules/orchestrator/executor/docs/requirements/chklst_req_inspection.rst>`__
       | `orchestrator <https://github.com/eclipse-score/score/blob/main/docs/modules/orchestrator/orchestrator/docs/requirements/chklst_req_inspection.rst>`__

   * - Persistency
     - ✅ Available (41/41)
     - 🔄 94% (36/38)
     - 🔄 50% (1/2)

       | `feature-level <https://github.com/eclipse-score/score/blob/main/docs/features/persistency/requirements/chklst_req_inspection.rst>`__
       | `kvs <https://github.com/eclipse-score/persistency/blob/main/docs/persistency/kvs/requirements/chklst_req_inspection.rst>`__

   * - Time
     - ✅ Available (15/15)
     - ❌ Open
     - ❌ Open

   * - Config Mgmt
     - ✅ Available (13/13)
     - ❌ Open
     - ❌ Open

   * - Lifecycle
     - 🔄 0% (0/92)

       | `requirements <https://github.com/eclipse-score/score/blob/main/docs/features/lifecycle/requirements/index.rst>`__
       | (all 92 entries ``:status: invalid``)
     - 🔄 0% (0/5)

       | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/main/docs/module/health_monitor/requirements/index.rst>`__
       | (template placeholder, ``:status: invalid``)
     - ❌ Open

   * - Security/Crypto
     - ✅ Available (42/42)
     - ❌ Open
     - ❌ Open

Process Area 3 — Architecture Design
************************************

Feature and component architecture must be designed and inspected.
Work products: ``wp__feature_arch``, ``wp__component_arch``, ``wp__sw_arch_verification``.
See :ref:`arch_workflow`.

.. rubric:: Process Status

.. list-table::
   :header-rows: 1
   :class: compact-overview-table

   * - Process req. status
     - ISO 26262 std_req status
     - Req. verification status
   * -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Valid, Draft, Invalid, Other
          :colors: LimeGreen, Gold, LightCoral, LightGray

          type == 'gd_req' and is_external == False and status == 'valid' and 'architecture_design' in tags
          type == 'gd_req' and is_external == False and status == 'draft' and 'architecture_design' in tags
          type == 'gd_req' and is_external == False and status == 'invalid' and 'architecture_design' in tags
          type == 'gd_req' and is_external == False and status not in ['valid', 'draft', 'invalid'] and 'architecture_design' in tags
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Ok, Recommendation, Open, Action, Deviation, N/A, Other
          :colors: LimeGreen, LightBlue, Gold, Orange, LightCoral, LightGray, Silver
          :filter-func: needs_filters.std_req_status_for_area(architecture_design)
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Automated, Waiting for automation, Inspection list, Other
          :colors: LimeGreen, Gold, LightBlue, LightGray
          :filter-func: needs_filters.area_verification_status(architecture_design)

.. rubric:: Implementation status: 🔄 22% (6/27 deliverables complete)

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :class: module-phase-tracker-table

   * - **Module**
     - **Feature Architecture**
     - **Component Architecture**
     - **Arch. Inspection**

   * - Baselibs
     - ✅ Available (4/4)
     - 🔄 98% (172/175)
     - 🔄 80% (8/10)

       | `bitmanipulation <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/bitmanipulation/docs/architecture/chklst_arc_inspection.rst>`__
       | `concurrency <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/concurrency/docs/architecture/chklst_arc_inspection.rst>`__
       | `containers <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/containers/docs/architecture/chklst_arc_inspection.rst>`__
       | `filesystem <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/filesystem/docs/architecture/chklst_arc_inspection.rst>`__
       | `json <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/json/docs/architecture/chklst_arc_inspection.rst>`__
       | `safecpp <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/language/safecpp/docs/architecture/chklst_arc_inspection.rst>`__
       | `result <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/result/docs/architecture/chklst_arc_inspection.rst>`__
       | `srs <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/static_reflection_with_serialization/docs/architecture/chklst_arc_inspection.rst>`__
       | `utils <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/utils/docs/architecture/chklst_arc_inspection.rst>`__
       | `feature-level <https://github.com/eclipse-score/score/blob/main/docs/features/baselibs/docs/architecture/chklst_arc_inspection.rst>`__

   * - Communication
     - ✅ Available (5/5)
     - 🔄 94% (17/18)
     - ❌ Open

   * - Logging
     - ✅ Available (4/4)
     - ✅ Available (3/3)
     - ❌ Open

   * - Orchestrator
     - 🔄 66% (4/6)
     - ✅ Available (27/27)
     - 🔄 0% (0/2)

       | `executor <https://github.com/eclipse-score/score/blob/main/docs/modules/orchestrator/executor/docs/architecture/chklst_arc_inspection.rst>`__
       | `orchestrator <https://github.com/eclipse-score/score/blob/main/docs/modules/orchestrator/orchestrator/docs/architecture/chklst_arc_inspection.rst>`__

   * - Persistency
     - ✅ Available (12/12)
     - 🔄 25% (1/4)
     - 🔄 0% (0/2)

       | `feature-level <https://github.com/eclipse-score/score/blob/main/docs/features/persistency/architecture/chklst_arc_inspection.rst>`__
       | `kvs <https://github.com/eclipse-score/persistency/blob/main/docs/persistency/kvs/architecture/chklst_arc_inspection.rst>`__

   * - Time
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Config Mgmt
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Lifecycle
     - 🔄 93% (30/32)
     - 🔄 93% (15/16)
     - ❌ Open

   * - Security/Crypto
     - ❌ Open
     - ❌ Open
     - ❌ Open

Process Area 4 — Implementation
********************************

Source code and detailed design must be implemented and inspected.
Work products: ``wp__sw_development_plan``, ``wp__sw_implementation``, ``wp__sw_implementation_inspection``.
See :ref:`workflow_implementation`.

.. rubric:: Process Status

.. list-table::
   :header-rows: 1
   :class: compact-overview-table

   * - Process req. status
     - ISO 26262 std_req status
     - Req. verification status
   * -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Valid, Draft, Invalid, Other
          :colors: LimeGreen, Gold, LightCoral, LightGray

          type == 'gd_req' and is_external == False and status == 'valid' and 'implementation' in tags
          type == 'gd_req' and is_external == False and status == 'draft' and 'implementation' in tags
          type == 'gd_req' and is_external == False and status == 'invalid' and 'implementation' in tags
          type == 'gd_req' and is_external == False and status not in ['valid', 'draft', 'invalid'] and 'implementation' in tags
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Ok, Recommendation, Open, Action, Deviation, N/A, Other
          :colors: LimeGreen, LightBlue, Gold, Orange, LightCoral, LightGray, Silver
          :filter-func: needs_filters.std_req_status_for_area(implementation)
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Automated, Waiting for automation, Inspection list, Other
          :colors: LimeGreen, Gold, LightBlue, LightGray
          :filter-func: needs_filters.area_verification_status(implementation)

.. rubric:: Implementation status: 🔄 47% (17/36 deliverables complete)

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :class: module-phase-tracker-table

   * - **Module**
     - **SW Development Plan**
     - **Code**
     - **Detailed Design**
     - **Impl. Inspection**

   * - Baselibs
     - ✅ Available
     - ✅ Available (~119,400 LOC) `baselibs <https://github.com/eclipse-score/baselibs>`__
     - ❌ Open
     - 🔄 0% (0/9)

       | `bitmanipulation <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/bitmanipulation/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `concurrency <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/concurrency/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `containers <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/containers/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `filesystem <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/filesystem/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `json <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/json/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `safecpp <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/language/safecpp/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `result <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/result/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `srs <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/static_reflection_with_serialization/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `utils <https://github.com/eclipse-score/score/blob/main/docs/modules/baselibs/utils/docs/detailed_design/chklst_impl_inspection.rst>`__

   * - Communication
     - ✅ Available
     - ✅ Available (~71,300 LOC) `communication <https://github.com/eclipse-score/communication>`__
     - ❌ Open
     - ❌ Open

   * - Logging
     - ✅ Available
     - ✅ Available (~22,900 LOC) `logging <https://github.com/eclipse-score/logging>`__
     - ❌ Open
     - ❌ Open

   * - Orchestrator
     - ✅ Available
     - ✅ Available (~38,300 LOC) `orchestrator <https://github.com/eclipse-score/orchestrator>`__
     - ❌ Open
     - ❌ Open

   * - Persistency
     - ✅ Available
     - ✅ Available (~8,700 LOC) `persistency <https://github.com/eclipse-score/persistency>`__
     - ❌ Open
     - 🔄 0% (0/1)

       | `kvs <https://github.com/eclipse-score/persistency/blob/main/docs/persistency/kvs/detailed_design/chklst_impl_inspection.rst>`__

   * - Time
     - ✅ Available
     - ✅ Available (~11,700 LOC) `inc_time <https://github.com/eclipse-score/inc_time>`__
     - ❌ Open
     - ❌ Open

   * - Config Mgmt
     - ✅ Available
     - ✅ Available (~5,400 LOC) `config_management <https://github.com/eclipse-score/config_management>`__
     - ❌ Open
     - ❌ Open

   * - Lifecycle
     - ✅ Available
     - ✅ Available (~38,300 LOC) `lifecycle <https://github.com/eclipse-score/lifecycle>`__
     - 🔄 50% (1/2)
     - ❌ Open

   * - Security/Crypto
     - ✅ Available
     - ❌ Open
     - ❌ Open
     - ❌ Open

Process Area 5 — Verification
*****************************

All tests must be implemented and a module verification report must be approved.
Work products: ``wp__verification_sw_unit_test``, ``wp__verification_comp_int_test``, ``wp__verification_feat_int_test``, ``wp__verification_module_ver_report``.
See :ref:`verification_workflows`.

.. rubric:: Process Status

.. list-table::
   :header-rows: 1
   :class: compact-overview-table

   * - Process req. status
     - ISO 26262 std_req status
     - Req. verification status
   * -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Valid, Draft, Invalid, Other
          :colors: LimeGreen, Gold, LightCoral, LightGray

          type == 'gd_req' and is_external == False and status == 'valid' and 'verification' in tags
          type == 'gd_req' and is_external == False and status == 'draft' and 'verification' in tags
          type == 'gd_req' and is_external == False and status == 'invalid' and 'verification' in tags
          type == 'gd_req' and is_external == False and status not in ['valid', 'draft', 'invalid'] and 'verification' in tags
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Ok, Recommendation, Open, Action, Deviation, N/A, Other
          :colors: LimeGreen, LightBlue, Gold, Orange, LightCoral, LightGray, Silver
          :filter-func: needs_filters.std_req_status_for_area(verification)
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Automated, Waiting for automation, Inspection list, Other
          :colors: LimeGreen, Gold, LightBlue, LightGray
          :filter-func: needs_filters.area_verification_status(verification)

.. note::

   **C0/C1 Coverage** data is sourced from the `reference_integration <https://github.com/eclipse-score/reference_integration>`__
   CI (``Code Quality & Documentation`` workflow, ``bazel coverage --config=ferrocene-coverage``).
   C0 = line coverage, C1 = branch coverage. Rust coverage reports line coverage only.
   Modules not yet integrated into the reference_integration CI (Time, Config Mgmt) or with
   disabled coverage extraction (Orchestrator) show ❌ Open.

.. note::

   **Static Code Analysis** is tracked per module via dedicated CI workflows (clang-tidy for C++,
   Rust Clippy for Rust). All listed workflows are zero-tolerance (CI fails on any finding),
   so a passing ``main`` branch implies **0 open findings**. Additionally,
   `CodeQL <https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/codeql-multiple-repo-scan.yml>`__
   runs centrally across all pinned repositories in ``reference_integration``
   (finding counts require the GitHub Security tab).

   **Dynamic Code Analysis** is tracked via sanitizer CI workflows (ASan/UBSan/LSan via
   ``--config=asan_ubsan_lsan``, TSan via ``--config=tsan``). All listed workflows are
   zero-tolerance, so a passing ``main`` branch implies **0 sanitizer findings**.

.. rubric:: Implementation status: 🔄 37% (23/63 deliverables complete)

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :class: module-phase-tracker-table

   * - **Module**
     - **Unit Tests**
     - **C0/C1 Coverage**
     - **Comp. Integration Tests**
     - **Feature Integration Tests**
     - **Static Code Analysis**
     - **Dynamic Code Analysis**
     - | **Module Verification**
       | **Report**

   * - Baselibs
     - ✅ Available

       | (4,663 tests)
     - 🔄 **C0:** 92.3%

       | **C1:** 60.3% (cpp)
       | **Rust line:** 74.4%
     - ✅ Available

       | (13 tests)
     - ❌ Open
     - ✅ 0 findings

       | `clang-tidy <https://github.com/eclipse-score/baselibs/blob/main/.github/workflows/lint.yml>`__
     - ✅ 0 findings

       | `ASan/UBSan/LSan <https://github.com/eclipse-score/baselibs/blob/main/.github/workflows/sanitizers_linux.yml>`__
     - ❌ Open

   * - Communication
     - ✅ Available

       | (2,374 tests)
     - 🔄 **C0:** 87.9%

       | **C1:** 58.8% (cpp)
     - ✅ Available

       | (42 tests)
     - ❌ Open
     - 🔄 Configured

       | `clang-tidy <https://github.com/eclipse-score/communication/blob/main/quality/static_analysis/static_analysis.bazelrc>`__
       | `CodeQL/MISRA <https://github.com/eclipse-score/communication/tree/main/quality/static_analysis>`__
       | but no CI enforcement workflow yet
     - ✅ 0 findings

       | `ASan/UBSan/LSan <https://github.com/eclipse-score/communication/blob/main/.github/workflows/address_undefined_behavior_leak_sanitizer.yml>`__
       | `TSan <https://github.com/eclipse-score/communication/blob/main/.github/workflows/thread_sanitizer.yml>`__
     - ❌ Open

   * - Logging
     - ✅ Available

       | (619 tests)
     - 🔄 **C0:** 79.5%

       | **C1:** 42.4% (cpp)
       | **Rust line:** 39.9%
     - ❌ Open
     - ✅ Available (1 test)

       | `reference_integration <https://github.com/eclipse-score/reference_integration>`__ (cross-module)
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Orchestrator
     - ✅ Available

       | (2 tests)
     - ❌ Open
     - ✅ Available

       | (9 tests)
     - ✅ Available (3 tests)

       | `reference_integration <https://github.com/eclipse-score/reference_integration>`__ (cross-module)
     - ✅ 0 findings

       | `Clippy <https://github.com/eclipse-score/orchestrator/blob/main/.github/workflows/clippy.yml>`__
     - ❌ Open
     - ❌ Open

   * - Persistency
     - ✅ Available

       | (138 tests)
     - 🔄 **C0:** 94.7%

       | **C1:** 63.0% (cpp)
       | **Rust line:** 92.7%
     - ❌ Open
     - ✅ Available (6 tests)

       | `reference_integration <https://github.com/eclipse-score/reference_integration>`__ (cross-module)
     - ✅ 0 findings

       | `Clippy <https://github.com/eclipse-score/persistency/blob/main/.github/workflows/clippy.yml>`__
     - ❌ Open
     - ❌ Open

   * - Time
     - ✅ Available

       | (296 tests)
     - ❌ Open
     - ✅ Available

       | (11 tests)
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Config Mgmt
     - ✅ Available

       | (143 tests)
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ✅ 0 findings

       | `clang-tidy <https://github.com/eclipse-score/config_management/blob/main/.github/workflows/static-analysis.yml>`__
     - ❌ Open
     - ❌ Open

   * - Lifecycle
     - ✅ Available

       | (2 tests)
     - 🔄 **C0:** 77.2%

       | **C1:** 45.8% (cpp)
       | **Rust line:** 53.8%
     - ✅ Available

       | (9 tests)
     - ❌ Open
     - ✅ 0 findings

       | `Clippy <https://github.com/eclipse-score/lifecycle/blob/main/.github/workflows/lint_clippy.yml>`__
     - ❌ Open
     - ❌ Open

   * - Security/Crypto
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open

Done Criteria
*************

A module is considered **complete** when all of the following are true:

#. All ``valid`` component requirements have **100% test coverage** (linked via ``FullyVerifies`` or ``PartiallyVerifies``).
#. All CI metadata checks pass (``TestType``, ``DerivationTechnique``, ``Description`` set on every test).
#. Static analysis has no open ``Critical`` or ``High`` findings.
#. The **Module Verification Report** (``wp__verification_module_ver_report``) is generated and approved by a Committer.
