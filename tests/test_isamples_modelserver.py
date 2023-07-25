import json
from typing import List

import pytest
from httpx import Response
from starlette.testclient import TestClient

from isamples_metadata.taxonomy.metadata_models import (
    SampleTypePredictor,
    PredictionResult,
    MaterialTypePredictor, SampledFeaturePredictor,
)
from main import (
    app,
    get_opencontext_sample_type_predictor,
    get_opencontext_material_type_predictor,
    get_sesar_material_type_predictor, get_smithsonian_sampled_feature_predictor,
)


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


@pytest.fixture(name="sampled_feature_predictor")
def sampled_feature_fixture():
    class MockSampledFeaturePredictor(SampledFeaturePredictor):
        def predict_sampled_feature(self, context: List[str]) -> str:
            return "sampled feature"

    return MockSampledFeaturePredictor()


@pytest.fixture(name="client")
def client_fixture(
    sample_type_predictor: SampleTypePredictor,
    material_type_predictor: MaterialTypePredictor,
    sampled_feature_predictor: SampledFeaturePredictor
):
    def get_sample_type_predictor_override():
        return sample_type_predictor

    def get_material_type_predictor_override():
        return material_type_predictor

    def get_sampled_feature_predictor_override():
        return sampled_feature_predictor

    app.dependency_overrides[
        get_opencontext_sample_type_predictor
    ] = get_sample_type_predictor_override
    app.dependency_overrides[
        get_opencontext_material_type_predictor
    ] = get_material_type_predictor_override
    app.dependency_overrides[
        get_sesar_material_type_predictor
    ] = get_material_type_predictor_override
    app.dependency_overrides[
        get_smithsonian_sampled_feature_predictor
    ] = get_sampled_feature_predictor_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _post_to_modelserver(client, data_dict, expected_value, handler, do_json_asserts=True) -> Response:
    post_data = json.dumps(data_dict).encode("utf-8")
    response = client.post(handler, data=post_data)
    assert response.status_code == 200
    if do_json_asserts:
        response_data = response.json()
        assert 1 == len(response_data)
        prediction_result = response_data[0]
        assert expected_value == prediction_result["value"]
        assert 0.5 == prediction_result["confidence"]
    return response


def test_getopencontext_material_type(client: TestClient):
    data_dict = {"source_record": {"foo": "bar"}, "type": "material"}
    _post_to_modelserver(client, data_dict, "material", "/opencontext")


def test_getopencontext_sample_type(client: TestClient):
    data_dict = {"source_record": {"foo": "bar"}, "type": "sample"}
    _post_to_modelserver(client, data_dict, "sample", "/opencontext")


def test_sesar_material_type(client: TestClient):
    data_dict = {"source_record": {"foo": "bar"}, "type": "material"}
    _post_to_modelserver(client, data_dict, "material", "/sesar")


def test_smithsonian_sampled_feature(client: TestClient):
    data_dict = {"type": "context", "input": ["foo"]}
    response = _post_to_modelserver(client, data_dict, "sampled feature", "/smithsonian", False)
    assert response.text == "\"sampled feature\""
