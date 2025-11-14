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

Example: Detailed Design
========================

Description
-----------

 - component is split into two units unit1 and unit2 based on single responsibility principle.
 - unit2 is injected to unit1 one via dependency injection for testability.


Static Diagrams for Unit Interactions
-------------------------------------

.. dd_sta:: dd example static
    :id: dd_sta__example_feature__doc_approver
    :security: NO
    :safety: ASIL_B
    :status: valid
    :implements: comp_req__example_feature__archdes_example_req
    :satisfies: comp_arc_sta__example_feature__archdes_sub_component_1
    :includes: sw_unit__example_feature__unit1, sw_unit__example_feature__unit2

.. uml:: dd_example_ex_sta.puml

Dynamic Diagrams for Unit Interactions
--------------------------------------

.. dd_dyn:: dd example dynamic
    :id: dd_dyn__example_feature__dd_example_dynamic
    :security: NO
    :safety: ASIL_B
    :status: valid
    :implements: comp_req__example_feature__archdes_example_req
    :satisfies: comp_arc_sta__example_feature__archdes_sub_component_1

.. uml:: dd_example_ex_dyn.puml

Units within the Component
--------------------------
From here onwards the needs are defined in the source code and will be automatically generated and linked via doxygen.

SW Unit
*******

.. sw_unit:: unit1
    :id: sw_unit__example_feature__unit1
    :security: NO
    :safety: ASIL_B
    :status: valid

    Placeholder for the description that will be generated from doxygen

Interface
*********

.. sw_unit_int:: int1
    :id: sw_unit_int__example_feature__unit1_int1
    :security: NO
    :safety: ASIL_B
    :status: valid

    Placeholder for the description that will be generated from doxygen

SW Unit
*******

.. sw_unit:: unit2
    :id: sw_unit__example_feature__unit2
    :security: NO
    :safety: ASIL_B
    :status: valid

    Placeholder for the description that will be generated from doxygen

Interface
*********

.. sw_unit_int:: int2
    :id: sw_unit_int__example_feature__unit2_int2
    :security: NO
    :safety: ASIL_B
    :status: valid

    Placeholder for the description that will be generated from doxygen
