:hide-toc:

Overall Status
==============

This page tracks feature and process status across the SCORE platform modules.
It is regenerated from live `eclipse-score` GitHub repositories pinned via
``known_good.json``.


Process Area 1 — Change Management
----------------------------------

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


.. rubric:: Implementation status: 🔄 90% (10/11 deliverables complete)


.. list-table::
   :header-rows: 1

   * - **Module**
     - **CR approved**
   * - Baselibs
     - ✅ Accepted

            | `#549 <https://github.com/eclipse-score/score/issues/549>`__ — ✅ Accepted [v0.5 Certifiable] — Feature request: common libraries for IPC and Logging
            | `#757 <https://github.com/eclipse-score/score/issues/757>`__ — ✅ Accepted — Feature request for qualified json-parser
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

   Total Feature and Component Requirements across the 11 PA2 modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).


.. rubric:: Implementation status: 🔄 39% (13/33 deliverables complete)


.. list-table::
   :header-rows: 1

   * - **Module**
     - **Feature Req**
     - **Component Req**
     - **Req. Inspection**
   * - Baselibs
     - ✅ Available (37/37)

            | `abi_compatible_data_types <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/baselibs/abi_compatible_data_types/requirements.rst>`__
            | `baselibs <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/baselibs/docs/requirements/index.rst>`__
     - ✅ Available (84/84 comp_req + 32/32 AoU)

            | `bitmanipulation <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/bitmanipulation/docs/requirements/index.rst>`__
            | `concurrency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/concurrency/docs/requirements/index.rst>`__
            | `containers <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/containers/docs/requirements/index.rst>`__
            | `filesystem <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/filesystem/docs/requirements/index.rst>`__
            | `json <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/json/docs/requirements/index.rst>`__
            | `safecpp <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/language/safecpp/docs/requirements/index.rst>`__
            | `result <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/result/docs/requirements/index.rst>`__
            | `static_reflection_with_serialization <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/static_reflection_with_serialization/docs/requirements/index.rst>`__
            | `utils <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/utils/docs/requirements/index.rst>`__
     - 🔄 20% (2/10)

            | `baselibs <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/baselibs/docs/requirements/chklst_req_inspection.rst>`__
            | `bitmanipulation <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/bitmanipulation/docs/requirements/chklst_req_inspection.rst>`__
            | `concurrency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/concurrency/docs/requirements/chklst_req_inspection.rst>`__
            | `containers <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/containers/docs/requirements/chklst_req_inspection.rst>`__
            | `filesystem <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/filesystem/docs/requirements/chklst_req_inspection.rst>`__
            | `json <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/json/docs/requirements/chklst_req_inspection.rst>`__
            | `safecpp <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/language/safecpp/docs/requirements/chklst_req_inspection.rst>`__
            | `result <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/result/docs/requirements/chklst_req_inspection.rst>`__
            | `static_reflection_with_serialization <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/static_reflection_with_serialization/docs/requirements/chklst_req_inspection.rst>`__
            | `utils <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/utils/docs/requirements/chklst_req_inspection.rst>`__
   * - Communication
     - ✅ Available (53/53)

            | `communication <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/communication/docs/requirements/index.rst>`__
            | `ipc <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/communication/ipc/docs/requirements/index.rst>`__
     - ✅ Available (0/0 comp_req [TRLC] + 33/33 AoU)

            | `com <https://github.com/eclipse-score/communication/blob/b021eccf1d811625d21eeb493071c0c4f4f6243a/score/mw/com/requirements/component_requirements/component_requirements_ipc.trlc>`__
            | `communication <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/communication/docs/requirements/aou_req.rst>`__
     - ❌ Open
   * - Logging
     - ✅ Available (46/46)

            | `logging <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/analysis-infra/logging/docs/requirements/mw-fr_logging_req.rst>`__
     - ❌ Open
     - ❌ Open
   * - Persistency
     - ✅ Available (37/37)

            | `persistency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/persistency/requirements/index.rst>`__
     - ✅ Available (35/35 comp_req)

            | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/requirements/index.rst>`__
     - 🔄 50% (1/2)

            | `persistency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/persistency/requirements/chklst_req_inspection.rst>`__
            | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/requirements/chklst_req_inspection.rst>`__
   * - Time
     - ✅ Available (15/15)

            | `time <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/time/docs/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open
   * - Config Mgmt
     - ✅ Available (13/13)

            | `config_mgmt <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/configuration/config_mgmt/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - 🔄 0% (0/92)

            | `lifecycle <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/lifecycle/requirements/index.rst>`__
     - 🔄 0% (0/1 comp_req + 0/1 AoU)

            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/2f2e9c4c3e6c6b38abd0b72f78c8ffb96dc7f9e8/docs/module/health_monitor/requirements/index.rst>`__
     - ❌ Open
   * - Security/Crypto
     - ✅ Available (41/41)

            | `security_crypto <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/security_crypto/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open
   * - Diagnostic Services
     - ✅ Available (22/22)

            | `diagnostics <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/diagnostics/requirements/index.rst>`__
     - ❌ Open
     - ❌ Open
   * - NM
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Some/IP
     - ✅ Available (5/5)

            | `some_ip_gateway <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/communication/some_ip_gateway/requirements/index.rst>`__
     - ✅ Available (8/8 comp_req)

            | `tc8_conformance <https://github.com/eclipse-score/inc_someip_gateway/blob/main/docs/tc8_conformance/requirements.rst>`__
     - ❌ Open


