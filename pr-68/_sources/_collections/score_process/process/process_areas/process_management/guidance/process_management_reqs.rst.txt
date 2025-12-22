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

.. _process_management_requirements:


Process Requirements
====================


.. gd_req:: Process Model Building Blocks
   :id: gd_req__process_management_build_blocks
   :status: valid
   :tags: done_automation, attribute, mandatory
   :satisfies: wf__cr_mt_process_mgt_strategy, wf__def_app_process_description, wf__mon_imp_process_description
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   The process model building blocks are defined. Compare also the process model
   overview here: :ref:`processes_introduction`.

   Following building blocks are defined:

      * Workflow
      * Work Product
      * Role (includes Team)

   Additionally there shall be the following additions for workflows:

      * Getting Started
      * Concept
      * Guidance

   Additionally there shall be the following details for guidance:

      * Guideline
      * Template
      * Checklist
      * Method
      * Process Requirements

   Additionally there shall be the following additions for standard compliance:

      * Standard Work Products
      * Standard Requirements

   Additionally there shall be the following additions to allow deployment examples or
   templates for later deployment for work products:

      * Document


Process Building Blocks Attributes
----------------------------------

.. gd_req:: Building blocks attributes
   :id: gd_req__process_management_build_blocks_attr
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__cr_mt_process_mgt_strategy, wf__def_app_process_description, wf__mon_imp_process_description
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   Each building block shall have defined attributes as defined here:
   :ref:`process_management_templates`.

   Some have further constraints as defined here:

   * The UID attribute must be unique.
   * The STATUS attribute shall have a status: <draft|valid>
   * The SAFETY attribute shall have level: <QM | ASIL_B>
   * The SECURITY attribute shall have level: <YES|NO>
   * Each building block shall have a description


Process Building Blocks Linkage
-------------------------------

.. gd_req:: Building blocks linkage
   :id: gd_req__process_management_build_blocks_link
   :status: valid
   :tags: manual_prio_1, attribute, mandatory
   :satisfies: wf__cr_mt_process_mgt_strategy, wf__def_app_process_description, wf__mon_imp_process_description
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   Each building block shall have defined links as defined here:
   :ref:`process_management_templates`.


Process Building Blocks Checks
------------------------------

.. gd_req:: Building blocks check
   :id: gd_req__process_management_build_blocks_check
   :status: valid
   :tags: done_automation
   :satisfies: wf__cr_mt_process_mgt_strategy, wf__def_app_process_description, wf__mon_imp_process_description
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   It shall be checked, that all attributes defined here
   :ref:`process_management_templates` are provided and correctly linked by the user.


.. needextend:: docname is not None and "process_areas/process_management" in docname
   :+tags: process_management
