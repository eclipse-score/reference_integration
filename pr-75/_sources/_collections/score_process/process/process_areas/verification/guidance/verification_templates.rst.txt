..
   # *******************************************************************************
   # Copyright (c) 2024 Contributors to the Eclipse Foundation
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

.. _verification_test_templates:

Verification Templates
======================

The sections below are seen as typical ways when writing tests and their specification.
Their usage differs based on the selected testing framework and the implementation language of the module(s).

C++
---

For C++ code gTest is a commonly used and accepted test framework to write test cases for C/C++ code.

Each test case requires a link to one or more requirement/design element.

For linking C++ tests to requirements **record properties** shall be used. Attributes
which are common for all test cases can be specified in the Setup Function (SetUp()), the other
attributes which are specific for each test case need to be specified within the test case:

Below code is exemplary and can be used as a template when writing test cases.

.. _verification_template_cpp:

C++ Properties Template
^^^^^^^^^^^^^^^^^^^^^^^

   .. code-block:: cpp

      class TestSuite : public ::testing::Test{
         public:
            void SetUp() override
            {
               RecordProperty("TestType", "<TestType>");
               RecordProperty("DerivationTechnique", "<DerivationTechnique>");
               ...
            }
      };

      TEST_F(TestSuite, <Test Case>)
      {
         RecordProperty("PartiallyVerifies", "ID_2, ID_3, ...");
         RecordProperty("FullyVerifies", "ID_4, ID_5, ...");
         RecordProperty("Description", "<Description>");

         ASSERT ...
      }

When writing test cases using gTest, they shall follow the recommendations from the official gTest documentation.
For very basic start follow http://google.github.io/googletest/primer.html
For advanced information follow http://google.github.io/googletest/advanced.html

Rust
----

The rust community uses the terms unit test and integration test. Where unit test basically represents what the project
considers as unit tests the term "integration test" in rust can be treated for component and feature testing.
Details on the definition an the test organization in rust can be found here:
https://doc.rust-lang.org/book/ch11-03-test-organization.html

Each test case requires a link to one or more requirement/design element.

Below code is exemplary and can be used as a template when writing test cases.

.. _verification_template_rust:

Rust Properties Template
^^^^^^^^^^^^^^^^^^^^^^^^

   For linking Rust tests to requirements **#[record_property]** shall be used:

   .. code-block:: rust

      use test_properties::record_property;

      #[record_property("PartiallyVerifies", "ID_2, ID_3, ...")]
      #[record_property("FullyVerifies", "ID_4, ID_5, ...")]
      #[record_property("Description", "<Description>")]
      #[record_property("TestType", "<TestType>")]
      #[record_property("DerivationTechnique", "<DerivationTechnique>")]
      #[test]
      fn test_case_function() {
         ...
      }

When writing test cases in rust, they shall follow the recommendations from the official rust documentation.
https://doc.rust-lang.org/book/ch11-01-writing-tests.html


Python
------

When writing test cases in python, this should be done using pytest.
Note that python unittest does not support metatags and therefore should not be considered as test framework.

Each test case requires a link to one or more requirement/design element.

For linking python tests to requirements **metadata** shall be used.

For allowed values for test_type & derivation_technique please check :need:`gd_req__verification_link_tests`

Below code is exemplary and can be used as a template when writing test cases.

.. _verification_template_python:

Python Properties Template
^^^^^^^^^^^^^^^^^^^^^^^^^^

   .. code-block:: python

      @add_test_properties(
            partially_verifies=["tool_req__docs_dd_link_source_code_link"],
            test_type="requirements-based",
            derivation_technique="requirements-analysis",
      )
      def test_group_by_need_empty_list():
            """Test grouping empty list of needlinks."""
            ...

When writing test cases in python, they shall follow the recommendations from the official python and community documentation.
https://docs.python-guide.org/writing/tests/
