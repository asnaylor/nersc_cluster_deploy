========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |github-actions|

.. |github-actions| image:: https://github.com/asnaylor/nersc_cluster_deploy/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/asnaylor/nersc_cluster_deploy/actions

.. end-badges

Deploy Ray clusters on NERSC supercomputers.

* Free software: GNU Lesser General Public License v3 (LGPLv3)


Deploy Ray Easily
============

.. code-block:: python

    from nersc_cluster_deploy import deploy_ray_cluster

    #Create Ray Cluster with dashboard
    rayCluster = deploy_ray_cluster(
        slurm_options = '-q regular -A elvis -t 01:00:00 -N 3'
        job_setup = 'module load pytorch',
    )
    >>> Ray cluster running at x.x.x.x:6379 
    >>> Dashboard avaliable at https://jupyter.nersc.gov/user/elivs/proxy/localhost:8265/ with metrics

    #Connect to cluster
    import ray
    ray.init(address='auto')

Installation
============

You can install the latest version with::

    pip install git+https://github.com/asnaylor/nersc_cluster_deploy.git@v0.4.0


Documentation
=============

Visit the documentation `README </docs/README.md>`_ for more information.


Tutorials
=============

For examples see the `tutorial <https://github.com/asnaylor/nersc_ray_notebook>`_ repo.
