..
   # *******************************************************************************
   # Copyright (c) 2026 Contributors to the Eclipse Foundation
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

Step 4 — Get built and tested on the target platforms
=====================================================

   **What this unlocks:** your module is actually **compiled and tested by the
   pipelines** — built for and deployed to every target platform (Linux x86_64,
   QNX, AutoSD, EBcLfSA aarch64), offered in the interactive CLI, and exercised
   by CI. This is the rung that turns a library into something that *runs* inside
   the integration images.

The integration ships four target images, each built and tested by its own
gating CI job. The table lists the platforms, the image target, the runner used
to execute it, and the per-platform CI check.

.. _supported_platforms:

.. list-table:: Supported target platforms
   :header-rows: 1
   :widths: 22 14 22 22 20

   * - Platform
     - Arch
     - Image
     - Runner
     - Build & test workflow
   * - Linux
     - x86_64
     - `images/linux_x86_64 <../../images/linux_x86_64>`_
     - Docker (`runners/docker_x86_64 <../../runners/docker_x86_64>`_)
     - `build_and_test_linux.yml <../../.github/workflows/build_and_test_linux.yml>`_
   * - QNX 8
     - x86_64
     - `images/qnx_x86_64 <../../images/qnx_x86_64>`_
     - QEMU (`runners/qemu_x86_64 <../../runners/qemu_x86_64>`_)
     - `build_and_test_qnx.yml <../../.github/workflows/build_and_test_qnx.yml>`_
   * - Red Hat AutoSD
     - x86_64
     - `images/autosd <../../images/autosd>`_
     - Docker (`runners/docker_x86_64 <../../runners/docker_x86_64>`_)
     - `build_and_test_autosd.yml <../../.github/workflows/build_and_test_autosd.yml>`_
   * - EB corbos Linux (Safety Apps)
     - aarch64
     - `images/ebclfsa_aarch64 <../../images/ebclfsa_aarch64>`_
     - QEMU (`runners/qemu_aarch64 <../../runners/qemu_aarch64>`_)
     - `build_and_test_ebclfsa.yml <../../.github/workflows/build_and_test_ebclfsa.yml>`_

.. note::

   The EB corbos *Safety Applications* image is special: it runs a
   high-integrity application demo under additional constraints. Read
   `images/ebclfsa_aarch64/README.md <../../images/ebclfsa_aarch64/README.md>`_
   before targeting it.

Run any image locally in QEMU
-----------------------------

Every image exposes a ``:run`` target that boots it in an emulator, so you can
try your module on the real target without hardware:

.. code-block:: bash

   bazel run //images/linux_x86_64:run
   bazel run //images/qnx_x86_64:run
   bazel run //images/autosd:run
   bazel run //images/ebclfsa_aarch64:run

The QNX and aarch64 images boot under QEMU, which needs a one-time host setup
(TUN device, bridge helper, libvirt network). Follow the QEMU runner how-to in
`runners/qemu_x86_64/README.md <../../runners/qemu_x86_64/README.md>`_ before the
first run.

Two ways to get your module onto the images
-------------------------------------------

There are two ways to make your binary part of the images:

* **As a showcase (recommended).** Bundle your binary once into the aggregate
  ``//showcases`` package; it is then deployed into **every** image
  automatically — one change covers all four platforms, and the binary is also
  offered in the interactive CLI. See :ref:`add_showcase` below.
* **Directly into each image.** Wire the binary into each image's build
  description by hand. This is **per-image work that you repeat four times**
  (once per image) and is only needed for components that are not run as a CLI
  showcase — typically a daemon. The ``datarouter`` is integrated this way; see
  how the QNX image does it in
  `images/qnx_x86_64/build/BUILD <../../images/qnx_x86_64/build/BUILD>`_ (the
  ``datarouter`` source and the ``DATAROUTER_PATH`` mapping). See
  :ref:`add_directly` below. Prefer the showcase route unless you have a reason
  not to.

