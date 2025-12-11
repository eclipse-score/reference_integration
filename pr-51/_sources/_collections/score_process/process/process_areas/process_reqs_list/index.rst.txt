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

.. _process_req:

Process Requirements List
#########################

Automation Status via Process Requirement Table
***********************************************

All process requirements should be labelled with the priorization of automation implementation:

- A label "manual" means nothing to do, because it must be fulfilled manually (e.g. by filling attributes). It can be added a prio (to denote that this req is a must for v0.5 add "prio_1")
- A label "done_automation" means nothing to do, because it already works. Note that in docs-as-code repository there are tool requirements linking to the process requirements with an "Implemented" attribute.
- A label "prio_*_automation" means the prio 1, 2, ... labelled requirement shall be implemented in this order. Prio 1 is everything we need for the re-audit, prio 2 could be done manually as a fallback, prio 3 is nice to have ...

.. needtable::
   :style: table
   :types: gd_req
   :columns: id;status;tags
   :colwidths: 25,10,25
   :sort: id
