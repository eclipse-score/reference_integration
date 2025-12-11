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


.. _workflow_safety_analysis:

Workflow Safety Analysis
########################

Safety Analysis is used as a umbrella term for the methods FMEA (Failure Modes and Effects Analysis) and DFA (Dependent Failure Analysis).

.. workflow:: Analyze Platform Feature Architecture
   :id: wf__analyse_platform_featarch
   :status: valid
   :tags: safety_analysis
   :responsible: rl__safety_engineer
   :approved_by: rl__safety_manager
   :supported_by: rl__contributor, rl__committer, rl__security_manager
   :input: wp__requirements_feat, wp__feature_arch, wp__issue_track_system
   :output: wp__platform_dfa
   :contains: gd_guidl__dfa_failure_initiators, gd_temp__plat_saf_dfa
   :has: doc_concept__safety_analysis, doc_getstrt__safety_analysis

   | With a platform DFA the potential common usage of features shall be analysed. It shall be used as an input for all other DFA's.
   | There will be only one platform DFA.

.. workflow:: Analyse Feature Architecture
   :id: wf__analyse_featarch
   :status: valid
   :tags: safety_analysis
   :responsible: rl__safety_engineer
   :approved_by: rl__safety_manager
   :supported_by: rl__contributor, rl__committer, rl__security_manager
   :input: wp__requirements_feat, wp__feature_arch, wp__issue_track_system
   :output: wp__feature_fmea, wp__feature_dfa
   :contains: gd_guidl__dfa_failure_initiators, gd_temp__feat_saf_dfa, gd_guidl__fault_models, gd_temp__feat_saf_fmea
   :has: doc_concept__safety_analysis, doc_getstrt__safety_analysis

   | The FMEA and DFA for the feature is executed.

.. workflow:: Analyse Component Architecture
   :id: wf__analyse_comparch
   :status: valid
   :tags: safety_analysis
   :responsible: rl__safety_engineer
   :approved_by: rl__safety_manager
   :supported_by: rl__contributor, rl__committer, rl__security_manager
   :input:  wp__requirements_comp, wp__component_arch, wp__issue_track_system
   :output: wp__sw_component_fmea, wp__sw_component_dfa
   :contains: gd_guidl__dfa_failure_initiators, gd_temp__comp_saf_dfa, gd_guidl__fault_models, gd_temp__comp_saf_fmea
   :has: doc_concept__safety_analysis, doc_getstrt__safety_analysis

   | The FMEA and DFA for the component is executed.

.. workflow:: Monitor FMEA and DFA
   :id: wf__mr_saf_analyses_dfa
   :status: valid
   :tags: safety_analysis
   :responsible: rl__safety_engineer
   :approved_by: rl__safety_manager
   :supported_by: rl__contributor, rl__committer, rl__security_manager
   :input: wp__feature_fmea, wp__feature_dfa, wp__sw_component_fmea, wp__sw_component_dfa
   :output: wp__verification_platform_ver_report, wp__issue_track_system, wp__verification_module_ver_report
   :contains: gd_guidl__dfa_failure_initiators, gd_temp__feat_saf_dfa, gd_temp__comp_saf_dfa, gd_guidl__fault_models, gd_temp__feat_saf_fmea, gd_temp__comp_saf_fmea
   :has: doc_concept__safety_analysis, doc_getstrt__safety_analysis

   | The FMEA and DFA are monitored.

.. workflow:: Verify FMEA and DFA
   :id: wf__vy_saf_analyses_dfa
   :status: valid
   :tags: safety_analysis
   :responsible: rl__safety_engineer
   :approved_by: rl__safety_manager
   :supported_by: rl__contributor, rl__committer, rl__security_manager
   :input: wp__platform_dfa, wp__feature_fmea, wp__feature_dfa, wp__sw_component_fmea, wp__sw_component_dfa
   :output: wp__verification_platform_ver_report, wp__verification_module_ver_report
   :contains: gd_guidl__dfa_failure_initiators, gd_temp__feat_saf_dfa, gd_temp__comp_saf_dfa, gd_guidl__fault_models, gd_temp__feat_saf_fmea, gd_temp__comp_saf_fmea, gd_chklst__safety_analysis
   :has: doc_concept__safety_analysis, doc_getstrt__safety_analysis

   | The FMEA and DFA are verified. The verification criteria is that it can be proven that the safety requirements for functions and the corresponding safety monitoring are not violated.


RAS(IC) for Safety Analysis  (FMEA and DFA)
*******************************************


.. needtable:: RASIC Overview for Safety Analysis  (FMEA and DFA)
   :tags: safety_analysis
   :filter: "safety_analysis" in tags and type == "workflow" and is_external == False
   :style: table
   :sort: status
   :columns: id as "Activity";responsible as "Responsible";approved_by as "Approver";supported_by as "Supporter"
   :colwidths: 30,30,30,30
