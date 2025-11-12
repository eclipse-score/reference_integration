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
   `Example Tool Verification Report <https://eclipse-score.github.io/score/main/score_tools/doc_as_code.html#doc_tool__doc_as_code>`_


[Your Tool Name] Verification Report
------------------------------------


Introduction
------------

Scope and purpose
~~~~~~~~~~~~~~~~~
[Describe the scope and purpose of the tool]

May add general use cases, scenarios, etc.

Inputs and outputs
~~~~~~~~~~~~~~~~~~
[Describe here the inputs and outputs of the tool]

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

May add where is the tool located?

May add how the tool is configured in order to be used in safe/secure way?

May add access/usage protection required?, execution authority required?

Integration
~~~~~~~~~~~
[Describe here how to integrate the tool in existing toolchain]

May add how the tool works together with other tools?

Environment
~~~~~~~~~~~
[Describe environment and its constraints/limitations]


Evaluation
----------
[Describe here detailed information about the tool evaluation]

Determine the use case for the tool in the project and for each use case

Determine the malfunctions/threats

Determine the tool impact based on the malfunctions/threats

Determine the available safety/security measures

Determine if the impact detection based on safety/security measures are sufficient and
add additional ones, if required

Determine the tool confidence based on tool impact and tool impact detection

Use the table below to document all uses cases and their evaluation. The table has an
example included.

The final Confidence shall be judged on the maximum confidence level of each use case.


.. list-table:: [Your tool name] evaluation
   :header-rows: 1

   * - Use case Identification
     - Use case Description
     - Malfunctions
     - Impact on safety?
     - Impact safety measures available?
     - Impact safety detection sufficient?
     - Threats
     - Impact on security?
     - Impact security measures available?
     - Impact security detection sufficient?
     - Further additional safety measure required?
     - Confidence (automatic calculation)
   * - 1
     - Generate element (requirements, architecture, safety analysis, ...)
     - Wrong or missed element may lead to an wrong implementation with any potential error
     - yes
     - Reviews
     - no
     - Gain access to modify or run manipulated Doc-as-code or to to modify input files
     - yes
     - Access control, roles in Github
     - yes
     - Compare generated text in documentation with original text (#PR)
     - low


Result
~~~~~~
Add here final statement, if tool qualification is required or not.


**Optional Section for Tool Qualification**
-------------------------------------------
Based on method: validation of the software tool


Requirements and testing aspects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Describe here requirements and their tests from user point of view]

Where are tool requirements defined?

Where are the test cases for the requirements defined?

Where are the requirements coverage documented?


Analysis perspective
~~~~~~~~~~~~~~~~~~~~
[Describe analysis perspective]

Optional:

Where is the architectural design of the tool defined?

Where is the safety analysis for the tool defined?

Where is the security analysis for the tool defined?
