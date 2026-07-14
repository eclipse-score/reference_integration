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

:hide-toc:

Overall Status
==============

.. important::

   **Data collected on: 2026-07-14**

.. note::

   This status overview is generated with AI assistance and is **not yet
   fully accurate**. It is intended as a directional snapshot — the trend and
   structure are correct, but individual figures and statuses may still be
   off. Treat the numbers as indicative until the underlying data sources are
   fully validated.

This page tracks feature and process status across the SCORE platform modules.
It is regenerated from live `eclipse-score` GitHub repositories pinned via
``known_good.json``.


.. _overall_status_pa1:

Process Area 1 — Change Management
----------------------------------

.. rubric:: Process Status
   :class: status-heading

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

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">90%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:90%"></div></div>
     <span class="impl-status-detail">10/11 deliverables complete</span>
   </div>


.. list-table::
   :header-rows: 1

   * - **Module**
     - **CR approved**
   * - Baselibs
     - ✅ Accepted

            | `#549 <https://github.com/eclipse-score/score/issues/549>`__ — ✅ Accepted [v0.5 Certifiable] — Feature request: common libraries for IPC and Logging
            | `#917 <https://github.com/eclipse-score/score/issues/917>`__ — ✅ Accepted [v1.0] — Feature Request for ABI compatible datatypes
   * - Communication
     - ✅ Accepted

            | `#69 <https://github.com/eclipse-score/score/issues/69>`__ — ✅ Accepted [v0.5 Certifiable] — Feature Request for IPC
   * - Logging
     - ✅ Accepted

            | `#68 <https://github.com/eclipse-score/score/issues/68>`__ — ✅ Accepted [v0.5 Certifiable] — Feature Request for Logging
   * - Persistency
     - ✅ Accepted

            | `#95 <https://github.com/eclipse-score/score/issues/95>`__ — ✅ Accepted [v0.5 Certifiable] — Feature Request for Persistency
   * - Time
     - ✅ Accepted

            | `#910 <https://github.com/eclipse-score/score/issues/910>`__ — ✅ Accepted [v1.0] — Feature Request for Time
   * - Config Mgmt
     - ✅ Accepted

            | `#754 <https://github.com/eclipse-score/score/issues/754>`__ — ✅ Accepted [v1.0] — Feature Request for Config Management
   * - Lifecycle
     - ✅ Accepted

            | `#909 <https://github.com/eclipse-score/score/issues/909>`__ — ✅ Accepted [v1.0] — Feature Request for Health & Lifecycle
   * - Security/Crypto
     - ✅ Accepted

            | `#905 <https://github.com/eclipse-score/score/issues/905>`__ — ✅ Accepted [v1.0] — Feature Request for Security & Crypto
   * - Diagnostic Services
     - ✅ Accepted

            | `#911 <https://github.com/eclipse-score/score/issues/911>`__ — ✅ Accepted [v1.0] — Feature Request for Diagnostic Services & Fault Management
   * - NM
     - ❌ Open
   * - Some/IP
     - ✅ Accepted

            | `#914 <https://github.com/eclipse-score/score/issues/914>`__ — ✅ Accepted [v1.0] — Feature Request for SOME/IP Gateway


.. _overall_status_pa2:

Process Area 2 — Requirements Engineering
-----------------------------------------

.. rubric:: Process Status
   :class: status-heading

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

.. figure:: /_assets/pa2_impl_progress.svg
   :alt: PA2 implementation progress
   :width: 720px

   Total Feature and Component Requirements across the 11 PA2 modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → v0.8).

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">45%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:45%"></div></div>
     <span class="impl-status-detail">15/33 deliverables complete</span>
   </div>


