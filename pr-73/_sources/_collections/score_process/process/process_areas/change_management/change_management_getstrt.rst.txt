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

.. doc_getstrt:: Getting Started on Change Management
   :id: doc_getstrt__change_process
   :status: valid
   :tags: change_management

This document describes the steps to create a change request, and further to analyze,
implement, and to control the change until closure. Where a change is defined as an
introduction of a new feature/component or modification of an existing feature/component.

Examples for change requests:

* New feature e.g. communication, debugging, health management, cryptography introduced (feature request).
* Existing feature, e.g. communication supports new protocol (feature modification).
* New component for parsing a protocol introduced (component request).
* API change for an existing component (component modification).

Therefore guidelines :need:`gd_temp__change_feature_request` and
:need:`gd_temp__change_component_request`, :need:`gd_guidl__change_change_request` and
a :need:`doc_concept__change_process` are available.

General Workflow
****************

The workflows are defined in the :ref:`chm_change_workflows` section.

For every change identified, the following workflows are executed:

* Create your change request according to :need:`wf__change_create_cr`
* Analyze change request report according to :need:`wf__change_analyze_cr`
* Implement change request and monitor it until closure according to :need:`wf__change_implement_monitor_cr`
* Close the change request according to :need:`wf__change_close_cr`

In addition create a change management plan as part of the platform management plan according to :need:`wf__platform_cr_mt_platform_mgmt_plan`
