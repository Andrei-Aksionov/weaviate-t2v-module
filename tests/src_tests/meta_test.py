import yaml
from sentence_transformers import SentenceTransformer

from src import Meta


class TestMeta:
    @classmethod
    def setup_class(cls: "TestMeta") -> None:
        with open("src/config/config.yaml", "r") as fin:
            config = yaml.safe_load(fin)
        cls.model = SentenceTransformer(config["vectorizer"]["model_name"])
        cls.meta = Meta(cls.model)

    def test_meta_output_is_dictionary(self) -> None:
        # When
        meta_info = TestMeta.meta.info

        # Then
        assert isinstance(meta_info, dict)

    def test_meta_output_dict_not_empty(self) -> None:
        # When
        meta_info = TestMeta.meta.info

        # Then
        assert bool(meta_info)
