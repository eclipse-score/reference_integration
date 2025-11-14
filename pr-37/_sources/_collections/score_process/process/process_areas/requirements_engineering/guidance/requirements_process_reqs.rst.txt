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

.. _process_requirements:

Process Requirements
====================

.. gd_req:: Requirements Structure
   :id: gd_req__req_structure
   :status: valid
   :tags: done_automation, structure
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_proc_tool, wf__req_feat_aou, wf__req_comp_aou
   :complies: std_req__iso26262__support_6431, std_req__iso26262__support_6432

   Requirements shall be hierarchically grouped into three levels.

   Following levels are defined:

      * Stakeholder requirement
      * Feature requirement
      * Component requirement

   Additionally there shall be the following logical groups of requirements:
      * Assumption of use requirement
      * Process requirement
      * Tool requirement

.. _process_requirement_attributes:

Process Requirement Attributes
------------------------------

.. gd_req:: Requirement attribute: UID
   :id: gd_req__req_attr_uid
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_proc_tool, wf__req_feat_aou, wf__req_comp_aou
   :complies: std_req__iso26262__support_6425, std_req__iso26262__support_6432

   Each requirement shall have a unique ID. It shall consist of three parts:

      * type of requirement
      * structural element (e.g. some part of the feature tree, component acronym)
      * keyword describing the content of the requirement.

   Consider the project's naming convention.

.. gd_req:: Requirement attribute: title
   :id: gd_req__req_attr_title
   :status: valid
   :tags: manual_prio_1 attribute, mandatory
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_proc_tool, wf__req_feat_aou, wf__req_comp_aou
   :complies: std_req__iso26262__support_6424

   The title of the requirement shall provide a short summary of the description, but is not an "additional" requirement.

   This means for example that the word "shall" is not allowed in the title for all requirements.

.. gd_req:: Requirement attribute: description
   :id: gd_req__req_attr_description
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_proc_tool, wf__req_feat_aou, wf__req_comp_aou
   :complies: std_req__iso26262__support_6424

   Each requirement shall have a description.

   .. note::

      *ISO/IEC/IEEE/29148 - Systems and software engineering — Life cycle processes — Requirements engineering* defines general concepts including terms and examples for functional requirements syntax.

      The concepts shall apply.

.. gd_req:: Requirement attribute: type
   :id: gd_req__req_attr_type
   :status: valid
   :tags: manual_prio_2, attribute, mandatory
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_feat_aou, wf__req_comp_aou

   Each requirement, apart from process and tool requirements, shall have a type of one of following options:

      * Functional
      * Interface
      * Process
      * Non-Functional

.. gd_req:: Requirements attribute: security
   :id: gd_req__req_attr_security
   :status: valid
   :tags: manual_prio_2, attribute, mandatory
   :satisfies: wf__req_feat_req, wf__req_comp_req, wf__req_feat_aou, wf__req_comp_aou

   Each requirement, apart from process and tool requirements, shall have a security relevance identifier:

      * Yes
      * No

.. gd_req:: Requirement attribute: safety
   :id: gd_req__req_attr_safety
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :complies: std_req__iso26262__support_6421, std_req__iso26262__support_6425
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_feat_aou, wf__req_comp_aou

   Each requirement, apart from process and tool requirements, shall have a automotive safety integrity level (ASIL) identifier:

      * QM
      * ASIL_B

.. gd_req:: Requirement attribute: status
   :id: gd_req__req_attr_status
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :complies: std_req__iso26262__support_6425
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_feat_aou, wf__req_comp_aou

   Each requirement, apart from process and tool requirements, shall have a status:

      * valid
      * invalid

.. gd_req:: Requirement attribute: rationale
   :id: gd_req__req_attr_rationale
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__req_stkh_req

   Each stakeholder requirement shall provide an attribute called rationale.
   The rationale shall contain the reason why the requirement is needed.

