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

.. _process_requirements_safety_analysis:

Safety Analysis Process Requirements
====================================

.. note:: Safety analysis is used as a umbrella term for the methods DFA (Dependent Failure Analysis) and FMEA (Failure Mode and Effects Analysis).

.. gd_req:: Safety Analysis Structure
   :id: gd_req__saf_structure
   :status: valid
   :tags: done_automation, safety_analysis
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__support_6432

   Safety Analysis (FMEA and DFA) shall be hierarchically grouped into different levels.

   Following levels are defined:

      * Platform DFA
      * Feature DFA/FMEA
      * Component DFA/FMEA

.. _process_requirements_safety_analysis_attributes:

Process Safety Analysis Attributes
----------------------------------

.. gd_req:: Safety Analysis attribute: UID
   :id: gd_req__saf_attr_uid
   :status: valid
   :tags: done_automation, attribute, mandatory
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__support_6425, std_req__iso26262__support_6432

   Each Safety Analysis shall have a unique ID. It shall be in a format which is also human readable and consists of

      * type of Safety Analysis (DFA or FMEA)
      * name of analysed structural element (e.g. Persistency, FEO, etc.)
      * element descriptor (e.g. KVS__Open KVS or KVS__GetKeyValue)

   The naming convention shall be defined in the project and shall be used consistently.

.. gd_req:: Safety Analysis attribute: title
   :id: gd_req__saf_attr_title
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__support_6424

   The title of the Safety Analysis shall provide a short summary of the description

.. gd_req:: Safety Analysis attribute: mitigated by
   :id: gd_req__saf_attr_mitigated_by
   :status: valid
   :tags: prio_1_automation, attribute, optional
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_844, std_req__iso26262__analysis_746, std_req__iso26262__analysis_747

   Each violation shall have an associated mitigation (e.g. prevention, detection or mitigation) or AoU.
   If mitigation has not yet been implemented, do not use this option.
   If status == valid then mitigated_by is mandatory.

.. gd_req:: Safety Analysis attribute: mitigation issue
   :id: gd_req__saf_attr_mitigation_issue
   :status: valid
   :tags: prio_1_automation, attribute, optional
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_844, std_req__iso26262__analysis_746, std_req__iso26262__analysis_747

   If a new mitigation (e.g. prevention, detection or mitigation) is needed link to the issue and keep status invalid until mitigation is sufficient.

.. gd_req:: Safety Analysis attribute: sufficient
   :id: gd_req__saf_attr_sufficient
   :status: valid
   :tags: prio_1_automation, attribute, mandatory
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_848, std_req__iso26262__analysis_749, std_req__isopas8926__44431, std_req__isopas8926__44432

   The mitigation(s) (e.g. prevention, detection or mitigation) shall be rated as sufficient with <yes> or <no>.
   A mitigation can only be sufficient if a mitigation is linked via the attribute mitigation.

.. gd_req:: Safety Analysis content: argument
   :id: gd_req__saf_argument
   :status: valid
   :tags: prio_1_automation, attribute, mandatory
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_848, std_req__iso26262__analysis_749, std_req__isopas8926__44433

   The argument shall describe why the mitigation (e.g. prevention, detection or mitigation) is sufficient or not. If it is not sufficient, the argument shall describe how the mitigation
   can be improved to achieve sufficiency. The argument shall be written in the content.

.. gd_req:: Safety Analysis attribute: status
   :id: gd_req__saf_attr_status
   :status: valid
   :tags: prio_1_automation, attribute, mandatory
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_848, std_req__iso26262__analysis_749, std_req__isopas8926__44431, std_req__isopas8926__44432

   Each safety analysis shall have the status invalid until the analysis is finished. The status shall be set to valid if the analysis is finished and all issues are closed.

.. gd_req:: Safety Analysis attribute: failure effect
   :id: gd_req__saf_attr_feffect
   :status: valid
   :tags: prio_1_automation, attribute, mandatory
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_742

   Every Safety Analysis shall have a short description of the failure effect (e.g. failure lead to an unintended actuation of the analysed element)

.. _process_requirements_safety_analysis_linkage:

