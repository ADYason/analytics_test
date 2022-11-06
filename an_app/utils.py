from an_app import elastic_client


def test_es():
    ec = elastic_client
    return ec.ping()