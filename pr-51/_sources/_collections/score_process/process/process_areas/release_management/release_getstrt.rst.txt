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

.. doc_getstrt:: Getting Started on Release Management
   :id: doc_getstrt__release_process
   :status: valid
   :tags: release_mgt

This document describes the steps to create a release of the SW and collaterals (test, documentation).

Releases can be done in every repository, mainly:

* Platform (Main project/Integration) repository
* Module (platform's components) repositories

For this are available: templates :need:`gd_temp__rel_plat_rel_note` & :need:`gd_temp__rel_mod_rel_note`
or `Combined Release Template <https://github.com/eclipse-score/process_description/blob/main/.github/RELEASE_TEMPLATE.md>`_,
guidelines :need:`gd_guidl__rel_management` and a :need:`doc_concept__rel_process`
are available.

General Workflow
****************

The workflows are defined in the :ref:`release_workflows` section.

The following workflows are executed:

* Create a release plan for the platform according to :need:`wf__rel_plat_rel_plan`
* Create a release plan for the module according to :need:`wf__rel_mod_rel_plan`
* According to the planning create release notes for modules :need:`wf__rel_mod_rel_note` and platform :need:`wf__rel_platform_rel_note`

In addition create a release management plan as part of the platform management plan according to :need:`wf__platform_cr_mt_platform_mgmt_plan`.
