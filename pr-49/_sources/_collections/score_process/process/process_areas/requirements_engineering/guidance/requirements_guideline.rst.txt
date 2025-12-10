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

Guideline
#########

.. gd_guidl:: Requirements Guideline
   :id: gd_guidl__req_engineering
   :status: valid
   :complies: std_req__isopas8926__44421, std_req__isopas8926__44422, std_req__isopas8926__44423

This document describes the general guidances for requirements based on the concept which is defined in :need:`[[title]]<doc_concept__req_process>`.

General Hints
=============

Templates
---------

*Need* templates displaying the correct syntax and attribute definition are provided for each requirement type. For VScode code snippets are included in the workspace settings which will provide in-place the definition of requirements including all mandatory attributes:

.. list-table:: Overview
   :header-rows: 1
   :widths: 37, 37, 25

   * - Requirement Level
     - Template
     - VS Code Snippet
   * - Stakeholder Requirements
     - :need:`[[title]] <gd_temp__req_stkh_req>`
     - ``stkh_req__``
   * - Feature Requirements
     - :need:`[[title]] <gd_temp__req_feat_req>`
     - ``feat_req__``
   * - Component Requirements
     - :need:`[[title]] <gd_temp__req_comp_req>`
     - ``comp_req__``
   * - AoU Requirements
     - :need:`[[title]] <gd_temp__req_aou_req>`
     - ``aou_req__``
   * - Process Requirements
     - :need:`[[title]] <gd_temp__req_process_req>`
     - ``gd_req__``
   * - Tool Requirements
     - :need:`[[title]] <gd_temp__req_tool_req>`
     - ``tool_req__``

Additionally for the formulation of requirements following template is available: :need:`[[title]]<gd_temp__req_formulation>`

Attributes
----------

For all requirements following mandatory attributes are defined:

.. needtable:: Overview of mandatory requirement attributes
   :tags: requirements_engineering
   :filter: "mandatory" in tags and "attribute" in tags and type == "gd_req" and is_external == False
   :style: table
   :columns: title
   :colwidths: 30


