import uvicorn
from fastapi import FastAPI, HTTPException, Response, status
from loguru import logger
from sentence_transformers import SentenceTransformer

from src import Meta, TextItem, Vectorizer, config

app = FastAPI()


@app.on_event("startup")
def startup_even() -> None:
    """Code below will be executed on app start."""
    global vectorizer, meta_info
    model = SentenceTransformer(config.vectorizer.model_name)
    vectorizer = Vectorizer(model)
    meta_info = Meta(model)


@app.get("/.well-known/live", response_class=Response)
@app.get("/.well-known/ready", response_class=Response)
def live_and_ready(response: Response) -> None:
    """Required by weaviate's transformer module.

    GET /.well-known/live -> respond 204 when the app is alive
    GET /.well-known/ready -> respond 204 when the app is ready to serve traffic

    More info here: https://weaviate.io/developers/weaviate/current/modules/custom-modules.html

    Parameters
    ----------
    response : Response
        provided automatically by FastAPI
    """
    response.status_code = status.HTTP_204_NO_CONTENT


@app.get("/meta")
def meta() -> dict:
    """Returns information about the model that is used for vectorization.

    Returns
    -------
    dict
        dictionary with the description
    """
    return meta_info.info


@app.post("/vectors")
async def vectorize(item: TextItem) -> dict:
    """Returns vector representation of the given text.

    Parameters
    ----------
    input : TextInput
        contains one field: text. Should contain only string, not a list of strings.

    Returns
    -------
    dict
        dictionary with 3 keys:
            - text (what was originally passed to the endpoint),
            - vector (vector representation of the given text),
            - dim (dimensionality of the vector)

    Raises
    ------
    HTTPException
        in case of internal error during vectorization process
    """
    try:
        vector = await vectorizer.vectorize(item.text)
        return {
            "text": item.text,
            "vector": vector,
            "dim": len(vector),
        }
    except Exception as e:
        error_message = str(e) or "Vectorization failed due to an internal error"
        logger.exception(error_message)
        raise HTTPException(status_code=500, detail=error_message) from e


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.app.host,
        port=config.app.port,
    )
