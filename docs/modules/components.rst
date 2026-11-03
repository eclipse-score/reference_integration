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

Components and Bazel targets
============================

The table lists all component needs (``comp``) available in the integrated
documentation, including imported needs. Bazel targets and rule types come from
the ``bazel_target`` and ``bazel_type`` metadata supplied by the documentation
bundles. Empty cells indicate that no corresponding metadata is available.
If a component has multiple targets, the target and type lists use the same
order: each type describes the target at the corresponding position.

.. needtable::
   :filter: type == 'comp'
   :columns: id; title; bazel_target as "Bazel targets"; bazel_type as "Bazel target types"
   :sort: id
   :style: table