.. gd_req:: Requirement attribute: valid_from
   :id: gd_req__req_attr_valid_from
   :status: valid
   :tags: manual_prio_2, attribute
   :satisfies: wf__req_stkh_req, wf__req_feat_req

   Stakeholder and feature requirements can have a validity attribute that tells
   from which milestone onwards the requirement is part of a feature.

   This validity attribute is defined as including the defined milestone.

   Milestone shall be valid release version tag, e.g. v1.0.2 as defined in
   Platform Release Note Template: :need:`gd_temp__rel_plat_rel_note`. Thus the
   corresponding requirement is valid from the defined milestone, including it.

.. gd_req:: Requirement attribute: valid_until
   :id: gd_req__req_attr_valid_until
   :status: valid
   :tags: manual_prio_2, attribute
   :satisfies: wf__req_stkh_req, wf__req_feat_req

   Stakeholder and feature requirements can have a validity attribute that tells
   until which milestone the requirement is part of a feature.

   This validity attribute is defined as excluding the defined milestone.

   Milestone shall be valid release version tag, e.g. v1.0.2 as defined in
   Platform Release Note Template: :need:`gd_temp__rel_plat_rel_note`. Thus the
   corresponding requirement is only valid until the defined milestone, excluding it.

.. _process_requirement_linkage:

Process Requirement Linkage
'''''''''''''''''''''''''''

.. gd_req:: Requirement Linkage
   :id: gd_req__req_linkage
   :status: valid
   :tags: manual_prio_1, attribute
   :complies: std_req__iso26262__support_6432
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_proc_tool

   Requirements shall be linked to its adjacent level via the attribute satisfies.

      * stakeholder requirements <- feature requirements
      * feature requirements <- component requirements
      * workflow or stakeholder requirements <- process requirements
      * process requirements or stakeholder requirements <- tool requirements

.. gd_req:: Requirement Traceability
   :id: gd_req__req_traceability
   :status: valid
   :tags: prio_1_automation, attribute
   :complies: std_req__iso26262__support_6432
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_proc_tool

   Bi-directional traceability shall be provided by adding a "back-link" via attribute satisfied by (i.e. make a <-> out of the <- in :need:`gd_req__req_linkage`).

.. gd_req:: Requirement attribute: requirement covered
   :id: gd_req__req_attr_req_cov
   :status: valid
   :tags: manual_prio_1, attribute
   :complies: std_req__iso26262__support_6423
   :satisfies: wf__req_stkh_req, wf__req_feat_req

   It shall be possible to specify the requirement coverage, meaning the requirement is covered fully by its linked children.

      * Yes
      * No

.. gd_req:: Requirement attribute: link to implementation
   :id: gd_req__req_attr_impl
   :status: valid
   :tags: prio_2_automation, attribute
   :satisfies: wf__req_feat_req, wf__req_comp_req

   It shall be possible to link requirements to code (to the respective line of code in an attribute of the requirement).

.. gd_req:: Requirement attribute: link to test
   :id: gd_req__req_attr_testlink
   :status: valid
   :tags: prio_1_automation, attribute
   :satisfies: wf__req_feat_req, wf__req_comp_req
   :complies: std_req__iso26262__support_6433, std_req__iso26262__software_944

   It shall be possible to link requirements to tests and automatically include a link to the test case in the attribute testlink.

.. gd_req:: Requirement attribute: test covered
   :id: gd_req__req_attr_test_covered
   :status: valid
   :tags: manual_prio_1, attribute
   :satisfies: wf__req_feat_req, wf__req_comp_req
   :complies: std_req__iso26262__support_6433, std_req__iso26262__software_944

   It shall be possible to specify if requirements are completely covered by the linked test cases.

      * Yes
      * No

.. gd_req:: Requirement attribute: versioning
   :id: gd_req__req_attr_version
   :status: valid
   :tags: prio_1_automation, attribute
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req
   :complies: std_req__iso26262__support_6425, std_req__iso26262__support_6434

   A versioning for requirements shall be provided. For this all mandatory attributes shall be taken into account: see :need:`gd_req__req_check_mandatory`

.. _process_requirement_checks:

Process Requirements Checks
'''''''''''''''''''''''''''

