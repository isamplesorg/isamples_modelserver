import fastapi
import logging
import uvicorn


app = fastapi.FastAPI()


def main():
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    logging.info("****************** Starting iSamples Model Server *****************")
    main()
