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

.. _documentation_process_requirements:

Document Management Process Requirements
========================================

.. gd_req:: Document Types
   :id: gd_req__doc_types
   :status: valid
   :tags: done_automation
   :satisfies: wf__platform_cr_mt_platform_mgmt_plan
   :complies: std_req__iso26262__support_1043

   There are the following document types:

   * document
   * doc_tool

    .. note::
      The type "document" is the GENERIC type, which can be used for realizing concrete work products,
      with the exception of the tool verification report (which uses the "doc_tool" type).
      The "doc_tool" type is described in :ref:`tlm_process_requirements`.

   .. note::
      Process documents are not documents realizing work products,
      types for that shall only used for process definition, as defined

      * gd_chklst
      * gd_guidl
      * gd_req
      * gd_temp
      * doc_concept
      * doc_getstrt
      * workproduct
      * workflow
      * role


.. gd_req:: Document attributes
   :id: gd_req__doc_attributes_manual
   :status: valid
   :tags: manual_prio_1
   :satisfies: wf__platform_cr_mt_platform_mgmt_plan
   :complies: std_req__iso26262__support_1043

   Generic documents shall have the following mandatory manual attributes:

   * id
   * status
   * security
   * safety
   * realizes

   The attribute "tags" is optional.

   Compare also  :need:`gd_temp__documentation`

.. gd_req:: Document Author
   :id: gd_req__doc_reviewer
   :status: valid
   :tags: prio_1_automation
   :satisfies: wf__platform_cr_mt_platform_mgmt_plan
   :complies: std_req__iso26262__support_1045

   The version management tool shall document and report (be able to show) the authorship of a document.
   I.e. for each change of a document the author of the changes is stored.

.. gd_req:: Document Reviewer
   :id: gd_req__doc_author
   :status: valid
   :tags: prio_1_automation
   :satisfies: wf__platform_cr_mt_platform_mgmt_plan
   :complies: std_req__iso26262__support_1043

   The version management tool shall document and report (be able to show) the reviewers of a document.
   I.e. for each change of a document the reviewers of the change are stored.

.. gd_req:: Document Approver
   :id: gd_req__doc_approver
   :status: valid
   :tags: prio_1_automation
   :satisfies: wf__platform_cr_mt_platform_mgmt_plan
   :complies: std_req__iso26262__support_1045

   The version management tool shall document and report (be able to show) the approver of a document.
   I.e. for each change of a document the approver of the change is stored,
   which is usually the person with "write-rights" on the document approving
   the merge of a Pull Request (this may also be more than one person).
   Note that every approver is also reviewer.