.. _add_showcase:

4.1 Add a runtime showcase
--------------------------
A *showcase* is the vehicle that gets your module onto the platforms: you bundle
a runnable binary, and the aggregate ``//showcases`` package is deployed into
**every** image automatically. You do this once — there is no per-platform work.

There are two patterns under `showcases/ <../../showcases>`_:

* **Standalone** (`showcases/standalone <../../showcases/standalone>`_) — bundle
  a binary that already exists in your module's repo.
* **Composed** (e.g.
  `showcases/orchestration_persistency <../../showcases/orchestration_persistency>`_)
  — a small binary defined *here* that combines several modules.

**1. Define the bundle.** Add a ``score_pkg_bundle`` target. To re-use a binary
that lives in your module:

.. code-block:: python

   load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

   score_pkg_bundle(
       name = "my_module",
       bins = ["@score_my_module//examples:my_example"],
       config_data = ["//showcases/standalone:my_module.score.json"],
       package_dir = "standalone",
   )

**2. Add a CLI descriptor.** Create a ``*.score.json`` next to the bundle. The
CLI auto-discovers every ``*.score.json`` deployed under ``/showcases`` and
offers it in the interactive menu, so **no code change to the CLI is required**:

.. code-block:: json

   {
       "name": "My Module Example",
       "description": "Demonstrates my_module at runtime",
       "apps": [
           {
               "path": "/showcases/bin/my_example",
               "args": [],
               "env": {},
               "dir": "/showcases/data/my_module"
           }
       ]
   }

**3. Register the bundle in the top-level showcase package.** Add your bundle to
the aggregate ``score_pkg_bundle`` in
`showcases/BUILD <../../showcases/BUILD>`_ so it is packaged into the images:

.. code-block:: python

   score_pkg_bundle(
       name = "showcases",
       bins = ["//showcases/cli"],
       other_package_files = [
           "//showcases/standalone:comm_pkg_files",
           # ...
           "//showcases/standalone:my_module_pkg_files",
       ],
       package_dir = "showcases",
   )

Once your bundle is part of ``//showcases``, it is reachable from
``//images/<platform>:image`` and is therefore **built by every platform CI
job** automatically.

.. _add_directly:

4.2 Add a binary directly to an image
-------------------------------------

If your component is not a CLI showcase — for example a background daemon that
must always be present — you wire it straight into each image's build
description instead. Unlike the showcase route, **this is per-image work: you
repeat it for every image you target** (Linux, QNX, AutoSD, EBcLfSA).

The reference example is the ``datarouter``. In the QNX image it is added as a
source of the image target and exposed to the image's build description via a
location mapping, then placed into the filesystem by ``system.build``:

.. code-block:: python

   # images/qnx_x86_64/build/BUILD
   qnx_ifs(
       name = "init",
       srcs = [
           # ...
           "//showcases",
           "@score_logging//score/datarouter",
           "//feature_integration_tests/configs/datarouter:etc_configs",
       ],
       ext_repo_maping = {
           "BUNDLE_PATH": "$(location //showcases:showcases)",
           "DATAROUTER_PATH": "$(location @score_logging//score/datarouter:datarouter)",
       },
   )

See `images/qnx_x86_64/build/BUILD <../../images/qnx_x86_64/build/BUILD>`_ and the
matching deployment lines in
`images/qnx_x86_64/build/system.build <../../images/qnx_x86_64/build/system.build>`_
for the full picture, and repeat the equivalent wiring in the other images you
need (`images/linux_x86_64 <../../images/linux_x86_64>`_,
`images/autosd <../../images/autosd>`_,
`images/ebclfsa_aarch64 <../../images/ebclfsa_aarch64>`_).

If your module simply cannot run on a given platform, exclude its targets via
``metadata.exclude_test_targets`` / ``metadata.extra_test_config`` in
``known_good.json`` (Step 1) rather than editing the workflow.
