from typing import Optional

import fastapi
import logging

import uvicorn
from fastapi import HTTPException, Depends
from pydantic import BaseModel

from enums import ISBModelType
from isamples_metadata.taxonomy.isamplesfasttext import SMITHSONIAN_FEATURE_PREDICTOR
from isamples_metadata.taxonomy.metadata_models import SampleTypePredictor, MaterialTypePredictor, PredictionResult, \
    MetadataModelLoader, OpenContextSamplePredictor, OpenContextMaterialPredictor

app = fastapi.FastAPI()


def main():
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


def get_opencontext_sample_type_predictor() -> SampleTypePredictor:
    ocs_model = MetadataModelLoader.get_oc_sample_model()
    return OpenContextSamplePredictor(ocs_model)


def get_opencontext_material_type_predictor() -> MaterialTypePredictor:
    ocs_model = MetadataModelLoader.get_oc_sample_model()
    return OpenContextMaterialPredictor(ocs_model)


class PredictParams(BaseModel):
    source_record: dict
    type: ISBModelType


@app.post("/opencontext", name="OpenContext Model Invocation")
async def opencontext(request: fastapi.Request,
                params: PredictParams,
                sample_type_predictor: SampleTypePredictor = Depends(get_opencontext_sample_type_predictor),
                material_type_predictor: MaterialTypePredictor = Depends(get_opencontext_material_type_predictor),
                ) -> list[PredictionResult]:
    if params.type == ISBModelType.SAMPLE:
        return sample_type_predictor.predict_sample_type(params.source_record)
    elif params.type == ISBModelType.MATERIAL:
        return material_type_predictor.predict_material_type(params.source_record)
    else:
        raise HTTPException(500, "Unable to serve specified model type. Valid types are 'sample' and 'material'.")


@app.get("/sesar", name="SESAR Model Invocation")
def sesar(type: Optional[ISBModelType] = None) -> str:
    if type == ISBModelType.SAMPLE:
        return "sample"
    elif type == ISBModelType.MATERIAL:
        return "material"
    else:
        raise HTTPException(500, "Unable to serve specified model type. Valid types are 'sample' and 'material'.")


@app.get("/smithsonian", name="Smithsonian Model Invocation")
def smithsonian(type: Optional[ISBModelType] = None, input: Optional[str] = None) -> str:
    """
    Predicts Smithsonian context value using the FastText model
    :param type: The type of value to predict, only valid value for Smithsonian is CONTEXT
    :param input: Comma-separated string of input parameters
    :return: The prediction result from the Smithsonian-trained FastText model
    """
    if input is None:
        raise HTTPException(500, "Input parameter is required.")
    if type == ISBModelType.CONTEXT:
        categories = SMITHSONIAN_FEATURE_PREDICTOR.predict_sampled_feature(input.split(","))
        return categories
    else:
        raise HTTPException(500, "Unable to serve specified model type. The only valid type is 'context'.")


if __name__ == "__main__":
    logging.info("****************** Starting iSamples Model Server *****************")
    main()
