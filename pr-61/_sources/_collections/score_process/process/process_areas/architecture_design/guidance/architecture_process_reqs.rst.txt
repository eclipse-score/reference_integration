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

.. _arch_process_requirements:

Process Requirements
====================

Architectural Model
-------------------

.. gd_req:: Architecture Modeling
   :id: gd_req__arch_model
   :status: valid
   :tags: manual_prio_1
   :complies: std_req__iso26262__support_6431, std_req__iso26262__support_6432
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   For architecture design a model based approach should be used. The model shall consist of different architectural elements.

.. gd_req:: Hierarchical structure of architectural elements
   :id: gd_req__arch_hierarchical_structure
   :status: valid
   :tags: done_automation
   :complies: std_req__iso26262__support_6431, std_req__iso26262__support_6432
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   The architectural elements shall be hierarchically structured on two levels:

   * Feature Level (=Logical Level)
   * Component Level

.. gd_req:: Structuring of the architectural elements
   :id: gd_req__arch_build_blocks
   :status: valid
   :tags: done_automation
   :complies: std_req__iso26262__support_6431, std_req__iso26262__support_6432
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   Following architectural elements shall be defined on the respective hierarchical level:

   * Logical Level

     * Feature (feature_arc_sta)
     * Logical Interface (logic_arc_int)
     * Logical Interface Operation (logic_arc_int_op)

   * Component Level

     * Component (comp_arc_sta)
     * Interface (real_arc_int)
     * Interface Operation (real_arc_int_op)

.. gd_req:: Correlations of the architectural building blocks
   :id: gd_req__arch_build_blocks_corr
   :status: valid
   :tags: done_automation
   :complies: std_req__iso26262__support_6431, std_req__iso26262__support_6432
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   For modeling the viewpoints following relations shall be used:

   .. figure:: ../_assets/metamodel_architectural_design.drawio.svg
      :width: 100%
      :align: center
      :alt: Definition of the Metamodel for Architectural Design

Architectural Views
-------------------

.. gd_req:: Architecture Viewpoints
   :id: gd_req__arch_viewpoints
   :status: valid
   :tags: manual_prio_1
   :complies: std_req__iso26262__support_6432, std_req__iso26262__software_742
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   The architecture shall be shown on following views on each architectural level:

   * Package Diagram (feat_arc_sta, comp_arc_sta)
   * Sequence Diagram (feat_arc_dyn, comp_arc_dyn)
   * Interface View (logic_arc_int, real_arc_int)

   Only an additional view  shall be created on module level.

Attributes of Architectural Elements
------------------------------------

.. gd_req:: Architecture attribute: UID
   :id: gd_req__arch_attribute_uid
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :complies: std_req__iso26262__support_6425, std_req__iso26262__support_6432
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   Each architectural element shall have a unique ID. It shall be in a format which is also human readable and consists of

      * type of architectural element
      * structural element (e.g. some part of the feature tree, component acronym)
      * keyword describing the content of the architectural element

   Check your project's naming conventions (should be called "doc__naming_conventions")

.. gd_req:: Architecture attribute: security
   :id: gd_req__arch_attr_security
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   Each architectural element shall have a security relevance identifier:

      * Yes
      * No

.. gd_req:: Architecture attribute: safety
   :id: gd_req__arch_attr_safety
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :complies: std_req__iso26262__support_6421, std_req__iso26262__support_6425, std_req__iso26262__software_746
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   Each architectural element shall have a automotive safety integrity level (ASIL) identifier:

      * QM
      * ASIL_B

.. gd_req:: Architecture attribute: status
   :id: gd_req__arch_attr_status
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :complies: std_req__iso26262__support_6425
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   Each architectural element shall have a status:

      * valid
      * invalid

Traceability to Requirements
----------------------------

.. gd_req:: Architecture attribute: fulfils
   :id: gd_req__arch_attr_fulfils
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :complies: std_req__iso26262__support_6425
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   Each architectural element shall be linked to a requirement.

.. gd_req:: Architecture traceability
   :id: gd_req__arch_traceability
   :status: valid
   :tags: manual_prio_2
   :complies: std_req__iso26262__support_6432
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   Requirements shall be fulfilled by an architectural element on the corresponding level.

   **Examples:**

   * feat_req <-> feat_arc_(sta|dyn), logic_arc_(int|int_op)
   * comp_req <-> comp_arc_(sta|dyn), real_arc_(int|int_op)

   .. note::
      In general the traceability is visualized in :ref:`general_concepts_traceability`

Checks for Architectural Design
-------------------------------

.. gd_req:: Architecture mandatory attributes
   :id: gd_req__arch_attr_mandatory
   :status: valid
   :tags: prio_1_automation, attribute, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked if all mandatory attributes for each architectural element are provided by the user. For all elements following attributes shall be mandatory:

   .. needtable:: Overview mandatory requirement attributes
      :filter: "mandatory" in tags and "attribute" in tags and "architecture_design" in tags and type == "gd_req" and is_external == False
      :style: table
      :columns: title
      :colwidths: 30

.. gd_req:: Architecture linkage metamodel
   :id: gd_req__arch_linkage_safety
   :status: valid
   :tags: prio_1_automation, attribute, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked that every valid safety architectural element is linked according to the defined model :need:`gd_req__arch_build_blocks_corr`.

.. gd_req:: Architecture linkage safety
   :id: gd_req__arch_linkage_safety_trace
   :status: valid
   :tags: prio_1_automation, attribute, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked that valid safety architectural elements (Safety != QM) can only be linked against valid safety architectural elements.

.. gd_req:: Architecture linkage security
   :id: gd_req__arch_linkage_security_trace
   :status: valid
   :tags: prio_2_automation, attribute, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked that security relevant architectural elements (Security == YES) can only be linked against security relevant architectural elements.

.. gd_req:: Architecture linkage requirement
   :id: gd_req__arch_linkage_requirement
   :status: valid
   :tags: prio_1_automation, attribute, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked that each architectural element (safety!=QM) is linked against at least one safety requirement (safety!=QM).
   It shall be checked that architectural elements with safety=QM are not linked against safety requirements (safety!=QM).

.. gd_req:: Architecture linkage requirement type
   :id: gd_req__arch_linkage_requirement_type
   :status: valid
   :tags: prio_3_automation, attribute, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked that requirements of a respective type can only be linked to architectural elements according to following traceability:

   * Functional requirements <-> static / dynamic architectural elements (feat_arc_sta, feat_arc_dyn)
   * Interface requirements <-> interface architectural elements (logic_arc_int, logic_arc_int_op)

.. gd_req:: Architecture check consistency modules
   :id: gd_req__arch_consistency_model
   :status: valid
   :tags: prio_2_automation, model, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked if all mentioned SW components are available in the modules repository.

.. gd_req:: Architecture check consistency interfaces
   :id: gd_req__arch_consistency_interf
   :status: valid
   :tags: prio_2_automation, model, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked if all mentioned component interfaces are available in the modules repository.

.. gd_req:: Architecture check consistency dynamic architecture
   :id: gd_req__arch_consistency_dynamic
   :status: valid
   :tags: prio_3_automation, model, check
   :satisfies: wf__cr_mt_featarch, wf__cr_mt_comparch

   It shall be checked if all SW components which are mentioned in the dynamic architecture are defined in the static architecture.
