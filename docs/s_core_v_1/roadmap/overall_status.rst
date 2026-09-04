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

   **Data collected on: 2026-09-04**

.. note::

   This status overview is generated with AI assistance and is **not yet
   fully accurate**. It is intended as a directional snapshot — the trend and
   structure are correct, but individual figures and statuses may still be
   off. Treat the numbers as indicative until the underlying data sources are
   fully validated.

This page tracks feature and process status across the SCORE platform modules.
It is regenerated from live `eclipse-score` GitHub repositories pinned via
``known_good.json``.

.. admonition:: Changes in this snapshot
   :class: tip

   * The progress charts now carry a fifth column, **v0.9** — this snapshot
     is measured against the ``release_candidate_09`` pins, so the v0.8
     column holds the previously published release figures.
   * **Kyron** is tracked as a module for the first time (12 module rows
     instead of 11). It ships code, unit tests, Rust coverage, a Clippy gate
     and a large component-integration suite, but has no requirements,
     architecture or detailed-design documents yet.
   * The ``score`` repository was **restructured**: component documentation
     moved from ``docs/modules/<module>/`` into the individual module
     repositories, and ``docs/features/analysis-infra/logging`` became
     ``docs/features/log_and_trace/logging``. All path filters were rebuilt
     against the pinned trees.
   * Several modules migrated their requirements to **TRLC**
     (Communication, Config Management). Where an RST set and a TRLC set
     describe the same feature area, only the larger of the two is counted —
     the duplicate is suppressed to avoid double counting.
   * **Time** and **Config Management** are now pinned in ``known_good.json``,
     so their source links point at a fixed commit instead of ``main``.
   * **Security/Crypto** and **Some/IP** are *not* pinned in
     ``known_good.json`` and therefore no longer part of the reference
     integration CI. Their unit-test and coverage cells are marked
     🔄 *Module CI only* and link to the workflows in their own repositories.
   * The PA2 feature-requirement total decreased (341 → 297) because the
     Lifecycle feature requirements were consolidated during the
     restructuring (92 → 32); the component-requirement total grew
     strongly (607 → 783).


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
     <span class="impl-status-percent">83%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:83%"></div></div>
     <span class="impl-status-detail">10/12 deliverables complete</span>
   </div>


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
   * - Kyron
     - 🔄 In Progress

            | `#2029 <https://github.com/eclipse-score/score/issues/2029>`__ — 🔄 Open — Certified async-runtime
            | `#2445 <https://github.com/eclipse-score/score/issues/2445>`__ — ✅ Accepted [v1.0] — Kyron — S-CORE Release v1.0
            | `#2894 <https://github.com/eclipse-score/score/issues/2894>`__ — ✅ Accepted [v0.8] — Kyron for S-CORE Release v0.8
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
   :width: 880px

   Total Feature and Component Requirements across the 12 tracked modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → v0.8 → v0.9).

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">50%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:50%"></div></div>
     <span class="impl-status-detail">18/36 deliverables complete</span>
   </div>


