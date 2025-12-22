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

Process Requirements
====================

.. gd_req:: Release note automated generation
   :id: gd_req__release_note
   :status: valid
   :tags: prio_2_automation, release_management
   :satisfies: wf__rel_platform_rel_note, wf__rel_mod_rel_note
   :complies: std_req__iso26262__management_64134, std_req__iso26262__management_64135, std_req__aspice_40__SUP-8-BP7

   | The release note shall be generated progressively and automatically compiling the content as far as possible.
   | This shall be done according to templates :need:`gd_temp__rel_plat_rel_note` and :need:`gd_temp__rel_mod_rel_note`.
