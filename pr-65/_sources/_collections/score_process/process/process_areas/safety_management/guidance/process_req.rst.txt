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

Safety Management Process Requirements
======================================

.. gd_req:: Safety Management Document Status
   :id: gd_req__safety_doc_status
   :status: valid
   :tags: done_automation
   :complies: std_req__iso26262__management_6468
   :satisfies: wf__cr_mt_safety_plan, wf__cr_comp_class, wf__cr_mt_safety_manual

   Safety plans shall contain documents references where the status is derived automatically.

   Note: This can be done by defining the document as a sphinx-need and using sphinx mechanisms.

.. gd_req:: Safety Management Work Product Status
   :id: gd_req__safety_wp_status
   :status: valid
   :tags: prio_2_automation
   :complies: std_req__iso26262__management_6468
   :satisfies: wf__cr_mt_safety_plan, wf__cr_comp_class, wf__cr_mt_safety_manual

   Safety plans shall contain work product references where the accumulated status is derived automatically.

   Note: This can be done as for documents if the work product is a single sphinx-need.
   For work products collections (e.g. all requirements of a component) an accumulated status is needed (e.g. like "% valid state")