.. list-table::
   :header-rows: 1

   * - **Module**
     - **Feature Req**
     - **Component Req**
     - **Req. Inspection**
   * - Baselibs
     - ✅ Available (14/14)

            | `baselibs <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/baselibs/requirements/index.rst>`__ (14)
     - ✅ Available (136/136 comp_req + 32/32 AoU)

            | `abi_compatible_data_types <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/docs/baselibs/components/abi_compatible_data_types/docs/requirements/index.rst>`__ (23)
            | `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/bitmanipulation/docs/requirements/index.rst>`__ (6)
            | `concurrency <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/concurrency/docs/requirements/index.rst>`__ (18)
            | `containers <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/containers/docs/requirements/index.rst>`__ (5)
            | `containers_rust <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/containers_rust/docs/requirements/index.rst>`__ (16)
            | `filesystem <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/filesystem/docs/requirements/index.rst>`__ (7)
            | `flatbuffers <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/flatbuffers/docs/requirements/index.rst>`__ (6)
            | `hash <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/hash/docs/requirements/index.rst>`__ (7)
            | `json <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/json/docs/requirements/index.rst>`__ (8)
            | `vajson <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/json/docs/vajson/requirements/index.rst>`__ (5)
            | `safecpp <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/language/safecpp/docs/requirements/index.rst>`__ (6)
            | `memory <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/memory/docs/requirements/index.rst>`__ (13)
            | `result <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/result/docs/requirements/index.rst>`__ (7)
            | `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/static_reflection_with_serialization/docs/requirements/index.rst>`__ (6)
            | `utils <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/utils/docs/requirements/index.rst>`__ (3)
     - 🔄 40% (4/10)

            | ✅ `baselibs <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/baselibs/requirements/chklst_req_inspection.rst>`__
            | ✅ `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/bitmanipulation/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `concurrency <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/concurrency/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `containers <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/containers/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `filesystem <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/filesystem/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `json <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/json/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `safecpp <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/language/safecpp/docs/requirements/chklst_req_inspection.rst>`__
            | ✅ `result <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/result/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/static_reflection_with_serialization/docs/requirements/chklst_req_inspection.rst>`__
            | ✅ `utils <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/utils/docs/requirements/chklst_req_inspection.rst>`__
   * - Communication
     - ✅ Available (64/64)

            | `message_passing <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/message_passing/dependability/requirements/feature_requirements.trlc>`__ (11) [TRLC]
            | `ipc <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/communication/ipc/requirements/index.rst>`__ (4)
            | `communication <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/communication/requirements/index.rst>`__ (49)
     - ✅ Available (363/363 comp_req + 38/38 AoU)

            | `message_passing <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/message_passing/dependability/requirements/component_requirements.trlc>`__ (29) [TRLC]
            | `message_passing <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/message_passing/dependability/requirements/external_component_requirements.trlc>`__ (4) [TRLC]
            | `ipc <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc.trlc>`__ (98) [TRLC]
            | `ipc_fields <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_fields.trlc>`__ (17) [TRLC]
            | `ipc_generic_proxy <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_generic_proxy.trlc>`__ (51) [TRLC]
            | `ipc_generic_skeleton <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_generic_skeleton.trlc>`__ (32) [TRLC]
            | `ipc_methods <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_methods.trlc>`__ (3) [TRLC]
            | `ipc_partial_restart <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_partial_restart.trlc>`__ (11) [TRLC]
            | `ipc_proxy <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_proxy.trlc>`__ (40) [TRLC]
            | `ipc_skeleton <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_skeleton.trlc>`__ (26) [TRLC]
            | `ipc_tracing <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/requirements/component_requirements/component_requirements_ipc_tracing.trlc>`__ (52) [TRLC]
            | `message_passing <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/message_passing/dependability/assumed_system/aous.trlc>`__ (1) [TRLC]
            | `com <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/mw/com/dependability/safety_analysis/aou.trlc>`__ (37) [TRLC]
     - ❌ Open
   * - Logging
     - ✅ Available (46/46)

            | `logging <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/log_and_trace/logging/requirements/index.rst>`__ (46)
     - ✅ Available (39/39 comp_req + 5/5 AoU)

            | `log <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/mw/log/docs/requirements/index.rst>`__ (18)
            | `datarouter <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/components/datarouter/requirements/index.rst>`__ (6)
            | `mw_log <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/components/mw_log/requirements/requirements.rst>`__ (15)
            | `log <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/mw/log/docs/safety_analysis/aou_requirements.rst>`__ (5)
     - 🔄 0% (0/3)

            | 🔄 `mw_log <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/components/mw_log/requirements/chklst_req_inspection.rst>`__
            | 🔄 `logging <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/log_and_trace/logging/requirements/chklst_req_inspection.rst>`__
            | 🔄 `log <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/mw/log/docs/requirements/chklst_req_inspection.rst>`__
   * - Persistency
     - ✅ Available (37/37)

            | `persistency <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/persistency/requirements/index.rst>`__ (37)
     - ✅ Available (35/35 comp_req)

            | `kvs <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/requirements/index.rst>`__ (35)
     - ✅ Available (2/2)

            | ✅ `persistency <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/persistency/requirements/chklst_req_inspection.rst>`__
            | ✅ `kvs <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/requirements/chklst_req_inspection.rst>`__
   * - Time
     - ✅ Available (15/15)

            | `time <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/time/requirements/index.rst>`__ (15)
     - 🔄 0% (0/4 AoU)

            | `time <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time/docs/requirements/requirements.rst>`__ (2)
            | `time_daemon <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time_daemon/docs/requirements/requirements.rst>`__ (2)
     - 🔄 0% (0/4)

            | 🔄 `time <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `time_daemon <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time_daemon/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `time_slave <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time_slave/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `ts_client <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/ts_client/docs/requirements/chklst_req_inspection.rst>`__
   * - Config Mgmt
     - ✅ Available (20/20)

            | `config_management <https://github.com/eclipse-score/config_management/blob/e0489b190ed6d2fa183b9a8063e2dba4f6378505/requirements/feature_requirements/feature_requirements.trlc>`__ (20) [TRLC]
     - ✅ Available (47/47 comp_req + 1/1 AoU)

            | `config_daemon <https://github.com/eclipse-score/config_management/blob/e0489b190ed6d2fa183b9a8063e2dba4f6378505/requirements/component_requirements/config_daemon/component_requirements.trlc>`__ (30) [TRLC]
            | `config_provider <https://github.com/eclipse-score/config_management/blob/e0489b190ed6d2fa183b9a8063e2dba4f6378505/requirements/component_requirements/config_provider/component_requirements.trlc>`__ (17) [TRLC]
            | `config_management <https://github.com/eclipse-score/config_management/blob/e0489b190ed6d2fa183b9a8063e2dba4f6378505/requirements/safety_analysis/aou.trlc>`__ (1) [TRLC]
     - ❌ Open
   * - Lifecycle
     - ✅ Available (32/32)

            | `lifecycle <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/lifecycle/requirements/index.rst>`__ (32)
     - ✅ Available (64/64 comp_req + 1/1 AoU)

            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/health_monitor/docs/requirements/index.rst>`__ (1)
            | `launch_manager <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/launch_manager/docs/requirements/requirements.rst>`__ (63)
     - 🔄 0% (0/2)

            | 🔄 `health_monitor <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/health_monitor/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `launch_manager <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/launch_manager/docs/requirements/chklst_req_inspection.rst>`__
   * - Kyron
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Security/Crypto
     - ✅ Available (41/41)

            | `security_crypto <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/security_crypto/requirements/index.rst>`__ (41)
     - 🔄 70% (1/1 comp_req + 6/9 AoU)

            | `iav_primula <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/iav_primula/docs/requirements/requirements.rst>`__ (1)
            | `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/docs/features/crypto/security_analysis/aou_requirements.rst>`__ (3)
            | `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/crypto/docs/requirements/requirements.rst>`__ (2)
            | `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/crypto/docs/security_analysis/aou_requirements.rst>`__ (2)
     - 🔄 0% (0/2)

            | 🔄 `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/crypto/docs/requirements/chklst_req_inspection.rst>`__
            | 🔄 `iav_primula <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/iav_primula/docs/requirements/chklst_req_inspection.rst>`__
   * - Diagnostic Services
     - ✅ Available (22/22)

            | `diagnostics <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/diagnostics/requirements/index.rst>`__ (22)
     - ❌ Open
     - ❌ Open
   * - NM
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Some/IP
     - ✅ Available (6/6)

            | `tc8_conformance <https://github.com/eclipse-score/inc_someip_gateway/blob/f701652c307d4d76073e49c2c9c3b74f588ce02d/docs/tc8_conformance/requirements.rst>`__ (1)
            | `some_ip_gateway <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/communication/some_ip_gateway/requirements/index.rst>`__ (5)
     - ✅ Available (8/8 comp_req)

            | `tc8_conformance <https://github.com/eclipse-score/inc_someip_gateway/blob/f701652c307d4d76073e49c2c9c3b74f588ce02d/docs/tc8_conformance/requirements.rst>`__ (8)
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
   :width: 880px

   Total Feature and Component Architecture elements across the 12 tracked modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → v0.8 → v0.9).

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">42%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:42%"></div></div>
     <span class="impl-status-detail">15/36 deliverables complete</span>
   </div>


