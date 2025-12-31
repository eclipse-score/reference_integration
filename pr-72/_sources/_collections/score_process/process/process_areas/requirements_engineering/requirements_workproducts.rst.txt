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

Requirements Engineering Work Products
######################################

.. workproduct:: Stakeholder Requirements
   :id: wp__requirements_stkh
   :status: valid
   :complies: std_wp__iso26262__system_651

   Technical requirements from a stakeholder viewpoint on SW-platform level, contain "assumed Technical Safety Requirements" in SW-Platform SEooC development.

.. workproduct:: Feature Requirements
   :id: wp__requirements_feat
   :status: valid
   :complies: std_wp__iso26262__software_651

   Feature requirements describe in a more detailed way the functionality which will fulfill a set of stakeholder requirements. A "feature" itself represents a set of requirements. It describes the interaction of the components to form a feature. It shall also be the basis for integration testing on platform level.

.. workproduct:: Component Requirements
   :id: wp__requirements_comp
   :status: valid
   :complies: std_wp__iso26262__software_651, std_wp__isopas8926__4521, std_wp__iso26262__analysis_651, std_wp__iso26262__software_app_c_51

   SW Requirements for components, broken down from feature requirements to the realizing component. These include configuration specification.

.. workproduct:: SW-Platform Assumptions of Use
   :id: wp__requirements_sw_platform_aou
   :status: valid
   :complies: std_wp__iso26262__software_651

   SW Safety Requirements for the user of the platform, exportable requirements for the user to integrate in their requirements management system.

.. workproduct:: Feature Assumptions of Use
   :id: wp__requirements_feat_aou
   :status: valid
   :complies: std_wp__iso26262__software_651

   SW Safety Requirements for the user of the feature, exportable requirements for the user to integrate in their req mgt system.

.. workproduct:: Component Assumptions of Use
   :id: wp__requirements_comp_aou
   :status: valid
   :complies: std_wp__iso26262__software_651, std_wp__isopas8926__4521

   SW Safety Requirements for the user of the component, exportable requirements for the user to integrate in their req mgt system.

.. workproduct:: Process/Tool Requirements
   :id: wp__requirements_proc_tool
   :status: valid

   Process and Tool requirements describe activities needed to be executed in the development process either manually or automated (i.e. tool supported).
   Tool requirements (if derived from process requirements) are more detailed as those are also the basis for tool (qualification) testing.

.. workproduct:: Requirements Inspection
   :id: wp__requirements_inspect
   :status: draft
   :complies: std_wp__iso26262__software_653

   Depends on requirements management tooling, expect text based requirements.

   Review done with inspection checklist. This checklist may be integrated in requirements/version management tooling.

.. needextend:: docname is not None and "process_areas/requirements_engineering" in docname
   :+tags: requirements_engineering
