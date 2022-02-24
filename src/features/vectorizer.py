import numpy as np
from sentence_transformers import SentenceTransformer


class Vectorizer:
    def __init__(self, model: SentenceTransformer) -> None:
        """Vectorize text into vector by sentence transformer model.

        Parameters
        ----------
        model : SentenceTransformer
        """
        self.model = model

    async def vectorize(self, text: str) -> list[float]:
        """Vectorize text into vector.

        Parameters
        ----------
        text : str

        Returns
        -------
        list[float]
            vector representation of the given text
        """
        if text is None:
            raise ValueError("None value is not allowed")
        vector: np.ndarray = self.model.encode(text)
        return vector.tolist()
