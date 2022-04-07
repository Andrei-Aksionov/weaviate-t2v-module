from sentence_transformers import SentenceTransformer


class Meta:
    def __init__(self, model: SentenceTransformer) -> None:
        """Generate vectorizer model's meta info.

        Parameters
        ----------
        model : SentenceTransformer
        """
        self.model = model

    @property
    def info(self) -> dict:
        """Return dictionary with vectorizer model's info.

        Returns
        -------
        dict
            dictionary with 4 keys: name, version, language and description
        """
        return {
            "name": "sentence-transformer",
            "version": self.model._model_config["__version__"],
            "language": "en",
            "max_sequence_length": self.model.get_max_seq_length(),
            "embedding_size": self.model.get_sentence_embedding_dimension(),
            "description": str(self.model),
        }
