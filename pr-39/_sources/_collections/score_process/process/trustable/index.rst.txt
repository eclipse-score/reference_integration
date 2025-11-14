.. SPDX-License-Identifier: CC-BY-SA-4.0

..
   note::
   This document is based on work by Codethink available at
   https://gitlab.com/CodethinkLabs/trustable/trustable.
   This modified version is licensed under CC-BY-SA-4.0
   in compliance with the original license.

   Changes from original:
   - two paragraphs were combined to single paragraph
   - neutral wording instead of "we"
   - sphinx-needs meta data is added

.. _external_tsf:

Trustable
=========

.. note::
   The copyright check ignores all files in trustable and its subdirectories.
   Modified BUILD file in process repository to be reverted after reuse implementation
   is implemented in tooling.

*The* `Trustable Software Framework (TSF) <https://codethinklabs.gitlab.io/trustable/trustable/index.html>`_
*approach is designed for consideration of software where factors such as safety, security,
performance, availability and reliability are considered critical. Broadly it asserts that any
consideration of trust must be based on evidence.*

The tenets and assertions defined in the Trustable Software Framework can be used to measure an (OSS) project trust score.
To calculate the score link evidences to the Trustable Assertions (TA).


.. figure:: _assets/tsf_overview.drawio.svg
  :width: 100%
  :align: center
  :alt: TSF Overview

  TSF Overview

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   tenets/tenets
   assertions/assertions

.. tsf:: TRUSTABLE SOFTWARE
   :id: tsf__trust__trustable-software
   :status: valid
   :links: tenet__trust__tt-provenance, tenet__trust__tt-construction, tenet__trust__tt-changes, tenet__trust__tt-expectations, tenet__trust__tt-results, tenet__trust__tt-confidence

    This release of XYZ is Trustable.

    Trustability of the release is based on aggregation of the evidence from all
    of the Trustable Tenets and Trustable Assertions.
    The algorithm for aggregation may involve weighting of specific Tenets or
    Assertions based on project priorities or experience.


XYZ Trustable Overview
----------------------

Trustable Software Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. needtable::
   :style: table
   :columns: title;id;status;links
   :colwidths: 25,25,25,25
   :sort: title

   results = []

   for need in needs.filter_types(["tsf"]):
                results.append(need)

Trustable Tenets Overview
~~~~~~~~~~~~~~~~~~~~~~~~~

.. needtable::
   :style: table
   :columns: title;id;status;links
   :colwidths: 25,25,25,25
   :sort: title

   results = []

   for need in needs.filter_types(["tenet"]):
                results.append(need)

Trustable Assertions Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. needtable::
   :style: table
   :columns: title;id;status;links
   :colwidths: 25,25,25,25
   :sort: title

   results = []

   for need in needs.filter_types(["assertion"]):
                results.append(need)