.. list-table::
   :header-rows: 1

   * - **Module**
     - **Feature Arch**
     - **Component Arch**
     - **Arch. Inspection**
   * - Baselibs
     - ✅ Available (3/3)

            | `baselibs <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/docs/features/architecture/index.rst>`__ (2)
            | `baselibs <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/baselibs/architecture/index.rst>`__ (1)
     - 🔄 99% (197/198)

            | `abi_compatible_data_types <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/docs/baselibs/components/abi_compatible_data_types/docs/architecture/index.rst>`__ (1)
            | `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/bitmanipulation/docs/architecture/index.rst>`__ (12)
            | `concurrency <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/concurrency/docs/architecture/index.rst>`__ (33)
            | `containers <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/containers/docs/architecture/index.rst>`__ (9)
            | `containers_rust <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/containers_rust/docs/architecture/index.rst>`__ (27)
            | `containers_rust <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/containers_rust/docs/requirements/index.rst>`__ (1)
            | `filesystem <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/filesystem/docs/architecture/index.rst>`__ (25)
            | `flatbuffers <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/flatbuffers/docs/architecture/index.rst>`__ (1)
            | `hash <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/hash/docs/requirements/index.rst>`__ (1)
            | `json <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/json/docs/architecture/index.rst>`__ (7)
            | `vajson <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/json/docs/vajson/architecture/index.rst>`__ (1)
            | `safecpp <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/language/safecpp/docs/architecture/index.rst>`__ (23)
            | `memory <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/memory/docs/architecture/index.rst>`__ (6)
            | `result <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/result/docs/architecture/index.rst>`__ (6)
            | `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/static_reflection_with_serialization/docs/architecture/index.rst>`__ (11)
            | `utils <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/utils/docs/architecture/index.rst>`__ (6)
            | `baselibs <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/baselibs/architecture/index.rst>`__ (28)
     - 🔄 80% (8/10)

            | ✅ `baselibs <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/docs/features/architecture/chklst_arc_inspection.rst>`__
            | ✅ `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/bitmanipulation/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `concurrency <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/concurrency/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `containers <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/containers/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `filesystem <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/filesystem/docs/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `json <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/json/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `safecpp <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/language/safecpp/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `result <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/result/docs/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/static_reflection_with_serialization/docs/architecture/chklst_arc_inspection.rst>`__
            | ✅ `utils <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/utils/docs/architecture/chklst_arc_inspection.rst>`__
   * - Communication
     - ✅ Available (3/3)

            | `communication <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/communication/architecture/index.rst>`__ (2)
            | `ipc <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/communication/ipc/architecture/index.rst>`__ (1)
     - ✅ Available (17/17)

            | `communication <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/communication/architecture/index.rst>`__ (1)
            | `configuration <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/modules/communication/configuration/docs/architecture/index.rst>`__ (1)
            | `frontent <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/modules/communication/frontent/docs/architecture/index.rst>`__ (10)
            | `ipc_binding <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/modules/communication/ipc_binding/docs/architecture/index.rst>`__ (1)
            | `message_passing <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/modules/communication/message_passing/docs/architecture/index.rst>`__ (3)
            | `mock_binding <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/modules/communication/mock_binding/docs/architecture/index.rst>`__ (1)
     - ❌ Open
   * - Logging
     - ✅ Available (2/2)

            | `logging <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/features/logging/architecture/index.rst>`__ (1)
            | `logging <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/log_and_trace/logging/architecture/index.rst>`__ (1)
     - ✅ Available (13/13)

            | `log <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/mw/log/docs/architecture/component_architecture.rst>`__ (2)
            | `rust_bridge_design <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/mw/log/docs/detailed_design/rust_bridge_design.rst>`__ (3)
            | `datarouter <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/components/datarouter/index.rst>`__ (1)
            | `mw_log <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/components/mw_log/architecture/component_architecture.rst>`__ (4)
            | `logging <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/log_and_trace/logging/architecture/index.rst>`__ (3)
     - 🔄 0% (0/2)

            | 🔄 `logging <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/features/logging/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `log <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/mw/log/docs/architecture/chklst_arc_inspection.rst>`__
   * - Persistency
     - ✅ Available (9/9)

            | `persistency <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/docs/features/persistency/architecture/index.rst>`__ (8)
            | `persistency <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/persistency/architecture/index.rst>`__ (1)
     - 🔄 40% (2/5)

            | `persistency <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/docs/features/persistency/architecture/index.rst>`__ (1)
            | `kvs <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/architecture/index.rst>`__ (3)
            | `persistency <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/persistency/architecture/index.rst>`__ (1)
     - 🔄 0% (0/2)

            | 🔄 `persistency <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/docs/features/persistency/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `kvs <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/architecture/chklst_arc_inspection.rst>`__
   * - Time
     - ✅ Available (1/1)

            | `time <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/time/architecture/index.rst>`__ (1)
     - ✅ Available (2/2)

            | `time <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time/docs/index.rst>`__ (1)
            | `ts_client <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/ts_client/docs/index.rst>`__ (1)
     - ❌ Open
   * - Config Mgmt
     - ✅ Available (1/1)

            | `config_mgmt <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/configuration/config_mgmt/architecture/index.rst>`__ (1)
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - ✅ Available (7/7)

            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/docs/features/lifecycle/architecture/health_monitor.rst>`__ (2)
            | `lifecycle <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/docs/features/lifecycle/architecture/index.rst>`__ (1)
            | `launch_manager <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/docs/features/lifecycle/architecture/launch_manager.rst>`__ (3)
            | `lifecycle <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/lifecycle/architecture/index.rst>`__ (1)
     - ✅ Available (45/45)

            | `launch_manager_configuration <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/docs/features/lifecycle/architecture/launch_manager_configuration.rst>`__ (1)
            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/health_monitor/docs/architecture/index.rst>`__ (16)
            | `launch_manager <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/launch_manager/docs/architecture/component_architecture.rst>`__ (2)
            | `lifecycle <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/lifecycle/architecture/index.rst>`__ (26)
     - 🔄 0% (0/3)

            | 🔄 `lifecycle <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/docs/features/lifecycle/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `health_monitor <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/health_monitor/docs/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `launch_manager <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/launch_manager/docs/architecture/chklst_arc_inspection.rst>`__
   * - Kyron
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Security/Crypto
     - ✅ Available (1/1)

            | `security_crypto <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/security_crypto/architecture/index.rst>`__ (1)
     - 🔄 16% (4/25)

            | `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/crypto/docs/architecture/interfaces.rst>`__ (21)
            | `iav_primula <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/iav_primula/docs/architecture/component_architecture.rst>`__ (4)
     - 🔄 0% (0/3)

            | 🔄 `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/docs/features/crypto/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/crypto/docs/architecture/chklst_arc_inspection.rst>`__
            | 🔄 `iav_primula <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/iav_primula/docs/architecture/chklst_arc_inspection.rst>`__
   * - Diagnostic Services
     - ✅ Available (1/1)

            | `diagnostics <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/features/diagnostics/architecture/index.rst>`__ (1)
     - ❌ Open
     - ❌ Open
   * - NM
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Some/IP
     - ✅ Available (1/1)

            | `inc_someip_gateway <https://github.com/eclipse-score/inc_someip_gateway/blob/f701652c307d4d76073e49c2c9c3b74f588ce02d/docs/architecture/features.rst>`__ (1)
     - ✅ Available (4/4)

            | `inc_someip_gateway <https://github.com/eclipse-score/inc_someip_gateway/blob/f701652c307d4d76073e49c2c9c3b74f588ce02d/docs/architecture/components.rst>`__ (4)
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
   :width: 880px

   Estimated Lines of Code across the 12 tracked modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → v0.8 → v0.9).

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">46%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:46%"></div></div>
     <span class="impl-status-detail">22/48 deliverables complete</span>
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

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~322,600 LOC)

            | 1,667 source files — cpp 178,100, h 96,100, hpp 30,500, rs 16,100
     - 🔄 Draft (1 design doc(s), 0 ``dd`` elements)

            | `CADS <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/json/docs/vajson/detailed_design/CADS.rst>`__
     - 🔄 0% (0/9)

            | 🔄 `bitmanipulation <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/bitmanipulation/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `concurrency <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/concurrency/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `containers <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/containers/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `filesystem <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/filesystem/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `json <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/json/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `safecpp <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/language/safecpp/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `result <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/result/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `static_reflection_with_serialization <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/static_reflection_with_serialization/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `utils <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/utils/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Communication
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~363,000 LOC)

            | 1,734 source files — cpp 245,400, h 82,000, py 22,300, rs 13,400
     - 🔄 Draft (1 design doc(s), 0 ``dd`` elements)

            | `lola <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/modules/communication/lola/docs/detailed_design/index.rst>`__
     - ❌ Open
   * - Logging
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~79,700 LOC)

            | 454 source files — cpp 56,100, h 20,200, py 1,800, rs 1,400
     - 🔄 Draft (2 design doc(s), 0 ``dd`` elements)

            | `log <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/mw/log/docs/detailed_design/index.rst>`__
            | `mw_log <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/components/mw_log/detailed_design/index.rst>`__
     - 🔄 0% (0/2)

            | 🔄 `mw_log <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/components/mw_log/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `log <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/score/mw/log/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Persistency
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~18,000 LOC)

            | 76 source files — rs 8,800, cpp 6,000, py 2,000, hpp 1,300
     - 🔄 Draft (1 design doc(s), 0 ``dd`` elements)

            | `kvs <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/detailed_design/index.rst>`__
     - 🔄 0% (0/1)

            | 🔄 `kvs <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/score/kvs/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Time
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~26,600 LOC)

            | 239 source files — cpp 16,000, h 9,900, py 700
     - 🔄 Draft (4 design doc(s), 0 ``dd`` elements)

            | `time <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time/docs/detailed_design/index.rst>`__
            | `time_daemon <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time_daemon/docs/detailed_design/index.rst>`__
            | `time_slave <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time_slave/docs/detailed_design/index.rst>`__
            | `ts_client <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/ts_client/docs/detailed_design/index.rst>`__
     - 🔄 0% (0/4)

            | 🔄 `time <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `time_daemon <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time_daemon/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `time_slave <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/time_slave/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `ts_client <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/score/ts_client/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Config Mgmt
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~23,300 LOC)

            | 156 source files — cpp 15,900, h 5,200, py 1,900, hpp 300
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~68,200 LOC)

            | 367 source files — cpp 30,400, hpp 18,400, rs 10,400, py 6,200
     - 🔄 Draft (2 design doc(s), 0 ``dd`` elements)

            | `health_monitor <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/health_monitor/docs/detailed_design/index.rst>`__
            | `launch_manager <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/launch_manager/docs/detailed_design/index.rst>`__
     - 🔄 0% (0/2)

            | 🔄 `health_monitor <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/health_monitor/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `launch_manager <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/score/launch_manager/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Kyron
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~38,600 LOC)

            | 166 source files — rs 32,100, py 6,500
     - ❌ Open
     - ❌ Open
   * - Security/Crypto
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~82,700 LOC)

            | 375 source files — hpp 28,300, cpp 27,700, rs 23,800, h 2,100
     - 🔄 Draft (2 design doc(s), 0 ``dd`` elements)

            | `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/crypto/docs/detailed_design/index.rst>`__
            | `iav_primula <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/iav_primula/docs/detailed_design/index.rst>`__
     - 🔄 0% (0/2)

            | 🔄 `crypto <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/crypto/docs/detailed_design/chklst_impl_inspection.rst>`__
            | 🔄 `iav_primula <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/score/iav_primula/docs/detailed_design/chklst_impl_inspection.rst>`__
   * - Diagnostic Services
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - NM
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ❌ Open
     - ❌ Open
     - ❌ Open
   * - Some/IP
     - ✅ Available

            | `software_development <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/platform_management_plan/software_development.rst>`__
     - ✅ Available (~37,300 LOC)

            | 172 source files — cpp 22,400, hpp 10,600, py 2,500, h 1,600
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
   :width: 1260px

   Test counts and coverage across the 12 tracked modules per release (v0.5.0-beta → v0.6.0 → v0.7.0 → v0.8 → v0.9).

