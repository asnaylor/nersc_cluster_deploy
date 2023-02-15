========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |github-actions|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |github-actions| image:: https://github.com/asnaylor/nersc_cluster_deploy/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/asnaylor/nersc_cluster_deploy/actions

.. |version| image:: https://img.shields.io/pypi/v/nersc-cluster-deploy.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/nersc-cluster-deploy

.. |wheel| image:: https://img.shields.io/pypi/wheel/nersc-cluster-deploy.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/nersc-cluster-deploy

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/nersc-cluster-deploy.svg
    :alt: Supported versions
    :target: https://pypi.org/project/nersc-cluster-deploy

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/nersc-cluster-deploy.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/nersc-cluster-deploy

.. |commits-since| image:: https://img.shields.io/github/commits-since/asnaylor/nersc_cluster_deploy/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/asnaylor/nersc_cluster_deploy/compare/v0.1.0...main



.. end-badges

Deploy workflow clusters on NERSC supercomputers.

* Free software: GNU Lesser General Public License v3 (LGPLv3)

Installation
============

::

    pip install nersc-cluster-deploy

You can also install the in-development version with::

    pip install https://github.com/asnaylor/nersc_cluster_deploy/archive/main.zip


Documentation
=============


To use the project:

.. code-block:: python

    import nersc_cluster_deploy
    nersc_cluster_deploy.longest()


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
