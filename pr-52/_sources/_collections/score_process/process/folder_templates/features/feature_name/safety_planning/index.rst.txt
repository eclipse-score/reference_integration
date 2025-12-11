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

.. _feature_safety_wp_template:

Feature Safety Planning
=======================

.. document:: [Your Feature Name] Safety WPs
   :id: doc__feature_name_safety_wp
   :status: draft
   :safety: ASIL_B
   :realizes: wp__platform_safety_plan
   :tags: template

.. attention::
    The above directive must be updated according to your Feature.

    - Modify ``Your Feature Name`` to be your Feature Name
    - Modify ``id`` to be your Module Name in upper snake case preceded by ``doc__`` and succeeded by ``_safety_wp``
    - Adjust ``status`` to be ``valid``
    - Adjust ``safety`` and ``tags`` according to your needs

.. list-table:: Feature <feature_name> Work products
    :header-rows: 1

    * - Work product Id
      - Link to process
      - Process status
      - Link to issue
      - Link to WP
      - WP/doc status

    * - :need:`wp__feat_request`
      - :need:`gd_temp__change_feature_request`
      - :ndf:`copy('status', need_id='gd_temp__change_feature_request')`
      - <link to issue>
      - :need:`doc__feature_name`
      - :ndf:`copy('status', need_id='doc__feature_name')`

    * - :need:`wp__requirements_feat`
      - :need:`gd_temp__req_feat_req`
      - :ndf:`copy('status', need_id='gd_temp__req_feat_req')`
      - <link to issue>
      - :need:`doc__feature_name_requirements`
      - doc :ndf:`copy('status', need_id='doc__feature_name')` & WP below

    * - :need:`wp__requirements_feat_aou`
      - :need:`gd_temp__req_aou_req`
      - :ndf:`copy('status', need_id='gd_temp__req_aou_req')`
      - <link to issue>
      - :need:`doc__feature_name_requirements`
      - doc :ndf:`copy('status', need_id='doc__feature_name')` & WP below

    * - :need:`wp__feature_arch`
      - :need:`gd_temp__arch_feature`
      - :ndf:`copy('status', need_id='gd_temp__arch_feature')`
      - <link to issue>
      - :need:`doc__feature_name_architecture`
      - doc :ndf:`copy('status', need_id='doc__feature_name_architecture')` & WP below

    * - :need:`wp__feature_fmea`
      - :need:`gd_temp__feat_saf_fmea`
      - :ndf:`copy('status', need_id='gd_temp__feat_saf_fmea')`
      - <link to issue>
      - :need:`doc__feature_name_fmea`
      - doc :ndf:`copy('status', need_id='doc__feature_name_fmea')` & WP below

    * - :need:`wp__feature_dfa`
      - :need:`gd_temp__feat_saf_dfa`
      - :ndf:`copy('status', need_id='gd_temp__feat_saf_dfa')`
      - <Link to issue>
      - :need:`doc__feature_name_dfa`
      - doc :ndf:`copy('status', need_id='doc__feature_name_dfa')` & WP below

    * - :need:`wp__requirements_inspect`
      - :need:`gd_chklst__req_inspection`
      - :ndf:`copy('status', need_id='gd_chklst__req_inspection')`
      - n/a
      - Checklist used in Pull Request Review
      - n/a

    * - :need:`wp__sw_arch_verification`
      - :need:`gd_chklst__arch_inspection_checklist`
      - :ndf:`copy('status', need_id='gd_chklst__arch_inspection_checklist')`
      - n/a
      - Checklist used in Pull Request Review
      - n/a

    * - :need:`wp__verification_feat_int_test`
      - :need:`gd_guidl__verification_guide`
      - :ndf:`copy('status', need_id='gd_guidl__verification_guide')`
      - <link to issue>
      - <Link to WP>
      - <automated>

.. attention::
    The above table must be updated according to your feature safety planning.

    - Create and link the issues to plan the work products (according to :need:`gd_guidl__saf_plan_definitions`)
    - Fill the work producs links and add their status (also possible below) to create the safety package (according to :need:`gd_guidl__saf_package`)

Feature Requirements Status
---------------------------

.. needtable::
   :filter: "feature_name" in docname and "requirements" in docname and docname is not None
   :style: table
   :types: feat_req
   :tags: feature_name
   :columns: id;status
   :colwidths: 25,25
   :sort: title

Feature AoU Status
------------------

.. needtable::
   :filter: "feature_name" in docname and "requirements" in docname and docname is not None
   :style: table
   :types: aou_req
   :tags: feature_name
   :columns: id;status
   :colwidths: 25,25
   :sort: title

Feature Architecture Status
---------------------------

.. needtable::
   :filter: "feature_name" in docname and "requirements" in docname and docname is not None
   :style: table
   :types: feat_arc_sta; feat_arc_dyn
   :tags: feature_name
   :columns: id;status
   :colwidths: 25,25
   :sort: title
