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

.. doc_getstrt:: Verification Get Started
   :id: doc_getstrt__verification_process
   :status: valid
   :tags: verification

   This document guides you through the initial steps of the software verification process,
   from creating test cases to executing and result reporting.
   It leverages the :need:`doc_concept__verification_process` and :need:`gd_guidl__verification_guide`.

Relevant Documents
******************

Key documents to get an understanding about verification activities are:

* **Concept Document:** :need:`doc_concept__verification_process` provides a high-level overview of the verification concept.
* **Verification Guideline:** :need:`gd_guidl__verification_guide` details test case development, execution, and reporting procedures.
* **Verification Plan:** :need:`wp__verification_plan` implementation outlines the overall verification strategy and objectives.
  (Note that the implementation of the verification plan can be found in the platform management plan.)


General Workflow
****************

The workflows can be split into 4 major parts:

* Test planning filling the template :need:`gd_temp__verification_plan`.
* Test specification and implementation for the respective testing level
* Test execution by the CI.
  (Manual test cases are treated as automated test with user interaction and timeouts.)
* Test reports are created when all verification artifacts on a module and platform level are
  available for a specific baseline.

The details of what needs to be done in each part are described in the :ref:`verification_workflows`.
