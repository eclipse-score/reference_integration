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

.. doc_getstrt:: Getting Started on Requirements
   :id: doc_getstrt__req_process
   :status: valid
   :tags: requirements_engineering

This document describes the steps which need to be done to create requirements, derive child requirements and finally to perform the formal requirement inspection.

For this a :need:`[[title]] <gd_guidl__req_engineering>`, :ref:`requirement templates` and a :need:`[[title]] <doc_concept__req_process>` are available.

The subsequent steps of linking requirements to code and test cases are described in different guidelines:

Linking Requirements

* to code: :need:`gd_guidl__implementation`
* to tests: :need:`gd_guidl__verification_guide`

General Workflow
****************

.. figure:: _assets/requirements_workflow.drawio.svg
   :align: center
   :width: 80%
   :name: requirements_workflow_fig

   Requirements Workflow

The details of what needs to be done in each steps are described in the :ref:`workflow_requirements`

Tooling Support
***************

The requirements templates and examples are built by using the means of a specific "Docs-as-Code" tool,
but this does not mean that projects are required to use this, as long as the content (e.g. attributes)
and functionality described in :ref:`process_requirements` is covered by the selected tool.