.. _overall_status_pa3:

Process Area 3 — Architecture Design
------------------------------------

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


.. figure:: /_assets/pa3_arch_progress.svg
   :alt: PA3 architecture progress
   :width: 720px

   Total Feature and Component Architecture elements across the 11 PA2 modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).


.. rubric:: Implementation status: 🔄 24% (8/33 deliverables complete)


.. list-table::
   :header-rows: 1

   * - **Module**
     - **Feature Arch**
     - **Component Arch**
     - **Arch. Inspection**
   * - Baselibs
     - ✅ Available (3/3)

            | `baselibs <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/baselibs/docs/architecture/index.rst>`__
     - 🔄 98% (164/166)

            | `bitmanipulation <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/bitmanipulation/docs/architecture/index.rst>`__
            | `concurrency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/concurrency/docs/architecture/index.rst>`__
            | `containers <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/containers/docs/architecture/index.rst>`__
            | `filesystem <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/filesystem/docs/architecture/index.rst>`__
            | `json <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/json/docs/architecture/index.rst>`__
            | `safecpp <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/language/safecpp/docs/architecture/index.rst>`__
            | `result <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/result/docs/architecture/index.rst>`__
            | `static_reflection_with_serialization <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/static_reflection_with_serialization/docs/architecture/index.rst>`__
            | `utils <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/utils/docs/architecture/index.rst>`__
     - 🔄 80% (8/10)

            | `baselibs <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/baselibs/docs/architecture/chklst_arc_inspection.rst>`__
            | `bitmanipulation <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/bitmanipulation/docs/architecture/chklst_arc_inspection.rst>`__
            | `concurrency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/concurrency/docs/architecture/chklst_arc_inspection.rst>`__
            | `containers <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/containers/docs/architecture/chklst_arc_inspection.rst>`__
            | `filesystem <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/filesystem/docs/architecture/chklst_arc_inspection.rst>`__
            | `json <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/json/docs/architecture/chklst_arc_inspection.rst>`__
            | `safecpp <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/language/safecpp/docs/architecture/chklst_arc_inspection.rst>`__
            | `result <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/result/docs/architecture/chklst_arc_inspection.rst>`__
            | `static_reflection_with_serialization <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/static_reflection_with_serialization/docs/architecture/chklst_arc_inspection.rst>`__
            | `utils <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/utils/docs/architecture/chklst_arc_inspection.rst>`__
   * - Communication
     - ✅ Available (3/3)

            | `communication <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/communication/docs/architecture/index.rst>`__
            | `ipc <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/communication/ipc/docs/architecture/index.rst>`__
     - ✅ Available (16/16)

            | `configuration <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/communication/configuration/docs/architecture/index.rst>`__
            | `frontent <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/communication/frontent/docs/architecture/index.rst>`__
            | `ipc_binding <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/communication/ipc_binding/docs/architecture/index.rst>`__
            | `message_passing <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/communication/message_passing/docs/architecture/index.rst>`__
     - ❌ Open
   * - Logging
     - ✅ Available (1/1)

            | `logging <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/analysis-infra/logging/docs/architecture/index.rst>`__
     - ✅ Available (3/3)

            | `logging <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/logging/logging/docs/architecture/index.rst>`__
     - ❌ Open
   * - Persistency
     - ✅ Available (9/9)

            | `persistency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/persistency/architecture/index.rst>`__
     - 🔄 0% (0/3)

            | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/architecture/index.rst>`__
     - 🔄 0% (0/2)

            | `persistency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/persistency/architecture/chklst_arc_inspection.rst>`__
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

            | `lifecycle <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/lifecycle/architecture/health_monitor.rst>`__
            | `lifecycle <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/features/lifecycle/architecture/launch_manager.rst>`__
     - ✅ Available (15/15)

            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/2f2e9c4c3e6c6b38abd0b72f78c8ffb96dc7f9e8/docs/module/health_monitor/architecture/index.rst>`__
     - ❌ Open
   * - Security/Crypto
     - ❌ Open
     - 🔄 0% (0/23)

            | `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/main/docs/crypto/architecture/dynamic_architecture.rst>`__
            | `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/main/docs/crypto/architecture/index.rst>`__
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
     - ❌ Open
     - ✅ Available (2/2)

            | `docs/architecture/components.rst <https://github.com/eclipse-score/inc_someip_gateway/blob/main/docs/architecture/components.rst>`__
     - ❌ Open


