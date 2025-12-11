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
####################

.. gd_req:: Static Diagram for Unit Interactions
   :id: gd_req__impl_static_diagram
   :status: valid
   :tags: manual_prio_1, mandatory
   :satisfies: wf__sw_detailed_design
   :complies: std_req__iso26262__software_843

   The static diagram shall represent the unit and their relationships using UML notations.

.. gd_req:: Dynamic Diagram for Unit Interactions
   :id: gd_req__impl_dynamic_diagram
   :status: valid
   :tags: manual_prio_2, mandatory
   :satisfies: wf__sw_detailed_design
   :complies: std_req__iso26262__software_843

   The dynamic diagram shall represent the unit and their relationships using UML notations.

.. gd_req:: Design to Code Linking
   :id: gd_req__impl_design_code_link
   :status: valid
   :tags: prio_1_automation, mandatory
   :satisfies: wf__sw_detailed_design
   :complies: std_req__iso26262__software_843

   The detailed design (units and interfaces in DD document) shall be linked
   to the source code which implements the units and interfaces in the DD.

   Note: Not every code element must have such a link (i.e. is represented in the detailed design),
   these elements are implementation detail.


.. gd_req:: Dependency Analysis
   :id: gd_req__impl_dependency_analysis
   :status: valid
   :tags: prio_2_automation
   :satisfies: wf__sw_verify_implementation
   :complies: std_req__iso26262__software_942

   For each component a dependency tree view shall be created to support design inspection and Safety Analysis.
   It shall show the libraries used by the component (i.e. which libraries are linked to the component, defined as CI build tool target) up to the leaves of the tree.

.. needextend:: docname is not None and "process_areas/implementation" in docname
   :+tags: implementation
