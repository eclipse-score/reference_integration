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

Modules
=======

.. The toctrees below stay empty in source: the `bundles` of the `docs()` macro in the root
   BUILD file mount every module from known_good.json here, target_sw modules into the
   first toctree and tooling modules into the second (see `toctree_index`). Their captions
   group the left section navigation; on this page the section headings show instead.

Functional Modules
------------------

S-CORE software modules that ship in the integration.

.. toctree::
   :caption: Functional Modules
   :class: modules-toc
   :titlesonly:
   :maxdepth: 1

.. Communication publishes no docs bundle; its dependable element docs are copied next
   to this site by CI, so they are linked here instead of mounted.

.. rst-class:: modules-list-continued

* `Communication <score_communication/dependable_element/mw_com_doc/index.html>`_
  (mw_com, built per module in CI and published next to these docs)

Non-Functional Modules
----------------------

Process description, platform standards, test framework and documentation toolchain.

.. toctree::
   :caption: Non-Functional Modules
   :class: modules-toc
   :titlesonly:
   :maxdepth: 1
