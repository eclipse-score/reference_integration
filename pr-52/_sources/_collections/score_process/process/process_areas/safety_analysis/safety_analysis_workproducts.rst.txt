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

Safety Analysis Work Products
#############################

.. workproduct:: Platform DFA
   :id: wp__platform_dfa
   :status: valid
   :complies: std_wp__iso26262__software_751, std_wp__iso26262__software_753, std_wp__isopas8926__4524

   Analyse the dependencies between features that references all platform feature static architecture diagrams, highlighting potential shared use of modules.

.. workproduct:: Feature FMEA
   :id: wp__feature_fmea
   :status: valid
   :complies: std_wp__iso26262__software_751, std_wp__iso26262__analysis_851, std_wp__isopas8926__4524

   FMEA verifies the feature architecture (as part of SW Safety Concept)

   Detections, preventions, mitigations linked to Software Feature Requirements or Feature Assumptions of Use.

.. workproduct:: Feature DFA
   :id: wp__feature_dfa
   :status: valid
   :complies: std_wp__iso26262__software_751, std_wp__iso26262__software_753, std_wp__isopas8926__4524

   Dependent Failure Analysis on feature level.

   Detections, preventions, mitigations linked to Software Feature Requirements or Feature Assumptions of Use.

   Perform analysis on interactions between safety related and non-safety related modules or modules with different ASIL of one feature.

.. workproduct:: Component FMEA
   :id: wp__sw_component_fmea
   :status: valid
   :complies: std_wp__iso26262__analysis_751, std_wp__iso26262__analysis_851, std_wp__isopas8926__4524, std_wp__iso26262__software_752

   FMEA, verifies the component architecture (as part of SW Safety Concept)

   Detections, preventions, mitigations linked to Software Component Requirements or Assumptions of Use.

.. workproduct:: Component DFA
   :id: wp__sw_component_dfa
   :status: valid
   :complies: std_wp__iso26262__analysis_751, std_wp__iso26262__software_753, std_wp__isopas8926__4524, std_wp__iso26262__software_752

   Dependent Failure Analysis on component/module level.

   Detections, preventions, mitigations linked to Software Component Requirements or Assumptions of Use.

   Perform analysis of safety related and non-safety related sub-elements or sub-elements with different ASIL.

   Perform analysis on interactions between safety related and non-safety related sub-components or sub-components with different ASIL of one component. Including potential influences from the other components in the component's module.
