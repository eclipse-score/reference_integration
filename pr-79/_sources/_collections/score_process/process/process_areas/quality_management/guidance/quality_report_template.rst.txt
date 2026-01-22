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

.. _quality_report_template:

Template Quality Report
=======================

.. gd_temp:: Quality Report Template
   :id: gd_temp__qlm_report
   :status: valid
   :complies: std_req__iso26262__management_5423, std_req__aspice_40__SUP-1-BP1, std_req__aspice_40__SUP-1-BP2, std_req__aspice_40__SUP-1-BP3, std_req__aspice_40__SUP-1-BP4, std_req__aspice_40__SUP-1-BP7, std_req__aspice_40__PIM-3-BP1, std_req__aspice_40__PIM-3-BP2, std_req__aspice_40__PIM-3-BP3, std_req__aspice_40__PIM-3-BP4, std_req__aspice_40__PIM-3-BP5, std_req__aspice_40__PIM-3-BP6, std_req__aspice_40__PIM-3-BP7

   This document implements :need:`wp__qms_report` and based on the :need:`wp__qms_plan`. It summarizes
   the results of the quality related activities. It shall be referred in the :need:`wp__platform_sw_release_note`
   of a platform release.

   The Quality Report contains:

   **1. Quality Overview**

   **1.1. Quality Objectives and Goals**
    - Quality objectives and goals as defined in the :need:`wp__qms_plan`
    - Status of achievement of the quality objectives and goals

   **1.2. Lists of all work products**
    - List of all work products, compared to the :need:`wp__qms_plan`
    - Status (valid / invalid)

   **1.3. Lists of all reports**
    - List of all reports, compared to the :need:`wp__qms_plan`
    - Results of the reports

   **1.4. Test coverage**
    - Overview of test coverage (overall, requirements, architecture)
    - Ratio of test coverage to the :need:`wp__verification_plan`

   **1.5. Issues**
    - List of all issues, compared to the :need:`wp__qms_plan`
    - Status of the issues (open / closed)

   **1.6. Process Improvement**
    - List of all process improvements, compared to the :need:`wp__process_impr_report`
    - Status of the process improvements (open / closed)

    **Note1:** All the above lists are generated automatically
