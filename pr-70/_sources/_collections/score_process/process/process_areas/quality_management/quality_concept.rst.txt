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

Concept
#######

.. doc_concept:: Quality Management Concept
   :id: doc_concept__quality_process
   :status: valid
   :tags: quality_management

In this section a concept for the Quality Management will be discussed. Inputs for this concepts is ASPICE SUP.1
as quality standard. And also in aspect to the development the addressed requirements from ISO 26262, ISO/SAE 21434
and ISO PAS 8926.

Inputs
******

#. Stakeholders for the Quality Management
#. Who needs which information?
#. How is Quality ensured?

Stakeholders for the Quality Management
=======================================

#. :need:`Quality Manager <rl__quality_manager>`
     * Creating/maintain Quality Management Plan
     * Verify/approve Platform release
     * Execute Platform Process Audit
     * Execute Feature Contribution Conformance Checks
     * Execute Work Product Reviews
     * Consult and execute Quality Trainings
     * Monitoring/improving of Quality activities

#. :need:`Project Lead <rl__project_lead>`
     * Approval of Platform Release
     * Support the work products
     * Approval of Quality Management Plan, Platform Process Audit, Feature Process Conformance Checks, Work Product Reviews, Consult and Execute Quality Trainings, Monitor/Improve Quality Activities

#. :need:`Committer <rl__committer>`
     * Support the Work Product Reviews

#. :need:`Safety Manager <rl__safety_manager>`
     * Supports the quality activities

#. :need:`Security Manager <rl__security_manager>`
     * Supports the quality activities

Standard Requirements
=====================

Quality requirements of the following standards need to be taken into consideration:

* ASPICE PAM 4.0
* ISO 26262:2018
* ISO 21434:2021
* ISO PAS 8926:2024

General Quality Concept
=======================

The Quality Concept is based on the requirements of the standards and were derived into the Quality Performance
Objectives that are listed in the Quality Management Plan. The Quality shall be continuous
checked and improved during the development. All tasks are planned within the Quality Management Plan. These
includes tasks like platform process audit or feature contribution conformance checks which have to be planed to milestones
or in a continuous manner. Only 100% compliant work products / releases will be formally delivered to the community.

Every person who contributes shall be trained according to Quality aspects. The committers will help to ensure the Quality
by following the workflows which are defined in the different process areas. The Quality Manager is responsible for the
Quality related workflows. The Quality Manager shall be independent from the development organization with a escalation
to the Project Lead Circle.