.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">42%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:42%"></div></div>
     <span class="impl-status-detail">35/84 deliverables complete</span>
   </div>

.. note::

   **C0/C1 Coverage** data is sourced from the ``reference_integration``
   CI (*Code Quality & Documentation* workflow,
   ``bazel coverage --config=ferrocene-coverage``). C0 = line coverage,
   C1 = branch coverage. Rust coverage reports line coverage only.
   Modules that are not pinned in ``known_good.json`` and therefore not
   built by the ``reference_integration`` CI (Security/Crypto, Some/IP)
   are marked 🔄 *Module CI only* and link to their own repository
   workflows instead.

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

.. note::

   **Module Verification Report** additionally lists generated
   traceability evidence where a module produces it. Communication builds
   a *L.O.B.S.T.E.R. Traceability Report* (LOBSTER 1.0.6, pulled by
   ``third_party/lobster/lobster.bzl``) from the ``dependable_element``
   Bazel rule in ``eclipse-score/tooling``. The report is assembled during
   ``bazel build //docs/sphinx:sphinx_doc`` and published to GitHub Pages
   by ``deploy_docs.yml`` — it is **not** checked into the repository, so
   it does not appear in the pinned source tree. It currently covers the
   ``message_passing`` dependable element only; there is no equivalent
   report for LoLa / ``mw::com``.


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
     - ✅ 23,976 tests

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
            | 23,926 passed, 50 skipped
     - 🔄 C0 94.9% / C1 61.7% (C++)

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - ✅ 6 test cases

            | 3 files — ``examples/integration/``
     - ❌ Open
     - ✅ 0 findings

            | `lint.yml <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/.github/workflows/lint.yml>`__
     - ✅ ASan, LSan, UBSan

            | `sanitizers_linux.yml <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/.github/workflows/sanitizers_linux.yml>`__
     - 🔄 Draft

            | `module_verification_report <https://github.com/eclipse-score/baselibs/blob/33aad37ad3d12591b0d662ee37e430eedb1c273c/docs/verification_report/module_verification_report.rst>`__
   * - Communication
     - ✅ 3,530 tests

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - 🔄 C0 83.0% / C1 52.6% (C++)

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - ✅ 111 test cases

            | 234 files — ``score/mw/com/test/``, ``score/mw/com/gateway/transport_layer/sample/test/``, ``quality/integration_testing/test/``
     - ❌ Open
     - ✅ 0 findings

            | `nightly_quality.yml <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/.github/workflows/nightly_quality.yml>`__
     - ✅ ASan, LSan, TSan, UBSan

            | `build_and_test_host.yml <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/.github/workflows/build_and_test_host.yml>`__
     - 🔄 Draft

            | `module_verification_report <https://github.com/eclipse-score/score/blob/6d65a262c2329328cb9cbdd276bb143b417c54a4/docs/modules/communication/docs/verification/module_verification_report.rst>`__
            | ✅ `LOBSTER traceability report (message_passing) <https://eclipse-score.github.io/communication/latest/docs/sphinx/dependable_element_message_passing_index/traceability_report/index.html>`__ — generated by `dependable_element_message_passing <https://github.com/eclipse-score/communication/blob/b22ed6d314313c87eb06ca916efda9a71ec53cc6/score/message_passing/dependability/BUILD>`__
   * - Logging
     - ✅ 334 tests

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - 🔄 C0 96.6% / C1 75.4% (C++), C0 39.9% (Rust)

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - ✅ 8 test cases

            | 11 files — ``score/test/component/``
     - ✅ 2 test cases

            | ``feature_integration_tests/``
     - ✅ 0 findings

            | `clang_tidy.yml <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/.github/workflows/clang_tidy.yml>`__
     - ✅ ASan, LSan, TSan, UBSan

            | `sanitizers.yml <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/.github/workflows/sanitizers.yml>`__
     - 🔄 Draft

            | `module_verification_report <https://github.com/eclipse-score/logging/blob/6d8fcb3734e3f3307615bae5495d2d3a82b0b8c4/docs/verification_report/module_verification_report.rst>`__
   * - Persistency
     - ✅ 95 tests

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - 🔄 C0 94.7% / C1 63.0% (C++), C0 92.7% (Rust)

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - ✅ 44 test cases

            | 9 files — ``score/kvs/tests/test_cases/tests/``
     - ✅ 50 test cases

            | ``feature_integration_tests/``
     - ✅ 0 findings

            | `clippy.yml <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/.github/workflows/clippy.yml>`__
     - ❌ Open
     - ✅ Available

            | `module_verification_report <https://github.com/eclipse-score/persistency/blob/9ae529ba9f413976ff5c9948c6490afa51bbfdc3/docs/verification_report/module_verification_report.rst>`__
   * - Time
     - ✅ 335 tests

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - 🔄 C0 90.3% / C1 61.4% (C++)

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - ✅ 7 test cases

            | 5 files — ``score/``
     - ❌ Open
     - 🔄 clang-tidy ✅, CodeQL ❌ failing

            | `clang-tidy.yml <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/.github/workflows/clang-tidy.yml>`__
            | `codeql.yml <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/.github/workflows/codeql.yml>`__
     - ✅ ASan, LSan, UBSan

            | `sanitizers.yml <https://github.com/eclipse-score/time/blob/c4f0194a3b496757e5c193ed8618fc3f45a868a5/.github/workflows/sanitizers.yml>`__
     - ❌ Open
   * - Config Mgmt
     - ✅ 238 tests

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - 🔄 C0 92.8% / C1 64.1% (C++)

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - ❌ Open
     - ❌ Open
     - ✅ 0 findings

            | `static-analysis.yml <https://github.com/eclipse-score/config_management/blob/e0489b190ed6d2fa183b9a8063e2dba4f6378505/.github/workflows/static-analysis.yml>`__
     - ❌ Open
     - ❌ Open
   * - Lifecycle
     - ✅ 478 tests

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
            | 476 passed, 2 skipped
     - 🔄 C0 77.4% / C1 50.7% (C++), C0 53.5% (Rust)

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - ✅ 58 test cases

            | 58 files — ``tests/integration/``
     - ❌ Open
     - ✅ 0 findings

            | `on-pr.yml <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/.github/workflows/on-pr.yml>`__
     - ✅ ASan, LSan, TSan, UBSan

            | `on-pr.yml <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/.github/workflows/on-pr.yml>`__
     - 🔄 Draft

            | `verification_report <https://github.com/eclipse-score/lifecycle/blob/9613f52b1ec1a3f169be79d9e6ef0948c5e19596/docs/verification_report/index.rst>`__
   * - Kyron
     - 🔄 3 tests

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
            | bazel-scoped unit tests only
     - 🔄 C0 50.4% (Rust)

            | `reference CI run <https://github.com/eclipse-score/reference_integration/actions/runs/33764114548>`__
     - ✅ 209 test cases

            | 25 files — ``tests/test_cases/tests/``
     - ❌ Open
     - ✅ 0 findings

            | `lint_fmt_clippy.yml <https://github.com/eclipse-score/kyron/blob/394b232a8db7fb77db0ff16e9c26ec31c7759efd/.github/workflows/lint_fmt_clippy.yml>`__
     - ❌ Open
     - ❌ Open
   * - Security/Crypto
     - 🔄 Module CI only

            | `test_linux.yml <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/.github/workflows/test_linux.yml>`__
     - ❌ Open
     - ✅ 10 test cases

            | 6 files — ``score/tests/integration_tests/``
     - ❌ Open
     - ✅ 0 findings

            | `on-pr.yml <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/.github/workflows/on-pr.yml>`__
     - ❌ Open
     - 🔄 Draft

            | `module_verification_report <https://github.com/eclipse-score/inc_security_crypto/blob/1e438b2d06041b9e1088c2144b865f237e0382c4/docs/verification_report/module_verification_report.rst>`__
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
     - 🔄 Module CI only

            | `build_and_test_host.yml <https://github.com/eclipse-score/inc_someip_gateway/blob/f701652c307d4d76073e49c2c9c3b74f588ce02d/.github/workflows/build_and_test_host.yml>`__
     - 🔄 Module CI only

            | `coverage.yml <https://github.com/eclipse-score/inc_someip_gateway/blob/f701652c307d4d76073e49c2c9c3b74f588ce02d/.github/workflows/coverage.yml>`__
     - ✅ 11 test cases

            | 8 files — ``quality/integration_testing/``
     - ❌ Open
     - ✅ 0 findings

            | `static-code-analysis.yml <https://github.com/eclipse-score/inc_someip_gateway/blob/f701652c307d4d76073e49c2c9c3b74f588ce02d/.github/workflows/static-code-analysis.yml>`__
     - ✅ ASan, LSan, TSan, UBSan

            | `build_and_test_host.yml <https://github.com/eclipse-score/inc_someip_gateway/blob/f701652c307d4d76073e49c2c9c3b74f588ce02d/.github/workflows/build_and_test_host.yml>`__
     - ❌ Open

.. admonition:: Platform Verification Report
   :class: important platform-ver-report

   Platform Verification Report — ❌ **Open** (single project-wide deliverable;
   not yet published at the pinned ``score`` ref)
