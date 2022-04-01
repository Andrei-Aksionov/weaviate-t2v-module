import pytest
from hypothesis import given
from sentence_transformers import SentenceTransformer

from src import Meta, Vectorizer, config
from tests.utils.hypothesis import generate_text


@pytest.mark.asyncio
class TestVectorizer:
    @classmethod
    def setup_class(cls: "TestVectorizer") -> None:
        cls.model = SentenceTransformer(config.vectorizer.model_name)
        cls.vectorizer = Vectorizer(cls.model)
        cls.meta = Meta(cls.model)

    async def test_vectorizer_none_value_raises_exception(self) -> None:
        # Given
        text = None

        # When/Then
        with pytest.raises(ValueError, match="None value is not allowed"):
            await TestVectorizer.vectorizer.vectorize(text)

    @given(generate_text())
    async def test_vectorizer_returns_list(self, text: str) -> None:
        # When
        vector = await TestVectorizer.vectorizer.vectorize(text)

        # Then
        assert isinstance(vector, list)

    @given(generate_text())
    async def test_vectorizer_returns_list_of_floats(self, text: str) -> None:
        # When
        vector = await TestVectorizer.vectorizer.vectorize(text)

        # Then
        assert all(isinstance(x, float) for x in vector)
