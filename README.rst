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

    from nersc_cluster_deploy import deploy_ray_cluster
    
    #
    #Start Ray Cluster (via Shared Jupyter Node)
    ####################
    slurm_options = {
        'qos': 'debug',
        'account':'<account>',
        'nodes': '2',
        't': '00:30:00'
    } #Also supported
    # slurm_options = '-q debug -a <account> --time=00:30:00 -N 2'

    module_load = 'tensorflow/2.9.0'
    rayCluster = deploy_ray_cluster(
        slurm_options = slurm_options,
        job_setup = f'module load {module_load}'
    )
    #Also supported
    # job_setup =['module load python', 'conda activate custom_env']
    

    #
    #Start Ray Cluster (via in slurm job)
    ####################
    rayCluster = deploy_ray_cluster(
        job_setup = ['module load pytorch/1.13.1'] 
    )


    #
    #Get ray cluster dashboard
    ####################
    print(rayCluster.ray_dashboard_url)
    

    #
    #Connect to ray cluster
    ####################
    ray.init(address='auto')


Tutorials
=============

For more information and examples see the `tutorial <https://github.com/asnaylor/nersc_ray_notebook>`_ repo.

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
