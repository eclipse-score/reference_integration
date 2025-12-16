..
   # *******************************************************************************
   # Copyright (c) 2024 Contributors to the Eclipse Foundation
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

.. _processes_introduction:

Introduction
============

.. doc_concept:: Process Meta Model
   :id: doc_concept__process_meta_model
   :status: valid
   :tags: process_management

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Motivation
----------

The process model aims to establish organization rules for developing
open source software in the automotive industry, which can be used in safety and security context.

Objectives
----------

The process model shall provide processes, which conform to state-of the art standards

* :ref:`ASPICE<standard_aspice_pam4>`
* :ref:`ISO 26262<standard_iso26262>`
* :ref:`ISO 21434<standard_isosae21434>`
* :ref:`ISO PAS 8926<standard_isopas8926>`

Approach
--------

1. We aim for a process model as common basis for process documentation (compare figure below).
2. We work code centric (trace text as code) and iteratively.
3. We aim to develop the process in conformance to the targeted standards (compare figure below).
4. We aim to establish traceability from the begin (compare :ref:`general_concepts_traceability`).
5. We aim to verify conformity and traceability by tool automation as much as possible (compare figure below).
6. We aim for an iterative collaboration model initiated by change requests (compare :need:`gd_guidl__change_change_request`).


.. figure:: _assets/score_process_model.drawio.svg
  :width: 100%
  :align: center
  :alt: Overview process model

  Overview process model

The process model is structured around the concept of :ref:`workflows<workflows>`, which form the core of each :ref:`process<process_areas>`. Each workflow defines the sequence of activities required to achieve specific objectives within the project. The activities linked from these workflows are directly linked to roles, ensuring that responsibilities and accountabilities are clearly assigned throughout the process.

Workflows also establish connections to :ref:`work products<work_products>`, which are often inputs and the tangible outputs or artifacts generated during process execution. Each work product is associated with or requested by relevant :ref:`standards<external_standards>` and :ref:`requirements<process_req>` of these standards, ensuring compliance and traceability.

To facilitate onboarding and understanding, the process model provides dedicated sections for a "Getting Started" and a detailed "Concept Description" for each process. These resources help Contributors, Committers and other Users quickly familiarize themselves with the process, understand key concepts, and apply best practices throughout process execution and should be read in this order. See :need:`Requirements process getting started<doc_getstrt__req_process>`, :need:`Requirement concept description<doc_concept__req_process>` as examples.

The model further integrates an comprehensive guideline (within the "Guidance" section), :ref:`templates<folder_templates>`, checklists and methods for each workflow to support the consistent and efficient execution of processes. See the :need:`Requirement process guideline<gd_guidl__req_engineering>`, the :need:`requirement inspection checklist<doc__feature_name_req_inspection>` and :need:`verification methods<gd_meth__verification_methods>` as examples.

Additionally, the process model incorporates traceability mechanisms, allowing for the verification of conformity to standards such as ASPICE, ISO 26262, and others. The relationships between workflows, roles, work products, and supporting materials are visualized in the process model diagram above, providing a clear overview of how all elements interact to support process development and continuous improvement within the organization.

The process model follows a code-centric, iterative approach that establishes :ref:`traceability<general_concepts_traceability>` according to the :ref:`meta model of the building blocks<general_concepts_building_blocks>` from the beginning and leverages tool automation to verify conformity and traceability as much as possible. Tools are evaluated and :ref:`qualified<tools_template>` by Committers, used by Contributors to execute workflows, and must fulfill defined process requirements to support efficient and compliant process execution.
