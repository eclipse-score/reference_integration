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

.. _workflows:

Workflows
=========

A workflow is a structured sequence of activities designed to achieve specific objectives within a project or process area. It serves as the central organizing element of the process model, defining the steps required to complete a particular task or produce specific outcomes.

There are no general workflows.

Project Workflow list
---------------------

.. needtable::
   :style: table
   :columns: title;id;tags
   :colwidths: 25,25,25
   :sort: title

   results = []

   for need in needs.filter_types(["workflow"]):
         if need['is_external'] == False:
                results.append(need)
