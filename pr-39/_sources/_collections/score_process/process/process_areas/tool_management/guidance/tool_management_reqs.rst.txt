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

.. _tlm_process_requirements:

Process Requirements
====================

.. _tlm_process_attributes:

Tool Verification Report Attributes
-----------------------------------

.. gd_req:: Tool attribute: UID
   :id: gd_req__tool_attr_uid
   :status: valid
   :tags: done_automation, tool_management, attribute, mandatory
   :satisfies: wf__tool_create_tool_verification_report
   :complies: std_req__iso26262__support_1141, std_req__aspice_40__SUP-8-BP1

   Each Tool Verification Report shall have a unique ID.

.. gd_req:: Tool attribute: status
   :id: gd_req__tool_attr_status
   :status: valid
   :tags: prio_1_automation, tool_management, attribute, mandatory
   :satisfies: wf__tool_create_tool_verification_report
   :complies: std_req__iso26262__support_1141, std_req__aspice_40__SUP-8-BP1

   Each Tool Verification Report shall have a status.

      * draft
      * evaluated
      * qualified
      * released
      * rejected

.. gd_req:: Tool attribute:: version
   :id: gd_req__tool_attr_version
   :status: valid
   :tags: manual_prio_1, tool_management, attribute, mandatory
   :satisfies: wf__tool_create_tool_verification_report
   :complies: std_req__iso26262__support_1141, std_req__aspice_40__SUP-8-BP1

   Each Tool Verification Report shall have a version:

      * v.X.Y.Z (major, minor, patch)

.. gd_req:: Tool attribute:: tcl
   :id: gd_req__tool_attr_tcl
   :status: valid
   :tags: manual_prio_1, tool_management, attribute, mandatory
   :satisfies: wf__tool_create_tool_verification_report
   :complies: std_req__iso26262__support_1141, std_req__aspice_40__SUP-8-BP1

   Each Tool Verification Report shall have a tool confidence level:

      * LOW
      * HIGH

.. gd_req:: Tool attribute:: safety affected
   :id: gd_req__tool_attr_safety_affected
   :status: valid
   :tags: manual_prio_1, tool_management, attribute, mandatory
   :satisfies: wf__tool_create_tool_verification_report
   :complies: std_req__iso26262__support_1141, std_req__aspice_40__SUP-8-BP1

   Each Tool Verification Report shall have a safety relevance identifier:

      * YES
      * NO

.. gd_req:: Tool attribute:: security affected
   :id: gd_req__tool_attr_security_affected
   :status: valid
   :tags: manual_prio_2, tool_management, attribute, mandatory
   :satisfies: wf__tool_create_tool_verification_report
   :complies: std_req__isosae21434__org_management_5451, std_req__aspice_40__SUP-8-BP1

   Each Tool Verification Report shall have a security relevance identifier:

      * YES
      * NO


Tool Verification Report Checks
'''''''''''''''''''''''''''''''

.. gd_req:: Tool Management mandatory attributes provided
   :id: gd_req__tool_check_mandatory
   :status: valid
   :tags: prio_1_automation, tool_management, attribute, check
   :satisfies: wf__tool_create_tool_verification_report
   :complies: std_req__aspice_40__SUP-8-BP1

   It shall be checked if all mandatory attributes for each Tool Verification Report
   is provided by the user. For all requirements following attributes shall be mandatory:

   .. needtable:: Overview mandatory problem attributes
      :filter: "mandatory" in tags and "attribute" and "tool_management" in tags and is_external == False
      :style: table
      :columns: title
      :colwidths: 30
