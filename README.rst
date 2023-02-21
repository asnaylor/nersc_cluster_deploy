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

You can install the in-development version with::

    pip install git+https://github.com/asnaylor/nersc_cluster_deploy.git


Documentation
=============


To use the project:

.. code-block:: python

    from SuperfacilityAPI import SuperfacilityAPI, SuperfacilityAccessToken
    from nersc_cluster_deploy import deploy_ray_cluster, get_ray_cluster_address
    import ray

    api_key = SuperfacilityAccessToken(
        client_id = client_id,
        private_key = private_key
    )
    sfapi = SuperfacilityAPI(api_key)

    slurm_options = {
        'qos': 'debug',
        'account':'<account>',
        'image': 'nersc/pytorch:ngc-22.09-v0',
        'nodes': '2',
        't': '00:30:00'
    }
    site = 'perlmutter'

    job = deploy_ray_cluster(
        sfp_api,
        slurm_options,
        site
    )

    #Also supported is
    slurm_options = '-q debug -a <account> --time=00:20:00 -N 3'
    site = 'cori'

    job = deploy_ray_cluster(
        sfp_api,
        slurm_options,
        site,
        use_gpu = False,
        job_setup = ['module load python', 'conda activate ray_test_env']
        post_job = 'echo Completed job at: $(date)'
    )

    #Get ray cluster address to connect
    cluster_address = get_ray_cluster_address(
        sfp_api,
        job['jobid'],
        site
    )
    ray.init(cluster_address)


Tutorials
=============

For more information and examples see the `tutorial <tutorial/README.md>`_ folder.

Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
