import json
from typing import List

import pytest
from starlette.testclient import TestClient

from isamples_metadata.taxonomy.metadata_models import SampleTypePredictor, PredictionResult, MaterialTypePredictor
from main import app, get_opencontext_sample_type_predictor, get_opencontext_material_type_predictor, \
    get_sesar_material_type_predictor


@pytest.fixture(name="sample_type_predictor")
def sample_type_fixture():
    class MockSampleTypePredictor(SampleTypePredictor):
        def predict_sample_type(self, source_record: dict) -> List[PredictionResult]:
            return [PredictionResult(value="sample", confidence=0.5)]
    return MockSampleTypePredictor()


@pytest.fixture(name="material_type_predictor")
def material_type_fixture():
    class MockMaterialTypePredictor(MaterialTypePredictor):
        def predict_material_type(self, source_record: dict) -> List[PredictionResult]:
            return [PredictionResult(value="material", confidence=0.5)]
    return MockMaterialTypePredictor()


@pytest.fixture(name="client")
def client_fixture(sample_type_predictor: SampleTypePredictor, material_type_predictor: MaterialTypePredictor):
    def get_sample_type_predictor_override():
        return sample_type_predictor

    def get_material_type_predictor_override():
        return material_type_predictor

    app.dependency_overrides[get_opencontext_sample_type_predictor] = get_sample_type_predictor_override
    app.dependency_overrides[get_opencontext_material_type_predictor] = get_material_type_predictor_override
    app.dependency_overrides[get_sesar_material_type_predictor] = get_material_type_predictor_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _post_to_modelserver(client, data_dict, expected_value, handler):
    post_data = json.dumps(data_dict).encode("utf-8")
    response = client.post(handler, data=post_data)
    assert response.status_code == 200
    response_data = response.json()
    assert 1 == len(response_data)
    prediction_result = response_data[0]
    assert expected_value == prediction_result["value"]
    assert 0.5 == prediction_result["confidence"]


def test_getopencontext_material_type(client: TestClient):
    data_dict = {
        "source_record": {"foo": "bar"},
        "type": "material"
    }
    _post_to_modelserver(client, data_dict, "material", "/opencontext")


def test_getopencontext_sample_type(client: TestClient):
    data_dict = {
        "source_record": {"foo": "bar"},
        "type": "sample"
    }
    _post_to_modelserver(client, data_dict, "sample", "/opencontext")


def test_sesar_material_type(client: TestClient):
    data_dict = {
        "source_record": {"foo": "bar"},
        "type": "material"
    }
    _post_to_modelserver(client, data_dict, "material", "/sesar")