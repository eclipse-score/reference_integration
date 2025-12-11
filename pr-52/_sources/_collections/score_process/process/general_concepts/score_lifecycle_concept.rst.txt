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

.. _general_concepts_lifecycle:

Lifecycle concept
-----------------

Contributions to the project are driven by feature/component requests.

As features and components are the main structuring elements of the project, new
features and components are requested by feature or components requests (compare
:need:`wf__change_create_cr`). Both are special types of change requests.

The figure below shows the standard lifecycle of any feature/component in the project.

.. figure:: _assets/score_lifecycle_model.drawio.svg
  :width: 100%
  :align: center
  :alt: Lifecycle model for the project

  Lifecycle model for the project

A new feature or component request starts the **Concept Phase**.
The **Concept Phase** is used to provide feasibility and further decision criteria, which
are needed to finally accept the new feature/component for the project platform.
The request may be supported by source code provided within incubator repositories. In
this phase only the the :need:`Change Management<doc_getstrt__change_process>` process
needs to be executed, all other processes are optional.

Accepted features or components must be planned and developed according the defined
project processes. Thus the accepted feature/component request starts the **Development Phase**.
During the **Development Phase** the feature/component implementation is initially
planned, before it is implemented and verified. The development may based on several
iterative implementation cycles. Any modification of the original feature/component
request may re-trigger the start of the development phase, as impact analysis and
re-planning may required. The development is planned, checked and adjusted to meet the
objectives. Planning is also required from several standards to provide necessary
artifacts aka work products especially to achieve functional safety. Finally the implemented
features/components are released.

Released features/components are maintained after their first major release. They may
have bugs so a problem report for the released feature/component starts the
**Maintenance Phase**. In this phase the :need:`Problem Resolution<doc_getstrt__problem_process>`
process must be applied. Depending on the reported problem and the agreed resolution,
also other process areas may apply. After resolving the problem the release version of
the features/components will change (e.g. minor, patch), but they are still in maintenance.

If the problem resolution requires a change request, then the feature will trigger again
a **Development Phase**. Also feature/component modifications (e.g. change or adding
new API) result in a change request. In this case the existing feature/component request
is modified and thus starts the **Development Phase** again.

Mandatory Processes for each Phase

.. list-table:: Mandatory Processes for each Phase
   :header-rows: 1
   :widths: 30,60

   * - Phase
     - Mandatory processes
   * - Concept
     - :need:`Change Management<doc_getstrt__change_process>`
   * - Development
     - All processes as defined in the :need:`wp__platform_mgmt`
   * - Maintenance
     - :need:`Problem Resolution<doc_getstrt__problem_process>`, and all applicable to resolve the problem
