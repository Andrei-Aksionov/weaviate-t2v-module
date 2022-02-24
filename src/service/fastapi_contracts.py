from pydantic import BaseModel


class TextItem(BaseModel):
    """Class that helps FastAPI to parse incoming data properly."""

    text: str