Safety Analysis Linkage
'''''''''''''''''''''''

.. gd_req:: Safety Analysis Linkage check
   :id: gd_req__saf_linkage_check
   :status: valid
   :tags: prio_1_automation, attribute, automated
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_842, std_req__iso26262__software_7410, std_req__iso26262__software_7411

   Safety Analysis shall be linked to the architecture view on the corresponding level via the attribute violates.

.. gd_req:: Safety Analysis Linkage
   :id: gd_req__saf_linkage
   :status: valid
   :tags: prio_2_automation, attribute, automated
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_842, std_req__iso26262__software_7410, std_req__iso26262__software_7411

   Each Safety Analysis shall be automatically linked (inverse direction) to the corresponding architecture view via the "violates by" linkage.

.. gd_req:: Safety Analysis attribute: check Requirements linkage
   :id: gd_req__saf_attr_requirements_check
   :status: valid
   :tags: prio_1_automation, attribute, automated
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_842, std_req__iso26262__software_7410, std_req__iso26262__software_7411

   Safety Analysis shall be linked to a requirement on the corresponding level via the attribute "mitigated by".

.. gd_req:: Safety Analysis attribute: Requirements linkage
   :id: gd_req__saf_attr_requirements
   :status: valid
   :tags: prio_2_automation, attribute, automated
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_842, std_req__iso26262__software_7410, std_req__iso26262__software_7411

   Each Safety Analysis shall be automatically linked to the corresponding Safety Requirement via the mitigates linkage.

.. gd_req:: Safety Analysis attribute: link to Aou
   :id: gd_req__saf_attr_aou
   :status: valid
   :tags: prio_1_automation, attribute, automated
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_845

   It shall be possible to link Aou.

.. gd_req:: Safety Analysis attribute: versioning
   :id: gd_req__saf_attr_ver
   :status: valid
   :tags: prio_2_automation, attribute, automated
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__support_6425, std_req__iso26262__support_6434

   It shall be possible to detect any differences in mandatory attributes compared to the versioning: :need:`gd_req__saf_attr_mandatory`

.. gd_req:: Safety Analysis Linkage status check
   :id: gd_req__saf_linkage_status_check
   :status: valid
   :tags: prio_3_automation, attribute, automated
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_842, std_req__iso26262__software_7410, std_req__iso26262__software_7411

   It shall be checked that safety analysis can only be linked against valid safety elements (architecture view, requirement, AoU). A valid safety element has the attribute 'status == valid' and safety != QM.

.. _process_requirements_safety_analysis_checks:

Safety Analysis Checks
''''''''''''''''''''''

.. gd_req:: Safety Analysis mandatory attributes provided
   :id: gd_req__saf_attr_mandatory
   :status: valid
   :tags: prio_1_automation, attribute, check
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_848, std_req__iso26262__analysis_749

   It shall be checked if all mandatory attributes for each Safety Analysis are provided by the user. For all Safety Analysis following attributes shall be mandatory:

   .. needtable:: Overview mandatory Safety Analysis attributes
      :filter: "mandatory" in tags and "attribute" in tags and "safety_analysis" in tags and type == "gd_req"
      :style: table
      :columns: title
      :colwidths: 30


.. gd_req:: Safety Analysis linkage safety
   :id: gd_req__saf_linkage_safety
   :status: valid
   :tags: prio_2_automation, attribute, check
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_848, std_req__iso26262__analysis_749

   It shall be checked that Safety Analysis (DFA and FMEA) can only be linked via mitigate_by against
   <Feature | Component | AoU> Requirements with at least one Requirement with the same ASIL or with a higher ASIL
   as the corresponding ASIL of the Feature or Component that is analysed and linked via violates.


.. gd_req:: Safety Analysis finalization check
   :id: gd_req__saf_finalization_check
   :status: valid
   :tags: prio_2_automation, attribute, automated
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_848, std_req__iso26262__analysis_749, std_req__isopas8926__44431, std_req__isopas8926__44432

    It shall be checked if all artifacts of the analysis are "valid" and "sufficient".

DFA Process Requirements
========================

.. gd_req:: DFA attribute: failure ID
   :id: gd_req__saf_attr_failure_id
   :status: valid
   :tags: prio_1_automation, attribute, mandatory
   :satisfies: wf__analyse_platform_featarch, wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__support_6425, std_req__iso26262__support_6432

   Each DFA shall have a failure ID. The failure ID is used to identify the related fault <:need:`gd_guidl__dfa_failure_initiators`>.
   The failure ID links to the corresponding failure initiator which describes how a potential violation can occur.


FMEA Process Requirements
=========================

.. gd_req:: FMEA attribute: fault ID
   :id: gd_req__saf_attr_fault_id
   :status: valid
   :tags: prio_1_automation, attribute, mandatory
   :satisfies: wf__analyse_featarch, wf__analyse_comparch
   :complies: std_req__iso26262__analysis_848

   Each FMEA shall have a fault ID. The fault ID is used to identify the related fault <:need:`gd_guidl__fault_models`>.
   The fault ID links to the corresponding fault which describes how a potential violation can occur.


.. needextend:: docname is not None and "process_areas/safety_analysis" in docname
   :+tags: safety_analysis
