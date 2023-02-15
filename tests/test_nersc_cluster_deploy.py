from nersc_cluster_deploy import deploy_ray_cluster


def test_main():
    test_dict = {'flag': 'option'}
    test_jobid = deploy_ray_cluster(test_dict)

    assert isinstance(test_jobid, str)
