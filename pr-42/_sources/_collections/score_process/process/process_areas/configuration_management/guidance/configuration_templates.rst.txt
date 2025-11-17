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

.. _configuration_templates:

Template Configuration Management Plan
======================================

.. gd_temp:: Configuration Management Plan Template
   :id: gd_temp__config_mgt_plan
   :status: valid
   :complies: std_req__iso26262__support_741, std_req__iso26262__support_742, std_req__iso26262__support_743, std_req__iso26262__support_744, std_req__iso26262__support_745, std_req__aspice_40__SUP-8-BP1, std_req__aspice_40__SUP-8-BP2, std_req__aspice_40__SUP-8-BP3, std_req__aspice_40__SUP-8-BP4, std_req__aspice_40__SUP-8-BP5, std_req__aspice_40__SUP-8-BP8, std_req__aspice_40__iic-13-08

Purpose
+++++++

The Configuration Management Plan defines how the integrity of all work products
and other project relevant artefacts can be reached and maintained.


Objectives and scope
++++++++++++++++++++

Goal of this plan is to describe

* how all configuration items in the project are identified
* the infrastructure to store the configuration items
* how to make all configuration items available to all concerned parties
* where to find which configuration item
* how to retrieve specific versions of a configuration item
* how to modify a configuration item and how to control this
* how to create and store versions of configuration items
* how to manage baselines
* how to backup and recover (including long term storage)
* how to report the configuration status

note: for definition of "configuration items" check :need:`doc_concept__configuration_process`


Approach
++++++++

The steps below describe how configuration identification, retrieval, modification, branches and baselines, backup and recovery are organized.

Lifecycle
^^^^^^^^^

The configuration management of the <project name> project is in place during the complete development lifecycle as described in :ref:`general_concepts_lifecycle`.
I.e. in Concept Phase, Development Phase and Maintenance.

Identification and Properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This should cover :need:`std_req__aspice_40__SUP-8-BP1` and :need:`std_req__aspice_40__SUP-8-BP2`.

Each work product is identified by its "Docs-as-Code" Id, this includes documents identified as such (by the document header as defined in :need:`gd_temp__documentation`).
The complete list of project documents is defined in the project's <link to doc__documentation_mgt_plan>.
Ids are checked for uniqueness, see :need:`gd_req__configuration_uid`.
"Docs-as-Code" is also used to document the work products properties/attributes defined in the process area descriptions.
The work products are stored in text or code files (these are identified by their filenames) within the selected version management tool.

For additional artefacts these are either

- files - are identified by their path/filename
- precompiled tools/binaries - CI build configuration identifies those by their hash.
- (external) tools/binaries to be built in <project name> CI - CI build configuration identifies those by their version.


Retrieval
^^^^^^^^^

<Describe how work products and files can be retrieved from versioning tooling.>
Their content is defined in the process/workproducts and process_area/<area_name>/workproducts files.
To find the location of the work products, the folder structure definition :ref:`folder_templates` can be used.
<Describe how certain versions (also the ones for a certain baseline) of the work products and the change history can be displayed by the version management tool.>

For other artefacts: these are pulled into <project name> integration repository by forking to be handled as above.


Control and Modification
^^^^^^^^^^^^^^^^^^^^^^^^

This should cover :need:`std_req__aspice_40__SUP-8-BP3` and :need:`std_req__aspice_40__SUP-8-BP4`

Files or new work products contained in these files are created in local branches by the :need:`Contributor <rl__contributor>`
and shared for review and incorporation into a main branch, which are after their acceptance merged by the :need:`Committer <rl__committer>`
(this should be supported by version management tool).
The same applies for changes in existing configuration items.
All modifications (differences between before and after) are documented in the pull-requests and are the main input to the pull-request reviews.
See also <link doc__platform_change_management_plan>.

For tool/binaries modifications (version changes) are controlled by the CI build files.
These build files, like other files, are also maintained in version management tool.


Branches and Baselines
^^^^^^^^^^^^^^^^^^^^^^

This should cover :need:`std_req__aspice_40__SUP-8-BP5` and :need:`std_req__aspice_40__iic-13-08`

Branches are used as a means of parallel development. In the <project name> project the following types of branches will be used:

* local branches - created from "remote" branches, in these the development of the contributors takes place, no restriction on naming.
* main branch - a "remote" branch (named "main") which contains all the latest file versions checked by CI, reviewed, accepted and merged.
* release branch - a "remote" branch derived from main branch which is used to prepare a release,
  no functional code changes are allowed, only bug fixes and verification based improvements.
  Only the technical lead is allowed to approve a merge into a release branch. The branch name is given as defined in :need:`doc_concept__rel_process`.

The "remote" branch is not "local" to the developer but resides on the "remote" version management server.

In <project name> project all configuration items are kept in the version management tool, this means that there only needs to be one baseline for these
(and not multiple ones for each of the work products which are maintained in seperate tools).
<Describe how baselines are created by using the version management tool.>
See also <link to doc__platform_release_management_plan>.

Every change in the release repository is also taken over into the main branch. The module development team
can decide how to ensure this (e.g. by development in main and cherrypick to release branch).


Backup and Recovery
^^^^^^^^^^^^^^^^^^^

This should cover :need:`std_req__aspice_40__SUP-8-BP8`

<Describe how backup and recovery are covered in the project.>
For the long term storage, additional measures should be taken, see :need:`gd_req__config_workproducts_storage`

Status and Reporting
^^^^^^^^^^^^^^^^^^^^

This should cover :need:`std_req__aspice_40__SUP-8-BP6` and :need:`std_req__aspice_40__SUP-8-BP7`

Every work product defined in our proceses has a "status" attribute. These are used to communicate to all the stakeholders.
The main communication means is a document list containing all documents and workproducts including their status.
This list is typically part of the Documentation Management Plan <link doc__documentation_mgt_plan> as part of the Platform Management Plan,
as defined in :need:`gd_guidl__documentation`.
Completeness of the configuration items (within a baseline) is checked at least for every release
against the list of planned documents and workproducts, which is also part of the Documentation Management Plan.

Configuration Management Tooling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Almost all requirements of the standards towards configuration management can be covered by
standard versioning tooling of the Eclipse Foundation and of the <project name> project
("Docs-as-Code" identification of work products).
The respective tools used in the project are:

* versioning tool: <tool name>
* "Docs-as-Code" tool: <tool name>
* CI build tool: <tool name>

Note 1: A versioning tool covers part of configuration management but not all (namely: storage, retrieval, control and modification, branching and baselining).

Note 2: A "Docs-as-Code" tool is used to identify, attribute and link parts of text files and generate human and machine readable documentation.
