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

Getting Started
###############

.. doc_getstrt:: Getting Started on Tool Management
   :id: doc_getstrt__tool_process
   :status: valid
   :tags: tool_management

This document describes the steps to evaluate tools and qualify them according to
ISO 26262 and ISO/SAE 21434 as used standards in the project.

Therefore guidelines :need:`gd_temp__tool_management_verif_rpt_template` and a
 :need:`doc_concept__tool_process` are available.


General Workflow
****************

The workflows are defined in the :ref:`tlm_workflows` section.

For every tool identified, the following workflows are executed:

* Create tool verification report according to :need:`wf__tool_create_tool_verification_report`
* Evaluate tool and update tool verification report according to :need:`wf__tool_evaluate_tool`
* Qualify tool and update tool verification report according to :need:`wf__tool_qualify_tool`
* Approve tool verification report according to :need:`wf__tool_approve_tool_verification_report`

In addition create a tool management plan as part of the platform management plan according to :need:`wf__platform_cr_mt_platform_mgmt_plan`.