* Title and description: For the formulation of requirements following template shall be used :need:`[[title]]<gd_temp__req_formulation>`
* ID: The naming convention for the ID is defined for every project in a central place (e.g. in the general contributor's guidelines)
* Furthermore the requirements need to be versioned. Therefore a hash value of the requirement will to be calculated. The concept is described: :ref:`traceability concept for requirements`
* For the remaining attributes only predefined values can be used. A more detailed description can be found here: :ref:`attributes of the requirements`
* Note that "rationale" is only mandatory for Stakeholder Requirements ...
* and process requirements do not need security and safety because these can be derived from the standards they comply to (as well type attributes as these would all be "Non-functional")

Checks
------

During the docs build checks will be performed on the requirements. Those are specified via following process requirements:

.. needtable:: Overview checks for requirement
   :tags: requirements_engineering
   :filter: "check" in tags and type == "gd_req" and is_external == False
   :style: table
   :columns: title;id
   :colwidths: 60,40

.. _workflow_requirements:

Workflow for Creating a Requirement
===================================

This section describes in detail which steps need to be performed to create a requirement based on :numref:`requirements_workflow_fig`

.. list-table:: Workflow for creating a requirement
   :header-rows: 1
   :widths: 10,60,30

   * - Step
     - Description
     - Responsible
   * - :ref:`1. <create_parent_requirement>`
     - Create parent requirement
     - :need:`[[title]] <rl__contributor>`
   * - :ref:`2. <review_parent_requirement>`
     - Review parent requirement
     - :need:`[[title]] <rl__committer>`
   * - :ref:`3. <review_parent_requirement>`
     - Merge valid parent requirement to main branch
     - :need:`[[title]] <rl__committer>`
   * - :ref:`4. <derive_child_requirement>`
     - Derive child requirement and establish traceability
     - :need:`[[title]] <rl__contributor>`
   * - :ref:`5. <review_child_requirement>`
     - Review child requirement
     - :need:`[[title]] <rl__committer>`
   * - :ref:`6. <review_child_requirement>`
     - Merge valid child requirement to main branch
     - :need:`[[title]] <rl__committer>`
   * - :ref:`7. <generate_linkage_document>`
     - Generate linkage document
     - :need:`[[title]] <rl__contributor>`
   * - :ref:`8. <formal_requirement_review>`
     - Perform formal review of requirements
     - :need:`[[title]] <rl__committer>`

.. _create_parent_requirement:

Create parent requirement
-------------------------

In this step the parent requirements shall be created. Stakeholder- and feature requirements should be generated in the project's main repository.

For this the following templates are available:

* :ref:`Requirement Templates <requirement templates>`

Note: The projec's way of contributing new content (how to branch, how to commit, how to merge with the selected version management tool)
has to be documented in a central place, stick to this guideline also for the requirement contributions.

.. _review_parent_requirement:

Review parent requirement
-------------------------

As soon as the parent requirements are in a mature state it can be :ref:`reviewed <review_concept>` and merged into the main branch of the main project's repository. However this is not the formal inspection of the requirements, this will follow in an upcoming step.

Following roles should be included in the review:

* :need:`[[title]] <rl__safety_manager>`
* :need:`[[title]] <rl__security_manager>`
* :need:`[[title]] <rl__committer>`

.. _derive_child_requirement:

Derive child requirement and establish traceability
---------------------------------------------------

In an upcoming step the child requirements shall be derived from the parent requirements. Feature requirements shall be placed in the main project's repository again, while component requirements shall be placed in the module repository. During this process the derived requirements shall also be linked according to the defined traceability matrix to the parent requirements.

For this the following templates are available:

* :ref:`Requirement Templates <requirement templates>`

Note: For non-functional (and process) type requirements no children need to be derived (on lower requirement levels),
these can mostly be directly fulfilled and verified.
To ease verification a link to these ("process" type) requirements can be established from :need:`gd_temp__req_process_req`.

.. _review_child_requirement:

Review child requirement
------------------------

As soon as also the child requirements are in a mature state they can be :ref:`reviewed <review_concept>` and merged into the main branch of the respective repository. Again this is not a formal inspection as it will be performed in a later step.

.. _generate_linkage_document:

Generate linkage document
-------------------------

As parent and child requirements are now available the linkage of the requirements can be established. This should be performed as described in :ref:`coverage_of_requirements`


.. _formal_requirement_review:

Perform formal review of requirements
-------------------------------------

In a last step the requirements shall be formally inspected. Therefore a checklist exists: :need:`[[title]] <gd_chklst__req_inspection>`

Following roles should be included in the review:

* :need:`[[title]] <rl__safety_manager>`
* :need:`[[title]] <rl__security_manager>`
* :need:`[[title]] <rl__committer>`


.. _aou_workflow:

Workflow for Creating and Linking Assumption of Use (AoU)
=========================================================

An AoU is a category of requirement which originates from a safety concept of an architectural element (and thus it is confirmed by a safety analysis).
This is different for AoU created on SW-platform level, these are also coming from the scope of the project (i.e. the knowledge which safety activities are not part of a project).
As it can not be fulfilled by the architecture element (e.g. component) itself, it needs to be fulfilled by the user of the element.
In Safety Elements out of Context (SEooC) the AoUs will normally be part of the safety manual.
In this process description (as it describes SEooC development) these AoUs are created both internally and externally - the latter if existing SEooCs are integrated into the platform (e.g. a qualified Operating System).
For AoU which arise internally (i.e. from project specific modules) the template is almost identical to the one for feature/component requirements. The only difference is that it is defined such that the attribute "satisfies" is replaced with the attribute "mitigates" (see picture below).
For externally provided AoUs of course the sentence template cannot be taken into account, as these are only imported from an external safety manual. It is also not possible to link it to other development artifacts via the attribute "mitigates".

AoUs can be of different class and shall be handled by tracing those

* to Feature/Component Architecture (via satisfies), if those are on Component Level and can be fulfilled there
* to Stakeholder Requirements (via satisfies), if AoU are of general nature and can be fulfilled by platform
* or by containing those in Platform Safety Manual, if AoU cannot be fulfilled by platform but need to be satisfied by the user of the platform


.. figure:: ../_assets/aou_traceability.drawio.svg
   :align: center
   :width: 100%
   :name: aou_traceability

   AoU Traceability

:numref:`aou_traceability` is an extension of the workproduct traceability to show the handling of (external) AoU. Note that the component level displayed in green shows two components - on the right the one exporting AoU to be fulfilled by others, left the component which fulfills and exports AoU (but without the traceability shown on the right to reduce complexity).

Special cases
=============

Requirements for future (or past) milestones
--------------------------------------------

A project release is always consistent, i.e. all development artefacts linked to each other do not contradict each other
and complete, i.e. all requirements are derived into dependent work products down to the implementation.
This is also the case for the selection of the scope of a platform by feature flags, as these
select a part of the platform but this part is complete.

In this chapter we cover a special use case where requirements not for the next milestone but for later milestones are specified.
This could be the case when a function is already specified but it is decided to delay its implementation.

A use case where the specification AND implementation of a new/modified feature is done
already during the development time of an earlier milestone than the feature is planned
can be realized by the feature flags (for new features) or by branching off.

For the "only specification" use case, the following attributes can be used:
- :need:`gd_req__req_attr_valid_from`
- :need:`gd_req__req_attr_valid_until`

These attributes can be used for stakeholder and feature requirements, but not for
the component requirements, as these are expected to be developed during small implementation cycles.

If an existing requirement needs to be reworked for the new function it will be split in two.
The requirement with the old specification will be valid_until the milestone before the
new function is planned and the requirement with the new specification is valid_from the planned milestone.

Tailoring
=========

.. gd_guidl:: Requirements Tailored
   :id: gd_guidl__req_tailored
   :status: valid
   :complies: std_req__iso26262__system_6423, std_req__iso26262__system_6424, std_req__iso26262__system_6425, std_req__iso26262__software_643, std_req__iso26262__software_644, std_req__iso26262__software_646

   This part of the guideline links to all the requirements which are not fulfilled by the
   requirements engineering process. Make sure these are tailored out in the safety/security/quality plans
   for your project (documented in the PMP). Reasoning given below must be confirmed there.

   The reasoning is:

   - for "system" standard requirements: see platform safety plan in PMP
   - for "software" standard requirements: 644, 646: because they refer to (PMP) tailored work product, 643: because this refers to (PMP) tailored activity
