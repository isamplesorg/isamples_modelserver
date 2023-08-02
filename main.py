import json
from typing import Type

import fastapi
import logging

import uvicorn
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from enums import ISBModelType
from isamples_metadata.metadata_exceptions import SESARSampleTypeException, TestRecordException, MetadataException
from isamples_metadata.taxonomy.isamplesfasttext import SMITHSONIAN_FEATURE_PREDICTOR
from isamples_metadata.taxonomy.metadata_models import (
    SampleTypePredictor,
    MaterialTypePredictor,
    PredictionResult,
    MetadataModelLoader,
    OpenContextSamplePredictor,
    OpenContextMaterialPredictor,
    SESARMaterialPredictor,
    SampledFeaturePredictor,
)

app = fastapi.FastAPI()


def exception_response(exception: Type[MetadataException]) -> PlainTextResponse:
    exception_classname = exception.__class__.__name__
    exception_message = str(exception)
    # http status code 409 is "Conflict".  Seemed most appropriate here.
    json_str = json.dumps({"exception": exception_classname, "message": exception_message})
    return PlainTextResponse(json_str, status_code=409)


@app.exception_handler(SESARSampleTypeException)
def sesar_sample_type_exception_handler(request: Request, exc: SESARSampleTypeException) -> PlainTextResponse:
    # The model invocation code raises if a record should be excluded, return a sentinel so callers don't choke
    return exception_response(SESARSampleTypeException)


@app.exception_handler(TestRecordException)
def test_record_exception_handler(request: Request, exc: SESARSampleTypeException) -> PlainTextResponse:
    # The model invocation code raises if a record should be excluded, return a sentinel so callers don't choke
    return exception_response(TestRecordException)


def main():
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


@app.on_event("startup")
def on_startup():
    # Force load these into memory on app startup so we don't incur a lazy loading penalty on first request
    print("Loading OpenContext sample model…")
    MetadataModelLoader.get_oc_sample_model()
    print("Loading OpenContext material model…")
    MetadataModelLoader.get_oc_material_model()
    print("Loading SESAR material model…")
    MetadataModelLoader.get_sesar_material_model()
    print("Loading done.")


def get_opencontext_sample_type_predictor() -> SampleTypePredictor:
    ocs_model = MetadataModelLoader.get_oc_sample_model()
    return OpenContextSamplePredictor(ocs_model)


def get_opencontext_material_type_predictor() -> MaterialTypePredictor:
    ocs_model = MetadataModelLoader.get_oc_material_model()
    return OpenContextMaterialPredictor(ocs_model)


def get_sesar_material_type_predictor() -> MaterialTypePredictor:
    sesar_model = MetadataModelLoader.get_sesar_material_model()
    return SESARMaterialPredictor(sesar_model)


def get_smithsonian_sampled_feature_predictor() -> SampledFeaturePredictor:
    return SMITHSONIAN_FEATURE_PREDICTOR


class PredictParams(BaseModel):
    source_record: dict
    type: ISBModelType


@app.post("/opencontext", name="OpenContext Model Invocation")
def opencontext(
    params: PredictParams,
    sample_type_predictor: SampleTypePredictor = Depends(
        get_opencontext_sample_type_predictor
    ),
    material_type_predictor: MaterialTypePredictor = Depends(
        get_opencontext_material_type_predictor
    ),
) -> list[PredictionResult]:
    if params.type == ISBModelType.SAMPLE:
        return sample_type_predictor.predict_sample_type(params.source_record)
    elif params.type == ISBModelType.MATERIAL:
        return material_type_predictor.predict_material_type(params.source_record)
    else:
        raise HTTPException(
            500,
            "Unable to serve specified model type. Valid types are 'sample' and 'material'.",
        )


@app.post("/sesar", name="SESAR Model Invocation")
def sesar(
    params: PredictParams,
    material_type_predictor: MaterialTypePredictor = Depends(
        get_sesar_material_type_predictor
    ),
) -> list[PredictionResult]:
    if params.type == ISBModelType.MATERIAL:
        return material_type_predictor.predict_material_type(params.source_record)
    else:
        raise HTTPException(
            500,
            "Unable to serve specified model type. The only valid type is 'material'.",
        )


class SampledFeatureParams(BaseModel):
    input: list[str]
    type: ISBModelType


@app.post("/smithsonian", name="Smithsonian Model Invocation")
def smithsonian(
    params: SampledFeatureParams,
    sampled_feature_predictor: SampledFeaturePredictor = Depends(
        get_smithsonian_sampled_feature_predictor
    ),
) -> str:
    """
    Predicts Smithsonian context value using the FastText model
    :param type: The type of value to predict, only valid value for Smithsonian is CONTEXT
    :param input: Comma-separated string of input parameters
    :return: The prediction result from the Smithsonian-trained FastText model
    """
    if params.input is None:
        raise HTTPException(500, "Input parameter is required.")
    if params.type == ISBModelType.CONTEXT:
        return sampled_feature_predictor.predict_sampled_feature(params.input)
    else:
        raise HTTPException(
            500,
            "Unable to serve specified model type. The only valid type is 'context'.",
        )


if __name__ == "__main__":
    logging.info("****************** Starting iSamples Model Server *****************")
    main()