.. list-table::
   :header-rows: 1

   * - **Module**
     - **Feature Req**
     - **Component Req**
     - **Req. Inspection**
   * - Baselibs
     - ✅ Available (17/17)

            | `baselibs <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/baselibs/docs/requirements/index.rst>`__
     - ✅ Available (112/112 comp_req + 32/32 AoU)

            | `abi_compatible_data_types <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/abi_compatible_data_types/docs/requirements/index.rst>`__
            | `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/bitmanipulation/docs/requirements/index.rst>`__
            | `concurrency <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/concurrency/docs/requirements/index.rst>`__
            | `containers <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/containers/docs/requirements/index.rst>`__
            | `filesystem <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/filesystem/docs/requirements/index.rst>`__
            | `flatbuffers <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/flatbuffers/docs/requirements/index.rst>`__
            | `json <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/json/docs/requirements/index.rst>`__
            | `vajson <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/json/docs/vajson/requirements/index.rst>`__
            | `safecpp <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/language/safecpp/docs/requirements/index.rst>`__
            | `memory_shared <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/memory_shared/docs/requirements/index.rst>`__
            | `result <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/result/docs/requirements/index.rst>`__
            | `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/static_reflection_with_serialization/docs/requirements/index.rst>`__
            | `utils <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/utils/docs/requirements/index.rst>`__
     - 🔄 30% (3/10)

            | ✅ `baselibs <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/baselibs/docs/requirements/chklst_req_inspection.rst>`__
            | ✅ `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/bitmanipulation/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `concurrency <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/concurrency/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `containers <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/containers/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `filesystem <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/filesystem/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `json <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/json/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `safecpp <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/language/safecpp/docs/requirements/chklst_req_inspection.rst>`__
            | ✅ `result <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/result/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/static_reflection_with_serialization/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `utils <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/utils/docs/requirements/chklst_req_inspection.rst>`__
   * - Communication
     - ✅ Available (53/53)

            | `communication <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/communication/docs/requirements/index.rst>`__
            | `ipc <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/communication/ipc/docs/requirements/index.rst>`__
     - ✅ Available (363/363 comp_req [TRLC] + 33/33 AoU)

            | `ipc <https://github.com/eclipse-score/communication/blob/0e0640998096049a8dd65a4173b03a988d5a85a7/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc.trlc>`__ (310) [TRLC]
            | `ipc_fields <https://github.com/eclipse-score/communication/blob/0e0640998096049a8dd65a4173b03a988d5a85a7/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_fields.trlc>`__ (17) [TRLC]
            | `ipc_methods <https://github.com/eclipse-score/communication/blob/0e0640998096049a8dd65a4173b03a988d5a85a7/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_methods.trlc>`__ (3) [TRLC]
            | `message_passing <https://github.com/eclipse-score/communication/blob/0e0640998096049a8dd65a4173b03a988d5a85a7/score/message_passing/dependability/requirements/component_requirements.trlc>`__ (33) [TRLC]
            | `aou_req <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/modules/communication/docs/requirements/aou_req.rst>`__
     - ❌ Open
   * - Logging
     - ✅ Available (46/46)

            | `logging <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/analysis-infra/logging/docs/requirements/mw-fr_logging_req.rst>`__
     - ✅ Available (22/22 comp_req)

            | `datarouter <https://github.com/eclipse-score/logging/blob/6282f3a2ec6b1eeeab87c8e9a4435c586bcf9973/docs/components/datarouter/requirements.rst>`__
            | `log <https://github.com/eclipse-score/logging/blob/6282f3a2ec6b1eeeab87c8e9a4435c586bcf9973/docs/components/mw/log/requirements.rst>`__
     - ❌ Open
   * - Persistency
     - ✅ Available (37/37)

            | `persistency <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/persistency/requirements/index.rst>`__
     - ✅ Available (35/35 comp_req)

            | `kvs <https://github.com/eclipse-score/persistency/blob/35a937f34ff5b2daad8df56e36de76687f19d631/score/kvs/docs/requirements/index.rst>`__
     - ✅ Available (2/2)

            | ✅ `persistency <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/persistency/requirements/chklst_req_inspection.rst>`__
            | ✅ `kvs <https://github.com/eclipse-score/persistency/blob/35a937f34ff5b2daad8df56e36de76687f19d631/score/kvs/docs/requirements/chklst_req_inspection.rst>`__
   * - Time
     - ✅ Available (15/15)

            | `time <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/time/docs/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open
   * - Config Mgmt
     - ✅ Available (13/13)

            | `config_mgmt <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/configuration/config_mgmt/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - 🔄 0% (0/92)

            | `lifecycle <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/lifecycle/requirements/index.rst>`__
     - 🔄 0% (0/1 comp_req + 0/1 AoU)

            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/654ac348e1cb9327e5c8c4d84fd0028ad3ef2714/score/health_monitor/docs/requirements/index.rst>`__
     - ❌ Open
   * - Security/Crypto
     - ✅ Available (41/41)

            | `security_crypto <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/security_crypto/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open
   * - Diagnostic Services
     - ✅ Available (22/22)

            | `diagnostics <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/diagnostics/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open
   * - NM
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Some/IP
     - ✅ Available (5/5)

            | `some_ip_gateway <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/communication/some_ip_gateway/requirements/index.rst>`__
     - ✅ Available (8/8 comp_req)

            | `tc8_conformance <https://github.com/eclipse-score/inc_someip_gateway/blob/main/docs/tc8_conformance/requirements.rst>`__
     - ❌ Open


