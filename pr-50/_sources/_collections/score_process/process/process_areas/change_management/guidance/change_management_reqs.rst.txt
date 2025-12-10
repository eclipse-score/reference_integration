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

.. _chm_process_change_request_attributes:

Process Requirements
====================

Change Request Attributes
-------------------------

.. gd_req:: Change Request attribute: UID
   :id: gd_req__change_attr_uid
   :status: valid
   :tags: done_automation, attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP1, std_req__iso26262__support_8411, std_req__iso26262__support_8421, std_req__iso26262__support_8432, std_req__iso26262__support_8453

   Each Change Request shall have a unique ID. It shall be in an integer number.

.. gd_req:: Change Request attribute: status
   :id: gd_req__change_attr_status
   :status: valid
   :tags: done_automation, attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP3, std_req__aspice_40__SUP-10-BP5, std_req__aspice_40__SUP-10-BP6, std_req__iso26262__support_8411, std_req__iso26262__support_8422, std_req__iso26262__support_8432, std_req__iso26262__support_8442

   Each Change Request shall have a status:

      * open
      * in review
      * in implementation
      * closed
      * rejected

.. gd_req:: Change Request attribute: title
   :id: gd_req__change_attr_title
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP1, std_req__iso26262__support_8411, std_req__iso26262__support_8422

   Reason for the Change Request

.. gd_req:: Change Request attribute: description
   :id: gd_req__change_attr_impact_description
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP2, std_req__iso26262__support_8411, std_req__iso26262__support_8422, std_req__iso26262__support_8431, std_req__iso26262__support_8432, std_req__iso26262__support_8452, std_req__iso26262__support_8453

   Exact description of the Change Request, including impact analysis on functional safety,
   security, implementation (schedule, risks, resources) verification (measures defined).

.. gd_req:: Change Request attribute: safety
   :id: gd_req__change_attr_impact_safety
   :status: valid
   :tags: prio_1_automation, attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP2, std_req__iso26262__support_8422

   Each Change Request shall have a automotive safety integrity level (ASIL) identifier:

      * QM
      * ASIL_B

.. gd_req:: Change Request attribute: security
   :id: gd_req__change_attr_impact_security
   :status: valid
   :tags: prio_2_automation, attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP2, std_req__iso26262__support_8422

   Each Change Request shall have a security relevance identifier:

      * Yes
      * No

.. gd_req:: Change Request attribute: Types
   :id: gd_req__change_attr_types
   :status: valid
   :tags: prio_1_automation, attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP1

      * Feature
      * Feature Modification
      * Component
      * Component Modification

      Feature
      This Change Request describes a potential new feature for the platform.
      The Change Request uses the Feature request template: :ref:`chm_feature_templates`.

      Feature Modification
      This Change Request describes a scope modification of an existing feature (requirement
      or work product). The Change Request modifies the already existing Feature Request
      template: :ref:`chm_feature_templates`.

      Component
      This Change Request describes a potential new component for the platform.
      The Change Request uses the Component request template: :ref:`chm_component_templates`.

      Component Modification
      This Change Request describes a scope modification of an existing component (requirement or work
      product). The Change Request modifies the already existing Component Request template: :ref:`chm_component_templates`.

.. gd_req:: Change Request attribute: Affected Work Products
   :id: gd_req__change_attr_affected_wp
   :status: draft
   :tags: attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP4, std_req__iso26262__support_8412, std_req__iso26262__support_8422, std_req__iso26262__support_8452, std_req__iso26262__support_8453

   Links to the work products affected by the Change Request

.. gd_req:: Change Request attribute: Milestone
   :id: gd_req__change_attr_milestone
   :status: valid
   :tags: done_automation, attribute, mandatory
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__SUP-10-BP6, std_req__iso26262__support_8413

   Milestone until the Change Request must be implemented (used for prioritization)


.. _chm_process_change_requests_checks:

Change Request Checks
'''''''''''''''''''''

.. gd_req:: Change Requests mandatory attributes provided
   :id: gd_req__change_attr_mandatory
   :status: valid
   :tags: prio_2_automation, attribute, check
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__iic-13-51

   It shall be checked if all mandatory attributes for each Change Request
   is provided by the user. For all requirements following attributes shall be mandatory:

   .. needtable:: Overview mandatory change request attributes
      :filter: "mandatory" in tags and "attribute" in tags and "change_management" in tags  and is_external == False
      :style: table
      :columns: title
      :colwidths: 30


.. _chm_process_change_requests_impact_analysis_tool:

Change Request Traceability Impact Analysis Tool
''''''''''''''''''''''''''''''''''''''''''''''''

.. gd_req:: Change Requests Impact Analysis Tool
   :id: gd_req__change_tool_impact_analysis
   :status: valid
   :tags: prio_3_automation, check, tool
   :satisfies: wf__change_create_cr, wf__change_analyze_cr, wf__change_implement_monitor_cr, wf__change_close_cr
   :complies: std_req__aspice_40__iic-13-51

   It shall be reported, which work products and elements are affected by adding a new
   feature or component or by a modification of an existing feature or component.

   Below picture illustrates the relations:

   .. figure:: ../_assets/impact_analysis.drawio.svg
      :width: 100%
      :align: center
      :alt: Which changes to follow for impact analysis.

   The picture is derived from the building blocks metamodel containing all the work products
   (:ref:`general_concepts_building_blocks`). Its arrows show how every work product is
   linked (manually) to other work products (e.g. feature requirements are linked to
   stakeholder requirements via "satisfies"). The color code describes which of these Links
   need to be followed for the impact analysis (so for the example this means: if a stakeholder
   requirement is changed, the feature requirements linked are affected, but not the other way round).
   "Black" links do not need to be followed, these are the "verifies" links. And these are
   expected to fail after implementation change, so the impact on testing will be detected
   by the test automation without the need for an additional tooling. Note that for some
   links it is expected to have both directions followed (red arrows) - these are the
   artefacts which reside in different repositories.

   Note also: The impact analysis needs to follow the links iteratively, so first to the directly
   connected work products, then to the next, ... (see the next illustration):

   .. figure:: ../_assets/impact_iteration.drawio.svg
      :width: 100%
      :align: center
      :alt: How to follow changes for impact analysis iteratively.

.. needextend:: docname is not None and "process_areas/change_management" in docname
   :+tags: change_management
