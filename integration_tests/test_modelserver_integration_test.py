import requests
import pytest
import os
import json


@pytest.fixture
def rsession():
    return requests.session()


@pytest.fixture
def hostname():
    hostname = os.getenv("INPUT_HOSTNAME")
    if hostname is None:
        hostname = "http://localhost:9000/"
    # ensure the hostname is properly ended, since we construct the URLs by hand
    if not hostname.endswith("/"):
        hostname = hostname + "/"
    return hostname


@pytest.fixture
def headers():
    return {"accept": "application/json", "User-Agent": "iSamples Integration Bot 2000"}


def _post_opencontext_material(
    rsession: requests.Session,
    hostname: str,
    headers: dict
) -> list:
    url = f"{hostname}opencontext/"
    params: dict = {"source_record": {"foo": "bar"}, "type": "material"}
    data_params = json.dumps(params).encode("utf-8")
    res = rsession.post(url, headers=headers, data=data_params)
    response_dict = res.json()
    return response_dict


def test_opencontext_material(
    rsession: requests.Session,
    hostname: str,
    headers: dict,
):
    response = _post_opencontext_material(rsession, hostname, headers)
    assert response is not None
    assert type(response) is list
    assert type(response[0]["value"]) is str
    assert type(response[0]["confidence"]) is float