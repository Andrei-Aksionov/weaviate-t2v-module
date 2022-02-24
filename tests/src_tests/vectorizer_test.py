import pytest
import yaml
from sentence_transformers import SentenceTransformer

from src import Meta, Vectorizer


@pytest.mark.asyncio
class TestVectorizer:
    @classmethod
    def setup_class(cls: "TestVectorizer") -> None:
        with open("src/config/config.yaml", "r") as fin:
            config = yaml.safe_load(fin)
        cls.model = SentenceTransformer(config["vectorizer"]["model_name"])
        cls.vectorizer = Vectorizer(cls.model)
        cls.meta = Meta(cls.model)

    async def test_vectorizer_none_value_raises_exception(self) -> None:
        # Given
        text = None

        # When/Then
        with pytest.raises(ValueError, match="None value is not allowed"):
            await TestVectorizer.vectorizer.vectorize(text)

    @pytest.mark.parametrize("text", ["", "Test text"])
    async def test_vectorizer_returns_list(self, text: str) -> None:
        # When
        vector = await TestVectorizer.vectorizer.vectorize(text)

        # Then
        assert isinstance(vector, list)

    @pytest.mark.parametrize("text", ["", "Test text"])
    async def test_vectorizer_returns_list_of_floats(self, text: str) -> None:
        # When
        vector = await TestVectorizer.vectorizer.vectorize(text)

        # Then
        assert all(isinstance(x, float) for x in vector)