.. _overall_status_pa4:

Process Area 4 — Implementation
-------------------------------

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


.. figure:: /_assets/pa4_impl_progress.svg
   :alt: PA4 implementation progress
   :width: 720px

   Estimated Lines of Code across the 11 PA2 modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).


.. rubric:: Implementation status: 🔄 47% (21/44 deliverables complete)


.. list-table::
   :header-rows: 1

   * - **Module**
     - **SW Dev Plan**
     - **Code**
     - **Detailed Design**
     - **Impl. Inspection**
   * - Baselibs
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~315,200 LOC)

            | `baselibs <https://github.com/eclipse-score/baselibs>`__
     - ❌ Open
     - 🔄 0% (0/9)

            | `bitmanipulation <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/bitmanipulation/docs/detailed_design/chklst_impl_inspection.rst>`__
            | `concurrency <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/concurrency/docs/detailed_design/chklst_impl_inspection.rst>`__
            | `containers <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/containers/docs/detailed_design/chklst_impl_inspection.rst>`__
            | `filesystem <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/filesystem/docs/detailed_design/chklst_impl_inspection.rst>`__
            | `json <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/json/docs/detailed_design/chklst_impl_inspection.rst>`__
            | `safecpp <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/language/safecpp/docs/detailed_design/chklst_impl_inspection.rst>`__
            | `result <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/result/docs/detailed_design/chklst_impl_inspection.rst>`__
            | `static_reflection_with_serialization <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/static_reflection_with_serialization/docs/detailed_design/chklst_impl_inspection.rst>`__
            | `utils <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/modules/baselibs/utils/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Communication
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~253,700 LOC)

            | `communication <https://github.com/eclipse-score/communication>`__
     - ❌ Open
     - ❌ Open
   * - Logging
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~50,800 LOC)

            | `logging <https://github.com/eclipse-score/logging>`__
     - ❌ Open
     - ❌ Open
   * - Persistency
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~18,000 LOC)

            | `persistency <https://github.com/eclipse-score/persistency>`__
     - ❌ Open
     - 🔄 0% (0/1)

            | `kvs <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/kvs/detailed_design/chklst_impl_inspection.rst>`__
   * - Time
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~23,200 LOC)

            | `inc_time <https://github.com/eclipse-score/inc_time>`__
     - ❌ Open
     - ❌ Open
   * - Config Mgmt
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~20,400 LOC)

            | `config_management <https://github.com/eclipse-score/config_management>`__
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~51,800 LOC)

            | `lifecycle <https://github.com/eclipse-score/lifecycle>`__
     - ✅ Available (1/1)

            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/2f2e9c4c3e6c6b38abd0b72f78c8ffb96dc7f9e8/docs/module/health_monitor/detailed_design/index.rst>`__
     - ❌ Open
   * - Security/Crypto
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~51,600 LOC)

            | `inc_security_crypto <https://github.com/eclipse-score/inc_security_crypto>`__
     - ❌ Open
     - ❌ Open
   * - Diagnostic Services
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - NM
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Some/IP
     - ✅ Available

            | `platform_management_plan <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~24,500 LOC)

            | `inc_someip_gateway <https://github.com/eclipse-score/inc_someip_gateway>`__
     - ❌ Open
     - ❌ Open