.. _overall_status_pa3:

Process Area 3 — Architecture Design
------------------------------------

.. rubric:: Process Status
   :class: status-heading

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

.. figure:: /_assets/pa3_arch_progress.svg
   :alt: PA3 architecture progress
   :width: 720px

   Total Feature and Component Architecture elements across the 11 PA2 modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → v0.8).

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">27%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:27%"></div></div>
     <span class="impl-status-detail">9/33 deliverables complete</span>
   </div>


.. list-table::
   :header-rows: 1

   * - **Module**
     - **Feature Arch**
     - **Component Arch**
     - **Arch. Inspection**
   * - Baselibs
     - ✅ Available (3/3)

            | `baselibs <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/baselibs/docs/architecture/index.rst>`__
            | `baselibs <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/feature/architecture/index.rst>`__
     - 🔄 97% (139/142)

            | `abi_compatible_data_types <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/abi_compatible_data_types/docs/architecture/index.rst>`__
            | `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/bitmanipulation/docs/architecture/index.rst>`__
            | `concurrency <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/concurrency/docs/architecture/index.rst>`__
            | `containers <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/containers/docs/architecture/index.rst>`__
            | `filesystem <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/filesystem/docs/architecture/index.rst>`__
            | `flatbuffers <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/flatbuffers/docs/architecture/index.rst>`__
            | `json <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/json/docs/architecture/index.rst>`__
            | `vajson <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/json/docs/vajson/architecture/index.rst>`__
            | `safecpp <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/language/safecpp/docs/architecture/index.rst>`__
            | `memory_shared <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/memory_shared/docs/architecture/index.rst>`__
            | `result <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/result/docs/architecture/index.rst>`__
            | `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/static_reflection_with_serialization/docs/architecture/index.rst>`__
            | `utils <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/utils/docs/architecture/index.rst>`__
     - 🔄 80% (8/10)

            | ✅ `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/bitmanipulation/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `concurrency <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/concurrency/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `containers <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/containers/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `filesystem <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/filesystem/docs/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `json <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/json/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `safecpp <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/language/safecpp/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `result <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/result/docs/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/static_reflection_with_serialization/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `utils <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/utils/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `baselibs <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/feature/architecture/chklst_arc_inspection.rst>`__
   * - Communication
     - ✅ Available (3/3)

            | `communication <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/communication/docs/architecture/index.rst>`__
            | `ipc <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/communication/ipc/docs/architecture/index.rst>`__
     - ✅ Available (16/16)

            | `configuration <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/modules/communication/configuration/docs/architecture/index.rst>`__
            | `frontent <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/modules/communication/frontent/docs/architecture/index.rst>`__
            | `ipc_binding <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/modules/communication/ipc_binding/docs/architecture/index.rst>`__
            | `message_passing <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/modules/communication/message_passing/docs/architecture/index.rst>`__
            | `mock_binding <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/modules/communication/mock_binding/docs/architecture/index.rst>`__
     - ❌ Open
   * - Logging
     - ✅ Available (2/2)

            | `logging <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/analysis-infra/logging/docs/architecture/index.rst>`__
            | `logging <https://github.com/eclipse-score/logging/blob/6282f3a2ec6b1eeeab87c8e9a4435c586bcf9973/docs/features/logging/architecture/index.rst>`__
     - ✅ Available (3/3)

            | `logging <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/modules/logging/logging/docs/architecture/index.rst>`__
     - ❌ Open
   * - Persistency
     - ✅ Available (9/9)

            | `persistency <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/persistency/architecture/index.rst>`__
            | `persistency <https://github.com/eclipse-score/persistency/blob/35a937f34ff5b2daad8df56e36de76687f19d631/docs/features/persistency/architecture/index.rst>`__
     - 🔄 0% (0/3)

            | `kvs <https://github.com/eclipse-score/persistency/blob/35a937f34ff5b2daad8df56e36de76687f19d631/score/kvs/docs/architecture/index.rst>`__
     - 🔄 0% (0/2)

            | 🔄 `persistency <https://github.com/eclipse-score/persistency/blob/35a937f34ff5b2daad8df56e36de76687f19d631/docs/features/persistency/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `kvs <https://github.com/eclipse-score/persistency/blob/35a937f34ff5b2daad8df56e36de76687f19d631/score/kvs/docs/architecture/chklst_arc_inspection.rst>`__
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

            | `lifecycle <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/lifecycle/architecture/health_monitor.rst>`__
            | `lifecycle <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/features/lifecycle/architecture/launch_manager.rst>`__
     - ✅ Available (15/15)

            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/654ac348e1cb9327e5c8c4d84fd0028ad3ef2714/score/health_monitor/docs/architecture/index.rst>`__
     - ❌ Open
   * - Security/Crypto
     - ❌ Open
     - 🔄 0% (0/21)

            | `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/main/docs/crypto/architecture/interfaces.rst>`__
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
     - ✅ Available (1/1)

            | `docs/architecture/features.rst <https://github.com/eclipse-score/inc_someip_gateway/blob/main/docs/architecture/features.rst>`__
     - ✅ Available (4/4)

            | `docs/architecture/components.rst <https://github.com/eclipse-score/inc_someip_gateway/blob/main/docs/architecture/components.rst>`__
     - ❌ Open


