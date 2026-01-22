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

Release Management Work Products
################################

.. workproduct:: Platform Release Notes
   :id: wp__platform_sw_release_note
   :status: valid
   :complies: std_wp__iso26262__management_656

   The platform release note provides clarity what is included in the current version of the platform
   release. The platform release note mentions all individual software modules used in the platform
   release and their used released versions. It shall indicate also the distinct changes to previous
   platform versions and provide information regarding the time of the release.
   It includes known bugs from own testing and field reporting, with clear statement,
   that these bugs do not lead to violation of any safety requirements or which workaround measures need to be applied.
   It contains also the build configuration capable to create the SEooC Library for the
   reference HW, platform level.

   Note: Embedded software in the sense of the Iso (i.e. deployed on the production HW)
   is not part of our delivery.

.. workproduct:: Module Release Notes
   :id: wp__module_sw_release_note
   :status: valid
   :complies: std_wp__iso26262__management_656

   The module release note provides clarity what is included in the current version of the software
   module release. It shall indicate also the distinct changes to previous versions and provide
   information regarding the time of the release. It includes known bugs from own testing and field reporting,
   with clear statement, that these bugs do not lead to violation of any safety requirements or
   which workaround measures need to be applied.
   It contains also the build configuration capable to create the SEooC Library for the
   reference HW, module level.

   Note: Embedded software in the sense of the Iso (i.e. deployed on the production HW)
   is not part of our delivery.

.. workproduct:: Platform Release Plan
   :id: wp__platform_sw_release_plan
   :status: valid

   The platform release plan is a high-level document that outlines which software modules
   will be included in the overall platform and what features can be expected within the platform.
   It provides a strategic overview of the platform's development, ensuring that all
   stakeholders are aligned on the platform's future direction and the integration of
   various software modules.

.. workproduct:: Module Release Plan
   :id: wp__module_sw_release_plan
   :status: valid

   The module release plan is a strategic document that outlines the features planned for upcoming
   module releases along with their estimated release dates. It provides a roadmap for the
   development and release of new features, ensuring that all stakeholders are aligned on the
   module's future direction.

.. workproduct:: Platform Handbook
   :id: wp__platform_handbook
   :status: valid

   The platform handbook is a tutorial to explain how the project works from a technical
   perspective. It explains the background of the project, but also what the project is
   not about.

   Further it contains:

   - Overview of the technologies used within the project
   - Software architecture overview
   - Module structure overview
   - Integration process
   - Getting started guide
   - Contribution guide