.. _overall_status_pa5:

Process Area 5 — Verification
-----------------------------

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


.. figure:: /_assets/pa5_verification_progress.svg
   :alt: PA5 verification progress
   :width: 1080px

   Test counts and coverage across the 11 PA2 modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).


.. rubric:: Implementation status: 🔄 28% (25/88 deliverables complete)

.. note::

   **C0/C1 Coverage** data is sourced from the ``reference_integration``
   CI (*Code Quality & Documentation* workflow,
   ``bazel coverage --config=ferrocene-coverage``). C0 = line coverage,
   C1 = branch coverage. Rust coverage reports line coverage only.
   Modules not yet integrated into the ``reference_integration`` CI
   (Time, Config Mgmt, Security/Crypto, Some/IP) show ❌ Open.

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

            | 5376 tests
     - 🔄

            | **C0:** 92.3%
            | **C1:** 60.3% (cpp)
            | **Rust line:** 74.35%
     - ✅ Available

            | 13 tests
     - ❌ Open
     - ✅ 0 findings
     - ✅ 0 findings
     - ❌ Open
   * - Communication
     - ✅ Available

            | 2585 tests
     - 🔄

            | **C0:** 87.9%
            | **C1:** 58.8% (cpp)
     - ✅ Available

            | 42 tests
     - ❌ Open
     - 🔄 Configured (no CI)
     - ✅ 0 findings
     - ❌ Open
   * - Logging
     - ✅ Available

            | 617 tests
     - 🔄

            | **C0:** 79.3%
            | **C1:** 42.1% (cpp)
            | **Rust line:** 39.86%
     - ❌ Open
     - ✅ Available

            | 1 test
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Persistency
     - ✅ Available

            | 138 tests
     - 🔄

            | **C0:** 94.7%
            | **C1:** 63.0% (cpp)
            | **Rust line:** 92.66%
     - ✅ Available
     - ✅ Available

            | 53 tests
     - ✅ 0 findings
     - ❌ Open
     - ✅ Available

            | `verification <https://github.com/eclipse-score/persistency/blob/4d1fa1ae3c55d27d0f1e863b8cdf59a148651c5d/docs/persistency/docs/verification/module_verification_report.rst>`__
   * - Time
     - ✅ Available

            | 296 tests
     - ❌ Open
     - ✅ Available

            | 11 tests
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Config Mgmt
     - ✅ Available

            | 179 tests
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ✅ 0 findings
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - ✅ Available

            | 2 tests
     - 🔄

            | **C0:** 77.2%
            | **C1:** 45.8% (cpp)
            | **Rust line:** 53.81%
     - ✅ Available

            | 8 tests
     - ❌ Open
     - ✅ 0 findings
     - ❌ Open
     - ❌ Open
   * - Security/Crypto
     - ✅ Available
     - ❌ Open
     - ✅ Available

            | 5 tests
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

            | 237 tests
     - ❌ Open
     - ✅ Available

            | 17 tests
     - ❌ Open
     - ❌ Open
     - ❌ Open
     - ❌ Open

.. admonition:: Platform Verification Report
   :class: important platform-ver-report

   `platform_ver_report <https://github.com/eclipse-score/score/blob/5b8a1e34c417384d919bb8c08d32213896ffe5aa/docs/score_releases/verification/platform_ver_report.rst>`__
   — 🔄 **Draft** (single project-wide deliverable)

