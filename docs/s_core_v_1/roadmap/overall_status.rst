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

Overall Status
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

.. rubric:: Implementation status: 🔄 91% (10/11 deliverables complete)

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

   * - Diagnostic Services
     - ✅ Available

   * - NM
     - ❌ Open

   * - Some/IP
     - ✅ Available

.. _overall_status_pa2:

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

.. rubric:: Implementation status: 🔄 42% (14/33 deliverables complete)

.. figure:: /_assets/pa2_impl_progress.svg
   :alt: Total Feature and Component Requirements across PA2 modules per release
   :width: 720px

   Total Feature and Component Requirements across all PA2 modules per release
   (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :class: module-phase-tracker-table

   * - **Module**
     - **Feature Requirements**
     - **Component Requirements**
     - **Req. Inspection**

   * - Baselibs
     - ✅ Available (37/37)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/baselibs/docs/requirements/index.rst>`__
       | `abi-compatible-data-types <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/baselibs/abi_compatible_data_types/requirements.rst>`__
     - ✅ Available (84/84 comp_req + 32/32 AoU)

       | `bitmanipulation <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/bitmanipulation/docs/requirements/index.rst>`__
       | `concurrency <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/concurrency/docs/requirements/index.rst>`__
       | `containers <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/containers/docs/requirements/index.rst>`__
       | `filesystem <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/filesystem/docs/requirements/index.rst>`__
       | `flatbuffers <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/flatbuffers/docs/requirements/index.rst>`__
       | `json <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/json/docs/requirements/index.rst>`__
       | `safecpp <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/language/safecpp/docs/requirements/index.rst>`__
       | `memory_shared <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/memory_shared/docs/requirements/index.rst>`__
       | `result <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/result/docs/requirements/index.rst>`__
       | `srs <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/static_reflection_with_serialization/docs/requirements/index.rst>`__
       | `utils <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/utils/docs/requirements/index.rst>`__
     - 🔄 20% (2/10)

       | `bitmanipulation <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/bitmanipulation/docs/requirements/chklst_req_inspection.rst>`__
       | `concurrency <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/concurrency/docs/requirements/chklst_req_inspection.rst>`__
       | `containers <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/containers/docs/requirements/chklst_req_inspection.rst>`__
       | `filesystem <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/filesystem/docs/requirements/chklst_req_inspection.rst>`__
       | `json <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/json/docs/requirements/chklst_req_inspection.rst>`__
       | `safecpp <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/language/safecpp/docs/requirements/chklst_req_inspection.rst>`__
       | `result <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/result/docs/requirements/chklst_req_inspection.rst>`__
       | `srs <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/static_reflection_with_serialization/docs/requirements/chklst_req_inspection.rst>`__
       | `utils <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/utils/docs/requirements/chklst_req_inspection.rst>`__
       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/baselibs/docs/requirements/chklst_req_inspection.rst>`__

   * - Communication
     - ✅ Available (58/58)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/communication/docs/requirements/index.rst>`__
       | `ipc <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/communication/ipc/docs/requirements/index.rst>`__
       | `some_ip_gateway <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/communication/some_ip_gateway/requirements/index.rst>`__
     - ✅ Available (0/0 comp_req [TRLC] + 33/33 AoU)

       | `aou_req (RST) <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/communication/docs/requirements/aou_req.rst>`__
       | (real component requirements maintained in TRLC: `component_requirements_ipc.trlc <https://github.com/eclipse-score/communication/blob/b021eccf1d811625d21eeb493071c0c4f4f6243a/score/mw/com/requirements/component_requirements/component_requirements_ipc.trlc>`__)
     - ❌ Open

   * - Logging
     - ✅ Available (46/46)

       | `mw-fr_logging_req <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/analysis-infra/logging/docs/requirements/mw-fr_logging_req.rst>`__
     - ❌ Open
     - ❌ Open

   * - Persistency
     - ✅ Available (37/37)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/persistency/requirements/index.rst>`__
     - ✅ Available (35/35 comp_req)

       | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/requirements/index.rst>`__
     - 🔄 50% (1/2)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/persistency/requirements/chklst_req_inspection.rst>`__
       | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/requirements/chklst_req_inspection.rst>`__

   * - Time
     - ✅ Available (15/15)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/time/docs/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open

   * - Config Mgmt
     - ✅ Available (13/13)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/configuration/config_mgmt/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open

   * - Lifecycle
     - 🔄 0% (0/92)

       | `requirements <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/lifecycle/requirements/index.rst>`__
       | (all 92 entries ``:status: invalid``)
     - 🔄 0% (0/1 comp_req + 0/1 AoU)

       | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/2f2e9c4c3e6c6b38abd0b72f78c8ffb96dc7f9e8/docs/module/health_monitor/requirements/index.rst>`__
       | (template placeholder, ``:status: invalid``)
     - ❌ Open

   * - Security/Crypto
     - ✅ Available (41/41)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/security_crypto/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open

   * - Diagnostic Services
     - ✅ Available (22/22)

       | `requirements <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/diagnostics/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open

   * - NM
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Some/IP
     - ✅ Available (6/6)

       | `score (5) <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/communication/some_ip_gateway/requirements/index.rst>`__
       | `tc8 conformance (1) <https://github.com/eclipse-score/inc_someip_gateway/blob/main/docs/tc8_conformance/requirements.rst>`__
     - ✅ Available (8/8)

       | `tc8 conformance <https://github.com/eclipse-score/inc_someip_gateway/blob/main/docs/tc8_conformance/requirements.rst>`__
     - ❌ Open

.. _overall_status_pa3:

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

.. rubric:: Implementation status: 🔄 15% (5/33 deliverables complete)

.. figure:: /_assets/pa3_arch_progress.svg
   :alt: Total Feature and Component Architecture items across PA2 modules per release
   :width: 720px

   Total Feature and Component Architecture items across all PA2 modules per
   release (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :class: module-phase-tracker-table

   * - **Module**
     - **Feature Architecture**
     - **Component Architecture**
     - **Arch. Inspection**

   * - Baselibs
     - ✅ Available (3/3)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/baselibs/docs/architecture/index.rst>`__
     - 🔄 98% (165/167)

       | `bitmanipulation <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/bitmanipulation/docs/architecture/index.rst>`__
       | `concurrency <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/concurrency/docs/architecture/index.rst>`__
       | `containers <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/containers/docs/architecture/index.rst>`__
       | `filesystem <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/filesystem/docs/architecture/index.rst>`__
       | `flatbuffers <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/flatbuffers/docs/architecture/index.rst>`__
       | `json <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/json/docs/architecture/index.rst>`__
       | `safecpp <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/language/safecpp/docs/architecture/index.rst>`__
       | `memory_shared <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/memory_shared/docs/architecture/index.rst>`__
       | `result <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/result/docs/architecture/index.rst>`__
       | `srs <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/static_reflection_with_serialization/docs/architecture/index.rst>`__
       | `utils <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/utils/docs/architecture/index.rst>`__
     - 🔄 80% (8/10)

       | `bitmanipulation <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/bitmanipulation/docs/architecture/chklst_arc_inspection.rst>`__
       | `concurrency <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/concurrency/docs/architecture/chklst_arc_inspection.rst>`__
       | `containers <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/containers/docs/architecture/chklst_arc_inspection.rst>`__
       | `filesystem <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/filesystem/docs/architecture/chklst_arc_inspection.rst>`__
       | `json <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/json/docs/architecture/chklst_arc_inspection.rst>`__
       | `safecpp <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/language/safecpp/docs/architecture/chklst_arc_inspection.rst>`__
       | `result <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/result/docs/architecture/chklst_arc_inspection.rst>`__
       | `srs <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/static_reflection_with_serialization/docs/architecture/chklst_arc_inspection.rst>`__
       | `utils <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/utils/docs/architecture/chklst_arc_inspection.rst>`__
       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/baselibs/docs/architecture/chklst_arc_inspection.rst>`__

   * - Communication
     - ✅ Available (3/3)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/communication/docs/architecture/index.rst>`__
       | `ipc <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/communication/ipc/docs/architecture/index.rst>`__
     - ✅ Available (16/16)

       | `configuration <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/communication/configuration/docs/architecture/index.rst>`__
       | `frontent <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/communication/frontent/docs/architecture/index.rst>`__
       | `ipc_binding <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/communication/ipc_binding/docs/architecture/index.rst>`__
       | `message_passing <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/communication/message_passing/docs/architecture/index.rst>`__
       | `mock_binding <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/communication/mock_binding/docs/architecture/index.rst>`__
     - ❌ Open

   * - Logging
     - ✅ Available (1/1)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/analysis-infra/logging/docs/architecture/index.rst>`__
     - ✅ Available (3/3)

       | `logging <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/logging/logging/docs/architecture/index.rst>`__
     - ❌ Open

   * - Persistency
     - ✅ Available (9/9)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/persistency/architecture/index.rst>`__
     - 🔄 0% (0/3)

       | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/architecture/index.rst>`__
     - 🔄 0% (0/2)

       | `feature-level <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/persistency/architecture/chklst_arc_inspection.rst>`__
       | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/architecture/chklst_arc_inspection.rst>`__

   * - Time
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Config Mgmt
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Lifecycle
     - 🔄 60% (3/5)

       | `health_monitor <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/lifecycle/architecture/health_monitor.rst>`__
       | `launch_manager <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/features/lifecycle/architecture/launch_manager.rst>`__
     - ✅ Available (15/15)

       | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/2f2e9c4c3e6c6b38abd0b72f78c8ffb96dc7f9e8/docs/module/health_monitor/architecture/index.rst>`__
     - ❌ Open

   * - Security/Crypto
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Diagnostic Services
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - NM
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Some/IP
     - ❌ Open
     - ❌ Open
     - ❌ Open

.. _overall_status_pa4:

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

.. rubric:: Implementation status: 🔄 39% (17/44 deliverables complete)

.. figure:: /_assets/pa4_impl_progress.svg
   :alt: Estimated total Lines of Code across PA2 modules per release
   :width: 720px

   Estimated total Lines of Code across all PA2 modules per release
   (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).

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
     - ✅ Available (~219,400 LOC) `baselibs <https://github.com/eclipse-score/baselibs>`__
     - ❌ Open
     - 🔄 0% (0/9)

       | `bitmanipulation <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/bitmanipulation/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `concurrency <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/concurrency/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `containers <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/containers/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `filesystem <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/filesystem/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `json <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/json/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `safecpp <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/language/safecpp/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `result <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/result/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `srs <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/static_reflection_with_serialization/docs/detailed_design/chklst_impl_inspection.rst>`__
       | `utils <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/baselibs/utils/docs/detailed_design/chklst_impl_inspection.rst>`__

   * - Communication
     - ✅ Available
     - ✅ Available (~175,100 LOC) `communication <https://github.com/eclipse-score/communication>`__
     - 🔄 0% (0/1)

       | `lola <https://github.com/eclipse-score/score/blob/1b51518e71835b02aef97433c5dd083339185256/docs/modules/communication/lola/docs/detailed_design/index.rst>`__
     - ❌ Open

   * - Logging
     - ✅ Available
     - ✅ Available (~40,300 LOC) `logging <https://github.com/eclipse-score/logging>`__
     - ❌ Open
     - ❌ Open

   * - Persistency
     - ✅ Available
     - ✅ Available (~14,700 LOC) `persistency <https://github.com/eclipse-score/persistency>`__
     - 🔄 0% (0/1)

       | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/detailed_design/index.rst>`__
     - 🔄 0% (0/1)

       | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/detailed_design/chklst_impl_inspection.rst>`__

   * - Time
     - ✅ Available
     - ✅ Available (~20,500 LOC) `inc_time <https://github.com/eclipse-score/inc_time>`__
     - ❌ Open
     - ❌ Open

   * - Config Mgmt
     - ✅ Available
     - ✅ Available (~14,200 LOC) `config_management <https://github.com/eclipse-score/config_management>`__
     - ❌ Open
     - ❌ Open

   * - Lifecycle
     - ✅ Available
     - ✅ Available (~28,800 LOC) `lifecycle <https://github.com/eclipse-score/lifecycle>`__
     - 🔄 50% (1/2)
     - ❌ Open

   * - Security/Crypto
     - ✅ Available
     - ✅ Available (~20,600 LOC) `inc_security_crypto <https://github.com/eclipse-score/inc_security_crypto>`__
     - ❌ Open
     - ❌ Open

   * - Diagnostic Services
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - NM
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Some/IP
     - ❌ Open
     - ✅ Available (~12,700 LOC) `inc_someip_gateway <https://github.com/eclipse-score/inc_someip_gateway>`__
     - ❌ Open
     - ❌ Open

.. _overall_status_pa5:

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
   Modules not yet integrated into the reference_integration CI (Time, Config Mgmt)
   show ❌ Open.

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

.. rubric:: Implementation status: 🔄 27% (21/79 deliverables complete)

.. figure:: /_assets/pa5_verification_progress.svg
   :alt: PA5 verification — test counts per release and current coverage
   :width: 1100px

   Test counts (Unit / Component Integration / Feature Integration) per release
   and current code coverage across the 11 PA2 modules. Coverage values are
   only available for the current snapshot.

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
     - | **Platform Verification**
       | **Report**

   * - Baselibs
     - ✅ Available

       | (4,663 tests)
     - 🔄 **C0:** 92.3%

       | **C1:** 60.4% (cpp)
       | **Rust line:** 74.4%
     - ✅ Available (13 tests)
     - ❌ Open
     - ✅ 0 findings

       | `clang-tidy <https://github.com/eclipse-score/baselibs/blob/cab36dd7de92c282f67e78e88032e08585803528/.github/workflows/lint.yml>`__
     - ✅ 0 findings

       | `ASan/UBSan/LSan <https://github.com/eclipse-score/baselibs/blob/cab36dd7de92c282f67e78e88032e08585803528/.github/workflows/sanitizers_linux.yml>`__
     - ❌ Open
     - ❌ Open

   * - Communication
     - ✅ Available

       | (2,374 tests)
     - 🔄 **C0:** 87.9%

       | **C1:** 58.8% (cpp)
     - ✅ Available (42 tests)
     - ❌ Open
     - 🔄 Configured

       | `clang-tidy <https://github.com/eclipse-score/communication/blob/b021eccf1d811625d21eeb493071c0c4f4f6243a/quality/static_analysis/static_analysis.bazelrc>`__
       | `CodeQL/MISRA <https://github.com/eclipse-score/communication/tree/main/quality/static_analysis>`__
       | but no CI enforcement workflow yet
     - ✅ 0 findings

       | `ASan/UBSan/LSan <https://github.com/eclipse-score/communication/blob/b021eccf1d811625d21eeb493071c0c4f4f6243a/.github/workflows/address_undefined_behavior_leak_sanitizer.yml>`__
       | `TSan <https://github.com/eclipse-score/communication/blob/b021eccf1d811625d21eeb493071c0c4f4f6243a/.github/workflows/thread_sanitizer.yml>`__
     - ❌ Open
     - ❌ Open

   * - Logging
     - ✅ Available

       | (619 tests)
     - 🔄 **C0:** 79.5%

       | **C1:** 42.5% (cpp)
       | **Rust line:** 39.9%
     - ❌ Open
     - ✅ Available (1 test)

       | `reference_integration <https://github.com/eclipse-score/reference_integration>`__ (cross-module)
     - ❌ Open
     - ❌ Open
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

       | `Clippy <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/.github/workflows/clippy.yml>`__
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Time
     - ✅ Available

       | (296 tests)
     - ❌ Open
     - ✅ Available (11 tests)
     - ❌ Open
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
     - ❌ Open

   * - Lifecycle
     - ✅ Available

       | (2 tests)
     - 🔄 **C0:** 77.2%

       | **C1:** 45.8% (cpp)
       | **Rust line:** 53.8%
     - ✅ Available (9 tests)
     - ❌ Open
     - ✅ 0 findings

       | `Clippy <https://github.com/eclipse-score/lifecycle/blob/2f2e9c4c3e6c6b38abd0b72f78c8ffb96dc7f9e8/.github/workflows/lint_clippy.yml>`__
     - ❌ Open
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
     - ❌ Open

   * - Diagnostic Services
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - NM
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open

   * - Some/IP
     - ✅ Available

       | (199 tests)
     - ❌ Open
     - ✅ Available (17 stress tests)
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
