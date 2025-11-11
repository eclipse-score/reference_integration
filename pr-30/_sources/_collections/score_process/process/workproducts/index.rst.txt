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

Work products
=============

Project development work product traceability model overview: :ref:`general_concepts_traceability`


Platform management
--------------------

General
^^^^^^^

.. workproduct:: Policies
   :id: wp__policies
   :status: draft
   :tags: requirements_management
   :complies: std_wp__iso26262__management_551

   In general the project follows the Eclipse Foundation Development Process (EDP,
   `Eclipse Foundation Development Process <https://www.eclipse.org/projects/dev_process/>`_).
   The EDP defines important concepts, including the Open Source Rules of Engagement,
   the organizational framework for open source projects and teams, releases, reviews,
   and more.

   Further the Eclipse Foundation Security Policy
   (`Eclipse Foundation Security Policy <https://www.eclipse.org/security/policy/>`_)
   applies.

   The Eclipse Foundation Functional Safety Process (EFFSP, currently in DRAFT
   `Eclipse Foundation Functional Safety Process <https://gitlab.eclipse.org/eclipsefdn/emo-team/policies/functional-safety-process/-/blob/main/source/fsp.adoc?ref_type=heads>`_)
   applies.

   Concerning the use of Generative Artificial Intelligence
   `Usage Guidelines <https://www.eclipse.org/projects/guidelines/genai/>`_ applies.

   Project specific Policies for functional safety and cybersecurity may extend the
   ones from ECLIPSE.


Product development
-------------------

Platform development
^^^^^^^^^^^^^^^^^^^^

.. workproduct:: Platform Build Configuration
   :id: wp__platform_sw_build_config
   :status: draft
   :tags: safety
   :complies: std_wp__iso26262__software_1052

   Build configuration capable to create the SEooC Library for the reference HW, platform level.
   Note: Embedded software in the sense of the Iso (i.e. deployed on the production HW) is not part of our delivery.


Component development
^^^^^^^^^^^^^^^^^^^^^

.. workproduct:: Module Build Configuration
   :id: wp__module_sw_build_config
   :status: draft
   :tags: safety
   :complies: std_wp__iso26262__software_1052

   Build configuration capable to create the SEooC Library for the reference HW, module level.
   Note: Embedded software in the sense of the Iso (i.e. deployed on the production HW) is not part of our delivery.


Project Work product Linkage
----------------------------

.. needpie:: The project work products contained in exactly one project workflow
   :labels: Not-Linked, Linked Work product, Linked Work product To Multiple Workflows
   :legend:
   :colors: red, green, blue
   :filter-func: score_metamodel.checks.standards.my_pie_workproducts_contained_in_exactly_one_workflow

Project Work product list
-------------------------

.. needtable::
   :style: table
   :columns: title;id;tags
   :colwidths: 25,25,25
   :sort: title

   results = []

   for need in needs.filter_types(["workproduct"]):
      if need['is_external'] == False:
                results.append(need)
