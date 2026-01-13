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

Tool Verification Report Template
=================================

.. note:: Tool Verification Report header

.. doc_tool:: [Your Tool Name]
   :id: doc_tool__tool_name_version
   :status: draft
   :version: vX.Y.Z
   :tcl: LOW
   :safety_affected: YES
   :security_affected: YES
   :realizes: wp__tool_verification_report
   :tags: template, tool_management

.. attention::
   The above directive must be updated according to your tool.

   The information is used for proper tool identification

   Status may (draft, evaluated, qualified, released, rejected)

   Safety/Security affected may (YES, NO)

   TCL may (LOW, HIGH)

   Version may v.MAJOR.MINOR.PATCH

.. note::
   An example of a Tool Verification Report can be found here:
   `Example Tool Verification Report <https://eclipse-score.github.io/score/main/score_tools/gtest.html#doc_tool__gtest>`_


[Your Tool Name] Verification Report
------------------------------------


Introduction
------------

Scope and purpose
~~~~~~~~~~~~~~~~~
[Describe the scope and purpose of the tool]

.. tip::
   May add general use cases, scenarios, etc.


Inputs and outputs
~~~~~~~~~~~~~~~~~~
[Describe here the inputs and outputs of the tool]

.. tip::
   May add a figure, if appropriate

.. note::
   | .. figure:: _assets/[Your Tool Name].drawio.svg
   |   :width: 100%
   |   :align: center
   |   :alt: [Your Tool Name] overview

   | [Your Tool Name] overview


Available information
~~~~~~~~~~~~~~~~~~~~~
[Describe here the available information for the tool]

.. tip::
   May also add some general information about the tool

   May add links to the public available information, if applicable,
   e.g. tools documentation, tracking of tool bugs, user manual, guidelines, etc.

   May add some comments to get started or usage information or integration manual

   May add tool usage constraints/limitations


Installation and integration
----------------------------

Installation
~~~~~~~~~~~~
[Describe here how to install the tool]

.. tip::
   May add where is the tool located

   May add how the tool is configured in order to be used in safe/secure way

   May add access/usage protection required, execution authority required

Integration
~~~~~~~~~~~
[Describe here how to integrate the tool in existing toolchain]

.. tip::
   May add how the tool works together with other tools

Environment
~~~~~~~~~~~
[Describe environment and its constraints/limitations]


Safety evaluation
-----------------
[Describe here detailed information about the tool safety evaluation]

.. tip::
   Determine the use case for the tool in the project and for each use case

   Determine the malfunctions

   Determine the tool impact based on the malfunctions

   Determine the available safety measures

   Determine if the impact detection based on safety measures are sufficient and
   add additional ones, if required

   Determine the tool confidence based on tool impact and tool impact detection

   Use the table below to document all uses cases and their evaluation, the example table provided below

   The final confidence shall be judged on the maximum confidence level of each use case


.. list-table:: [Your tool name] evaluation
   :header-rows: 1
   :widths: 1 2 8 2 6 4 2 2

   * - Malfunction identification
     - Use case description
     - Malfunctions
     - Impact on safety?
     - Impact safety measures available?
     - Impact safety detection sufficient?
     - Further additional safety measure required?
     - Confidence (automatic calculation)
   * - 1
     - Use case description example
     - | Malfunction X (with safety impact and available measures)
       |
       | Detailed description of malfunction X shall be added here, if applicable.
     - yes
     - Reviews
     - yes
     - no
     - high
   * - 2
     - Use case description example
     - | Malfunction Y (with safety impact and no available measures)
       |
       | Detailed description of malfunction Y shall be added here, if applicable.
     - yes
     - no
     - no
     - yes (qualification)
     - low
   * - 3
     - Use case description example
     - | Malfunction Z (without safety impact)
       |
       | Detailed description of malfunction Z shall be added here, if applicable.
     - no
     - no
     - yes
     - no
     - high


Security evaluation
-------------------
[Describe here detailed information about the tool security evaluation]

.. tip::
   Determine the use case for the tool in the project and for each use case

   Determine the threats

   Determine the tool impact based on the threats

   Determine the available security measures

   Determine if the impact detection based on security measures are sufficient and
   add additional ones, if required

   Use the table below to document all uses cases and their security evaluation, the example table provided below

   The final confidence shall be judged on the maximum confidence level of each use case

.. list-table:: [Your tool name] security evaluation
   :header-rows: 1
   :widths: 1 2 8 2 6 4 2

   * - Threat identification
     - Use case description
     - Threats
     - Impact on security?
     - Impact security measures available?
     - Impact security detection sufficient?
     - Further additional security measure required?
   * - 1
     - Use case description example
     - | Threat A (with security impact and available measures)
       |
       | Detailed description of threat A shall be added here, if applicable.
     - yes
     - (Example) Usage of SSH/GPG keys to access to the source code repository
     - yes
     - no
   * - 2
     - Use case description example
     - | Threat B (with security impact and no available measures)
       |
       | Detailed description of threat B shall be added here, if applicable.
     - yes
     - no
     - no
     - yes (qualification)
   * - 3
     - Use case description example
     - | Threat C (without security impact)
       |
       | Detailed description of threat C shall be added here, if applicable.
     - no
     - no
     - yes
     - no


Result
~~~~~~
.. tip::
   Add here final statement, if tool qualification is required or not.

[Your tool name] requires qualification for use in safety-related software development according to ISO 26262.

or

[Your tool name] does not require qualification for use in safety-related software development according to ISO 26262.

**Optional Section for Tool Qualification**
-------------------------------------------
Based on method: validation of the software tool


Requirements and testing aspects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Describe here requirements and their tests from user point of view]

.. tip::
   Where are tool requirements defined

   Where are the test cases for the requirements defined

   Where are the requirements coverage documented


Analysis perspective
~~~~~~~~~~~~~~~~~~~~
[Describe analysis perspective]

.. tip::
   Optional:

   Where is the architectural design of the tool defined

   Where is the safety analysis for the tool defined

   Where is the security analysis for the tool defined
