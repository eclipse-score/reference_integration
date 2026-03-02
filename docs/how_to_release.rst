=================================
How to create a release of S-CORE
=================================

Definitions
-----------

==========================  ==================================
Role                        Description
==========================  ==================================
Reference Integration Team  Prepare integration process
Module Codeowners           Prepare Module's release candidate
Project Manager             Approves S-CORE release
==========================  ==================================

Process overview
----------------
Release interval between S-CORE Product Increments can be divided into two phases:

* development (4 weeks) 
* integration (2 weeks) 

At the beginning, the overall scope and general requirements for the Modules are discussed and agreed upon within the S-CORE community,
providing clear goals for what must be achieved.

During the development phase, work on new features and improvements to the Modules takes place. At the end of this period, each Module
must provide a hash of the commit that represents a *code freeze* and serves as a candidate for integration. The hash can be from the **main** or **dedicated release** branch.

The integration phase begins with the creation of a **release branch** in the ``reference_integration`` repository.
Module Codeowners prepare a Pull Request to that branch with updates to the ``known_good.json`` file, pointing to the hash of their *code freeze*.
They may update other JSON fields for their Module as needed. Automated workflows will build and test to provide clear feedback directly in the PR.
If there are any issues, Module Codeowners can either push fixes to their **dedicated release** branch and update the hash in the PR accordingly,
or provide patches (see :ref:`ref_int_patching-label`). 

Once all Modules are merged with their *code freeze*, Module Codeowners create a tag on that exact hash following the S-CORE release process,
provide release notes to the ``score_platform`` team, and ensure that the new release is present in S-CORE's ``bazel_registry``.
The Reference Integration Team prepares a final Pull Request and replaces all hashes with the dedicated release versions.
The Project Manager approves the PR, and the Reference Integration Team creates the new S-CORE release.

An automated verification process of the release begins, and once successful, the release and its downloadable assets are ready for distribution.

Fallbacks
---------

Module Codeowners may decide that their Module will not be released with a new major version for the S-CORE Product Increment.
However, they must ensure that the Module remains compatible with the S-CORE release and does not fail any workflows.

If any S-CORE community member discovers a showstopper for the upcoming release, they must communicate it promptly to the Project Manager and other community members.
Following discussion and impact analysis, a decision is made regarding whether to postpone or skip the S-CORE release, and the planning is updated accordingly.


.. _ref_int_patching-label:

Patching Module
---------------

Module Codeowners prepare ``.patch`` file(s) and place them in the ``/patches/MODULE_NAME`` directory.
The patch filename must clearly indicate what it addresses.
For multiple issues, it is preferred to create multiple patches rather than a single patch addressing all issues.
An empty Bazel ``BUILD`` file must be placed alongside the patches.