.. _overall_status_pa4:

Process Area 4 — Implementation
-------------------------------

.. rubric:: Process Status
   :class: status-heading

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

.. figure:: /_assets/pa4_impl_progress.svg
   :alt: PA4 implementation progress
   :width: 720px

   Estimated Lines of Code across the 11 PA2 modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → v0.8).

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">45%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:45%"></div></div>
     <span class="impl-status-detail">20/44 deliverables complete</span>
   </div>


.. list-table::
   :header-rows: 1

   * - **Module**
     - **SW Dev Plan**
     - **Code**
     - **Detailed Design**
     - **Impl. Inspection**
   * - Baselibs
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~344,200 LOC)

            | `baselibs <https://github.com/eclipse-score/baselibs>`__
     - ❌ Open
     - 🔄 0% (0/9)

            | 🔄 `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/bitmanipulation/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `concurrency <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/concurrency/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `containers <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/containers/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `filesystem <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/filesystem/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `json <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/json/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `safecpp <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/language/safecpp/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `result <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/result/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/static_reflection_with_serialization/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `utils <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/components/utils/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Communication
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~274,000 LOC)

            | `communication <https://github.com/eclipse-score/communication>`__
     - ❌ Open
     - ❌ Open
   * - Logging
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~53,200 LOC)

            | `logging <https://github.com/eclipse-score/logging>`__
     - ❌ Open
     - ❌ Open
   * - Persistency
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~18,000 LOC)

            | `persistency <https://github.com/eclipse-score/persistency>`__
     - ❌ Open
     - 🔄 0% (0/1)

            | 🔄 `kvs <https://github.com/eclipse-score/persistency/blob/35a937f34ff5b2daad8df56e36de76687f19d631/score/kvs/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Time
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~25,700 LOC)

            | `inc_time <https://github.com/eclipse-score/inc_time>`__
     - ❌ Open
     - ❌ Open
   * - Config Mgmt
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~21,200 LOC)

            | `config_management <https://github.com/eclipse-score/config_management>`__
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~54,300 LOC)

            | `lifecycle <https://github.com/eclipse-score/lifecycle>`__
     - ❌ Open
     - ❌ Open
   * - Security/Crypto
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~51,700 LOC)

            | `inc_security_crypto <https://github.com/eclipse-score/inc_security_crypto>`__
     - ❌ Open
     - ❌ Open
   * - Diagnostic Services
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - NM
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Some/IP
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~39,500 LOC)

            | `inc_someip_gateway <https://github.com/eclipse-score/inc_someip_gateway>`__
     - ❌ Open
     - ❌ Open


.. _overall_status_pa5:

Process Area 5 — Verification
-----------------------------

.. rubric:: Process Status
   :class: status-heading

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

.. figure:: /_assets/pa5_verification_progress.svg
   :alt: PA5 verification progress
   :width: 1080px

   Test counts and coverage across the 11 PA2 modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → v0.8).

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">33%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:33%"></div></div>
     <span class="impl-status-detail">26/77 deliverables complete</span>
   </div>

