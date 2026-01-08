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

.. _process_management_templates:

Templates
=========

.. gd_temp:: Workflow Template
   :id: gd_temp__process_workflow
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. workflow:: <Title reflecting activity>
         :id: wf__<process area or abbreviation>_<activity>
         :status: <draft|valid>
         :tags: <process area or abbreviation>
         :responsible: <defined role:rl__<...>>
         :approved_by: <defined role:rl__<...>>, ..., <defined role:rl__<...>>
         :supported_by: <defined role:rl__<...>>, ..., <defined role:rl__<...>>
         :input: <defined workproduct:wp__<...>>
         :output: <defined workproduct:wp__<...>>
         :contains: <defined guidances: guideline:gd_guidl__<...>, template:gd_temp__<...>, checklist:gd_chklst__<...>, method:gd_meth__<...>
         :has: <concept:doc_concept__<...>, getting started:doc_getstrt__<...>>


.. gd_temp:: Work Product Template
   :id: gd_temp__process_workproduct
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. workproduct:: <Title reflecting work product>
         :id: wp__<process area or abbreviation>_<work product>
         :status: <draft|valid>
         :tags: <process area or abbreviation>
         :complies: <standard work product:std_wp__<...>>, ..., <standard work product:std_wp__<...>>, <standard requirement:std_req__aspice_40__iic-<...>>, ..., <std_req__aspice_40__iic-<...>>


.. gd_temp:: Role Template
   :id: gd_temp__process_role
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      Single person role
      .. role:: <Title reflecting role>
         :id: rl__<role>
         :status: <draft|valid>
         :tags: <process area or abbreviation>

      Team role
      .. role:: <Title reflecting team role>
         :id: rl__<process area or abbreviation>_<team role<>>
         :status: <draft|valid>
         :tags: <process area or abbreviation>
         :contains: <role:rl__<...>>, ..., <role:rl__<...>>


.. gd_temp:: Getting Started Template
   :id: gd_temp__process_getstrt
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. doc_getstrt:: <Title reflecting process area getting started>
         :id: doc_getstrt__<process area or abbreviation>
         :status: <draft|valid>
         :tags: <process area or abbreviation>


.. gd_temp:: Concept Description Template
   :id: gd_temp__process_concept
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. doc_concept:: <Title reflecting process area concept description>
         :id: doc_concept__<process area or abbreviation>
         :status: <draft|valid>
         :tags: <process area or abbreviation>


.. gd_temp:: Guideline Template
   :id: gd_temp__process_guideline
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. gd_guidl:: <Title reflecting process area guideline>
         :id: gd_guidl__<process area or abbreviation>_<...>
         :status: <draft|valid>
         :tags: <process area or abbreviation>
         :complies: <standard requirement:std_req__<...>>, ..., <standard requirement:std_req__<...>>


.. gd_temp:: Template Template
   :id: gd_temp__process_template
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. gd_temp:: <Title reflecting process area template>
         :id: gd_temp__<process area or abbreviation>_<...>
         :status: <draft|valid>
         :tags: <process area or abbreviation>
         :complies: <standard requirement:std_req__<...>>, ..., <standard requirement:std_req__<...>>


.. gd_temp:: Checklist Template
   :id: gd_temp__process_checklist
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. gd_chklst:: <Title reflecting process area checklist>
         :id: gd_chklst__<process area or abbreviation>_<...>
         :status: <draft|valid>
         :tags: <process area or abbreviation>
         :complies: <standard requirement:std_req__<...>>, ..., <standard requirement:std_req__<...>>


.. gd_temp:: Method Template
   :id: gd_temp__process_method
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. gd_method:: <Title reflecting process area method>
         :id: gd_meth__<process area or abbreviation>_<...>
         :status: <draft|valid>
         :tags: <process area or abbreviation>
         :complies: <standard requirement:std_req__<...>>, ..., <standard requirement:std_req__<...>>


.. gd_temp:: Process Requirement Template
   :id: gd_temp__process_requirement
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. gd_req:: <Title reflecting process area requirement>
         :id: gd_req__<process area or abbreviation>_<...>
         :status: <draft|valid>
         :tags: <process area or abbreviation>
         :satisfies: <defined workflow:wf__<...>>, ..., <defined workflow:wf__<...>>
         :complies: <standard requirement:std_req__<...>>, ..., <standard requirement:std_req__<...>>


.. gd_temp:: Standard Requirement Template
   :id: gd_temp__process_standard_req
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. std_req:: <Title reflecting standard requirement>
         :id: std_req__<standard>__<...>
         :status: <draft|valid>
         :tags: <standard>


.. gd_temp:: Standard Work Product Template
   :id: gd_temp__process_standard_wp
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. std_wp:: <Title reflecting standard work product>
         :id: std_wp__<standard>__<...>
         :status: <draft|valid>
         :tags: <standard>


.. gd_temp:: Document Template
   :id: gd_temp__process_document
   :status: valid
   :tags: process_management
   :complies: std_req__iso26262__management_5421, std_req__iso26262__management_5422, std_req__aspice_40__gp-311

   .. code-block:: rst

      .. document:: <Title reflecting the deployed work product>
         :id: doc__<work product>
         :status: <draft|valid>
         :safety: <QM | ASIL_B>
         :security: <YES|NO>
         :realizes: wp__<work product reference>, ..., wp__<work product reference>
         :tags: <depends on where it is deployed>

.. note::
   The document template must be used from the projects deploying the process and
   implementing the defined work products. :ref:`processes_introduction` shows the
   'fullfils' link from a 'TEXT FILE' to a work product defined in the process
   description. This link is implemented by the ':realize:' attribute in the template
   above.
