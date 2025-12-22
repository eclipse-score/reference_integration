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

.. _prm_templates:

Problem Report Template
=======================

.. gd_temp:: Problem Template
   :id: gd_temp__problem_template
   :status: draft
   :complies: std_req__aspice_40__SUP-9-BP1, std_req__aspice_40__SUP-9-BP2, std_req__aspice_40__SUP-9-BP3, std_req__aspice_40__SUP-9-BP4,

This template defines the content to be implemented in the selected Issue Tracking System
of the project.


Problem status
--------------
[“open”, “in review”, “in implementation”, “closed”, “rejected”]

| (to be filled out during :need:`wf__problem_create_pr`)
| (to be updated during :need:`wf__problem_analyze_pr`)
| (to be updated during :need:`wf__problem_initiate_monitor_pr`)
| (to be updated during :need:`wf__problem_close_pr`)

Problem submitter
-----------------
[Who is the reporter of the problem?]

(to be filled out during :need:`wf__problem_create_pr`)

Problem description
-------------------
[What is the problem?]

| Determine the cause of the problem, if possible.
| Determine the impact of the problem, if possible.
| Is notification required due to determined impact on affected parties?

| (to be filled out during :need:`wf__problem_create_pr`)
| (to be updated during :need:`wf__problem_analyze_pr`)

Problem supporting information
------------------------------
[How to reproduce the problem?]

| Add additional information, e.g.
| add which operational state the problem occurred?
| observations, screenshots, debug traces, etc.

[Error occurrence rate?]

| Select one [None | Single Event | Sporadic | Highly Intermittent | Reproducible]

| (to be filled out during :need:`wf__problem_create_pr`)
| (to be updated during :need:`wf__problem_analyze_pr`)

Problem category
----------------
[Safety affected, Security affected]

Safety, Security: Additional qualifiers to highlight, if safety or security is affected

They qualifiers have to be filled. If not filled out, a quality problem is assumed as
default category.

In addition to the category Safety affected, the ASIL classification may be added in the
documentation, if applicable.

| (to be filled out during :need:`wf__problem_create_pr`)
| (to be updated during :need:`wf__problem_analyze_pr`)

Problem classification
----------------------
[minor, major, critical, blocker]

Classify the problem severity

| Use **minor**, if the impact is not significant of the project

* The problem does not restrict usage of features in a significant manner

| Resolution may be scheduled to any planned future SW release

| Use **major**, if the impact does effect the quality of the project

* The problem can be solved with workarounds for affected features

| Resolution shall be scheduled to next planned future SW release

| Use **critical**, if the impact does not prohibit to use the project, but quality cannot be guaranteed

* The problem affects a complete feature, that they are partly or complete not behave as expected

| Resolution shall be scheduled to next planned future SW release or to a new planned intermediate release, if urgent resolution is required

| Use **blocker**, if the impact prohibits using the project

* The problem affects more than one feature, that they are partly or complete not behave as expected OR
* Safety or Security risks identified

| Resolution shall be provided upon availability

.. note::
  In case of doubt, a safety or security relevant problem shall always classified as **blocker**.

Determine if Urgent resolution is required? (yes, no, only valid for critical, blocker)

| (to be filled out during :need:`wf__problem_create_pr`)
| (to be updated during :need:`wf__problem_analyze_pr`)

Problem affected version
------------------------
[What version of the release is affected?]

Document the version of the release where the problem was detected.

| (to be filled out during :need:`wf__problem_create_pr`)

Problem analysis results
------------------------
[What is the problem analysis result? Accepted or Rejected?]

| Especially document rejection reason, if applicable

In addition the safety/security relevance is confirmed or disconfirmed by safety/Security
Experts.

| Especially document disconfirming reason, if applicable

(to be filled out during :need:`wf__problem_analyze_pr`)

Problem stakeholder
-------------------
[What are the potential stakeholder to resolve the problem?]

Add affected features, if applicable

(to be filled out during :need:`wf__problem_analyze_pr`)

Problem expected closure version
--------------------------------
[Version when the problem should be resolved]

Document the version of the release where the problem should be resolved.

Optionally add a concrete Milestone, if applicable.

(to be filled out during :need:`wf__problem_analyze_pr`)

Problem solutions
-----------------
[What are measures to solve the problem?]

Specify the measures to resolve the problem, based on a rationale

Verify the effectiveness of the implemented measure

Report the results of the verification, if applicable

Are all arguments convincing

| (to be filled out during :need:`wf__problem_initiate_monitor_pr`)
| (to be updated during :need:`wf__problem_close_pr`)

Problem escalations
-------------------
[Document escalation activities, if applicable]

| (to be filled out during :need:`wf__problem_initiate_monitor_pr`)
| (to be updated during :need:`wf__problem_close_pr`)
