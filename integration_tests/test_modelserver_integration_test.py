from typing import Any

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


class ModelServerClient:
    base_url: str
    base_headers: dict

    def __init__(self, base_url: str, base_headers: dict = {}):
        self.base_url = base_url
        self.base_headers = base_headers

    def _make_json_request(self, url: str, rsession: requests.Session, data_params: dict) -> Any:
        data_params_bytes: bytes = json.dumps(data_params).encode("utf-8")
        res = rsession.post(url, headers=self.base_headers, data=data_params_bytes)
        response_dict = res.json()
        return response_dict

    def make_opencontext_material_request(self, source_record: dict, rsession: requests.Session = requests.Session()) -> Any:
        url = f"{self.base_url}opencontext/"
        params: dict = {"source_record": source_record, "type": "material"}
        return self._make_json_request(url, rsession, params)

def _post_opencontext_material(
    rsession: requests.Session,
    hostname: str,
    headers: dict
) -> list:
    client = ModelServerClient(hostname, headers)
    return client.make_opencontext_material_request({"foo": "bar"}, rsession)


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