.. note::

   **C0/C1 Coverage** data is sourced from the ``reference_integration``
   CI (*Code Quality & Documentation* workflow,
   ``bazel coverage --config=ferrocene-coverage``). C0 = line coverage,
   C1 = branch coverage. Rust coverage reports line coverage only.
   Modules not yet integrated into the ``reference_integration`` CI
   (Config Mgmt, Security/Crypto, Some/IP) show ❌ Open.

.. note::

   **Static Code Analysis** is tracked per module via dedicated CI
   workflows (clang-tidy for C++, Rust Clippy for Rust). All listed
   workflows are *zero-tolerance* (CI fails on any finding), so a passing
   ``main`` branch implies **0 open findings**. Additionally, CodeQL
   runs centrally across all pinned repositories in
   ``reference_integration`` (finding counts require the GitHub Security
   tab).

   **Dynamic Code Analysis** is tracked via sanitizer CI workflows
   (ASan/UBSan/LSan via ``--config=asan_ubsan_lsan``, TSan via
   ``--config=tsan``). All listed workflows are zero-tolerance, so a
   passing ``main`` branch implies **0 sanitizer findings**.


.. list-table::
   :header-rows: 1

   * - **Module**
     - **Unit Tests**
     - **C0/C1 Cov**
     - **Comp. IT**
     - **Feat. IT**
     - **Static**
     - **Dynamic**
     - **Module Ver. Rpt**
   * - Baselibs
     - ✅ Available

            | 25833 tests
     - 🔄

            | **C0:** 94.9%
            | **C1:** 61.9% (cpp)
     - ✅ Available

            | 13 tests
     - ❌ Open
     - ✅ 0 findings
     - ✅ 0 findings
     - 🔄 Draft

            | 🔄 `verification <https://github.com/eclipse-score/baselibs/blob/ce204159f37ee7815907369a8f678583bf102306/docs/baselibs/module/verification/module_verification_report.rst>`__
   * - Communication
     - ✅ Available

            | 3301 tests
     - 🔄

            | **C0:** 83.7%
            | **C1:** 54.8% (cpp)
     - ✅ Available

            | 63 tests
     - ❌ Open
     - 🔄 Configured (no CI)
     - ✅ 0 findings
     - 🔄 Draft

            | 🔄 `verification <https://github.com/eclipse-score/score/blob/24ec6f276cd37755b5dae7f2345913628d56831f/docs/modules/communication/docs/verification/module_verification_report.rst>`__
   * - Logging
     - ✅ Available

            | 650 tests
     - 🔄

            | **C0:** 96.8%
            | **C1:** 74.1% (cpp)
            | **Rust line:** 39.86%
     - ✅ Available

            | 8 tests
     - ✅ Available

            | 1 test
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Persistency
     - ✅ Available

            | 95 tests
     - 🔄

            | **C0:** 94.7%
            | **C1:** 63.0% (cpp)
            | **Rust line:** 92.66%
     - ✅ Available

            | 44 tests
     - ✅ Available

            | 53 tests
     - ✅ 0 findings
     - ❌ Open
     - ✅ Available

            | ✅ `verification <https://github.com/eclipse-score/persistency/blob/35a937f34ff5b2daad8df56e36de76687f19d631/docs/verification_report/module_verification_report.rst>`__
   * - Time
     - ✅ Available

            | 314 tests
     - 🔄

            | **C0:** 88.7%
            | **C1:** 61.1% (cpp)
     - ✅ Available

            | 4 tests
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Config Mgmt
     - ✅ Available

            | 190 tests
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ✅ 0 findings
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - ✅ Available

            | 248 tests
     - 🔄

            | **C0:** 83.9%
            | **C1:** 56.9% (cpp)
            | **Rust line:** 53.81%
     - ✅ Available

            | 36 tests
     - ❌ Open
     - ✅ 0 findings
     - ❌ Open
     - ❌ Open
   * - Security/Crypto
     - ✅ Available

            | 5 tests
     - ❌ Open
     - ✅ Available

            | 11 tests
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - 🔄 Draft

            | 🔄 `verification <https://github.com/eclipse-score/inc_security_crypto/blob/main/docs/verification_report/module_verification_report.rst>`__
   * - Diagnostic Services
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
   * - Some/IP
     - ✅ Available

            | 375 tests
     - ❌ Open
     - ✅ Available

            | 21 tests
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open


.. admonition:: Platform Verification Report
   :class: important platform-ver-report

   Platform Verification Report — ❌ **Open** (single project-wide deliverable;
   not yet published at the pinned ``score`` ref)
