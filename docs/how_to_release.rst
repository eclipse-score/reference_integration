=================================
How to create a release of S-CORE
=================================

Definitions
-----------

==========================  ====================================================
Role                        Description
==========================  ====================================================
Reference Integration Team  Prepare integration process
Module Maintainers          Prepare Module's release candidate
Project Lead                Guides the release process and leads decision making
==========================  ====================================================

Process overview
----------------

Release interval between S-CORE Product Increments can be divided into two phases:

**Development phase (6 weeks) :**

#. Common release requirements definition
#. Features' implementations and improvements
#. Tooling release
#. Code freeze

**Integration phase (2 weeks) :**

#. Release branch creation
#. Integration of the Modules
#. Release candidate
#. Release creation

Common release requirements definition
--------------------------------------

At the beginning, the overall scope and general requirements for the Modules are discussed and 
agreed upon within the S-CORE community, providing clear goals for what must be achieved.
The scope should define requirements such as:

* Tooling versions
* Used toolchains
* Supported platforms

rather than specific features' implementation scopes.
Based on the operating system definitions documented in the `Operating Systems<_collections/score_platform/docs/modules/os/operating_systems/docs/index.html>`_ 
the Reference Integration Team will only maintain functional/certifiable level OSs as part of the release, 
while community OSs will be prepared and maintained by the OS module Maintainers. *Code freeze* applies to OSs as well.

.. note:: 

    Performed by: Project Lead and S-CORE community

Features' implemntations and improvements
-----------------------------------------

During the development phase, the community works on new features and improvements to the Modules. 
Changes are reviewed by Commiters and Module Maintainers.

.. note:: 

    Performed by: S-CORE community and Module Maintainers

Tooling release
---------------

S-CORE tools, toolchains and other dependencies which are listed in the following Bazel MODULE files:

* ``bazel_common/score_gcc_toolchains.MODULE.bazel``
* ``bazel_common/score_modules_tooling.MODULE.baze``
* ``bazel_common/score_qnx_toolchains.MODULE.bazel``
* ``bazel_common/score_rust_toolchains.MODULE.baze``

are released at the end of the development phase the latest.
During the integration phase, no changes other than necessary bug fixes are allowed to give time to the Modules to rebase 
their dependencies and prepare their *code freeze*.

.. note:: 

    Performed by: Module Maintainers

Code freeze
-----------
At the end of development phase, each Module must provide a hash of the commit that represents a *code freeze*
and serves as a candidate for integration. The hash can be from the **main** or **dedicated release** branch.
 
.. note:: 

    Performed by: Module Maintainers

Release branch creation
-----------------------

The integration phase begins with the creation of a **release branch** in the ``reference_integration`` repository 
originating from current **main**.

.. note:: 

    Performed by: Reference Integration Team

Integration of the Modules
--------------------------

Module Maintainers prepare a Pull Request to that branch with updates to the ``known_good.json`` file, 
pointing to the hash of their *code freeze*. They may update other JSON fields for their Module as needed. 
Automated workflows will build and test to provide clear feedback directly in the PR.
If there are any issues, Module Maintainers can either push fixes to their **dedicated release** branch 
and update the hash in the PR accordingly, or provide patches (see :ref:`ref_int_patching-label`).

.. note:: 

    Performed by: Module Maintainers

Release candidate
-----------------

Once all Modules are merged with their *code freeze*, Module Maintainers create a tag on that exact hash following the S-CORE release process,
provide release notes to the ``score_platform`` repository, and ensure that the new release is present in S-CORE's ``bazel_registry``.
The Reference Integration Team prepares a final Pull Request and replaces all hashes with the dedicated release versions.

This pull request has additional workflow checking that every Maintainer has approved the PR signing off their Module's release candidate. 
There is an additional ``.rst`` file listing every Module and GitHub ID of the Maintainer responsible. 

.. note:: 

    Performed by: Reference Integration Team and Module Maintainers

Release creation
----------------

Once all previous steps are completed Reference Integration Team triggers the release creation workflow in ``release_integration``. 
An automated verification process of the release begins which includes building, testing, deploying documentation and checking that 
every Module has been correctly signed-off by its Maintainer. If any issue is found, the release creation process is stopped.
When successfully completed the release and its downloadable assets are ready for distribution.

.. note:: 

    Performed by: Reference Integration Team 


Opting out of a release
-----------------------

Module Maintainers may decide that their Module will not be released with a new version for the S-CORE Product Increment.
In that case currently integrated version can be used. However, they must still ensure that the Module remains compatible with 
the S-CORE release and does not fail any workflows.

If Module Maintainers cannot adapt to the newest release requirements or any S-CORE community member discovers a showstopper 
for the upcoming release, they must communicate it promptly to the Project Lead and other community members.
Following discussion and impact analysis, a decision is made regarding whether to postpone or skip the S-CORE release,
and the planning is updated accordingly.


Removing Module from Reference Integration
------------------------------------------

Currently following modules can be removed without an impact on the S-CORE release:

* ``score_feo``
* ``score_orchestrator``

Once excluded from the release and integration issue persists also on a ``reference_integration`` **main** branch, 
Reference Integration Team will remove the Module completely.
It is up to Module Maintainers to fix and integrate the Module back into the main branch and later releases.


.. _ref_int_patching-label:

Patching Module
---------------

Module Maintainers prepare ``.patch`` file(s) and place them in the ``/patches/MODULE_NAME`` directory.
The patch filename must clearly indicate what it addresses.
For multiple issues, it is preferred to create multiple patches rather than a single patch addressing all issues.

Target releases definition
--------------------------

Based on the operating system definitions documented in the `OS module <https://eclipse-score.github.io/score/main/modules/os/operating_systems/docs/index.html>`_, 
the Reference Integration Team defines which OSs will be maintained as part of the release:

* **Functional/Certifiable level OSs** - maintained by the Reference Integration Team and included in the release
* **Community OSs** - prepared and maintained by the OS module Maintainers during the integration phase

Only changes to functional/certifiable level OSs are considered until the *code freeze*. 
Community OS updates can be prepared by the OS Maintainer during the release phase if needed.

.. note::

    Performed by: Reference Integration Team and OS module Maintainers