.. gd_req:: Requirement check: suspicious
   :id: gd_req__req_suspicious
   :status: valid
   :tags: prio_2_automation, check
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req
   :complies: std_req__iso26262__support_6425, std_req__iso26262__support_6434

   Based on the requirement versioning it shall be checked if a parent requirement was updated but not the linked child requirements (or tests).
   In case an update was detected, the attribute requirement (or test) covered shall be set to "No"

   Note: This refers to :need:`gd_req__req_attr_req_cov` and :need:`gd_req__req_attr_test_covered`

.. gd_req:: Requirements mandatory attributes provided
   :id: gd_req__req_check_mandatory
   :status: valid
   :tags: prio_1_automation, check
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_proc_tool, wf__req_feat_aou, wf__req_comp_aou

   It shall be checked if all mandatory attributes for each requirement is provided by the user. For all requirements following attributes shall be mandatory:

   .. needtable:: Overview mandatory requirement attributes
      :filter: "mandatory" in tags and "attribute" in tags and "requirements_engineering" in tags and type == "gd_req" and is_external == False
      :style: table
      :columns: title
      :colwidths: 30

.. gd_req:: Requirements no weak words
   :id: gd_req__req_desc_weak
   :status: valid
   :tags: done_automation, check
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req, wf__req_proc_tool, wf__req_feat_aou, wf__req_comp_aou

   It shall be ensured that no *weak words* are contained in the requirement description for:

   * Stakeholder Requirements
   * Feature Requirements
   * Component Requirements
   * Tool Requirements

   List of these weak words: just, about, really, some, thing, absolutely (to be extended)


.. gd_req:: Requirements linkage level
   :id: gd_req__req_linkage_fulfill
   :status: valid
   :tags: done_automation, check
   :complies: std_req__iso26262__support_6432
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req

   Every feature- and component requirement shall be linked to at least one parent requirement according to the defined traceability scheme:

   :ref:`traceability concept for requirements`

.. gd_req:: Requirements linkage architecture
   :id: gd_req__req_linkage_architecture
   :status: valid
   :tags: prio_2_automation, check
   :complies: std_req__iso26262__support_6423
   :satisfies: wf__req_feat_req, wf__req_comp_req

   It shall be checked if every feature- and component requirement is linked at least to one valid architectural element on the same level.
   This should also include requirement type checking:

   * If the requirement is of type "Functional" it shall be linked to architecture diagram elements.
   * If the requirement is of type "Interface" it shall be linked to architecture interface elements. Here the level matching is feature <> logical and component <> real.
   * If the requirement is of any other type there shall not be a link to architecture elements.

   Note that the linking is done from the architecture element to the requirement as described for example in :ref:`allocate_feature_requirements`.

.. gd_req:: Requirements linkage architecture switch
   :id: gd_req__req_linkage_architecture_switch
   :status: valid
   :tags: prio_2_automation, check
   :complies: std_req__iso26262__support_6423
   :satisfies: wf__req_feat_req, wf__req_comp_req

   The check :need:`gd_req__req_linkage_architecture` shall only be enabled for a release build, otherwise it would block creating requirements first without architecture.

.. gd_req:: Requirements linkage safety
   :id: gd_req__req_linkage_safety
   :status: valid
   :tags: prio_1_automation, check
   :satisfies: wf__req_stkh_req, wf__req_feat_req, wf__req_comp_req
   :complies: std_req__iso26262__support_6422

   It shall be checked that (child) QM requirements (Safety == QM) can not be linked against a (parent) safety requirement (Safety != QM).

   Note: This ensures that safety requirements are properly derived into their children. Also a mix of safe and QM aspects in a parent is avoided by this.

.. gd_req:: Requirements validity
   :id: gd_req__req_validity
   :status: valid
   :tags: prio_3_automation, check
   :satisfies: wf__req_stkh_req, wf__req_feat_req

   Validity attributes (:need:`gd_req__req_attr_valid_from` and :need:`gd_req__req_attr_valid_until`) shall be checked for correctness (i.e. they denote an existing milestone) and consistent (e.g. the until is not before from)
   Several of the above checks are not to be executed on requirements not valid in the next milestone, these are TBD

.. needextend:: docname is not None and "process_areas/requirements_engineering" in docname
   :+tags: requirements_engineering
