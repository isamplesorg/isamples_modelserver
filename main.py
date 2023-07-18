from typing import Optional

import fastapi
import logging
import uvicorn
from fastapi import HTTPException

from enums import ISBModelType

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
def smithsonian(type: Optional[ISBModelType] = None) -> str:
    if type == ISBModelType.CONTEXT:
        return "context"
    else:
        raise HTTPException(500, "Unable to serve specified model type. The only valid type is 'context'.")


if __name__ == "__main__":
    logging.info("****************** Starting iSamples Model Server *****************")
    main()
