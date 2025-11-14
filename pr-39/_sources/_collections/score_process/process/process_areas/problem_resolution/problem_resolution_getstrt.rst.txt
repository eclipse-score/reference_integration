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

.. doc_getstrt:: Getting Started on Problem Resolution
   :id: doc_getstrt__problem_process
   :status: valid
   :tags: problem_resolution

This document describes the steps to create a problem report, and further to analyze,
resolve, and to control the problem until closure. Where a problem is defined as a
deviation of an expected result.

Examples for problem origins:

* Deviations relating to requirements, architecture, implementation or code found by user of the platform.
* Deviations found by contributor based on component, feature or Platform Integration Tests.
* Deviations found by Quality Management activities as defined in the Quality Management Plan.

Therefore guidelines :need:`gd_temp__problem_template`,
:need:`gd_guidl__problem_problem` and a :need:`doc_concept__problem_process`
are available.

General Workflow
****************

The workflows are defined in the :ref:`problem_workflows` section.

For every problem identified, the following workflows are executed:

* Create your problem report according to :need:`wf__problem_create_pr`
* Analyze your problem report according to :need:`wf__problem_analyze_pr`
* Initiate problem resolution and monitor it until closure according to :need:`wf__problem_initiate_monitor_pr`
* Close the problem resolution according to :need:`wf__problem_close_pr`

In addition create a problem resolution plan as part of the platform management plan according to :need:`wf__platform_cr_mt_platform_mgmt_plan`.
