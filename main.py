from typing import Optional

import fastapi
import logging

import uvicorn
from fastapi import HTTPException

from enums import ISBModelType
from isamples_metadata.taxonomy.isamplesfasttext import SMITHSONIAN_FEATURE_PREDICTOR

app = fastapi.FastAPI()


def main():
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


@app.get("/opencontext", name="OpenContext Model Invocation")
def opencontext(type: Optional[ISBModelType] = None) -> str:
    if type == ISBModelType.SAMPLE:
        return "sample"
    elif type == ISBModelType.MATERIAL:
        return "material"
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
