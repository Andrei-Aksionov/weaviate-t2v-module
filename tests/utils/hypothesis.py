import string
from typing import Optional

from hypothesis import strategies as st


def generate_text(
    alphabet: str = string.ascii_letters,
    min_word_len: int = 0,
    max_word_len: Optional[int] = None,
    min_number_of_words: int = 0,
    max_number_of_words: Optional[int] = None,
) -> str:
    """Generates text in given range from specified vocabulary.

    Note: words are not meaningful as they are composed from randomly picked characters.

    Parameters
    ----------
    alphabet : str, optional
        from alphabet characters are randomly selected, by default string.ascii_letters
    min_word_len : int, optional
        minimal number of characters in a word, by default 0
    max_word_len : Optional[int], optional
        maximal number of characters in a word, by default None
    min_number_of_words : int, optional
        minimal number of words in a result text, by default 0
    max_number_of_words : Optional[int], optional
        maximal number of words in a result text, by default None

    Returns
    -------
    str
        text with words that are generated with specified parameters
    """
    return st.lists(
        elements=st.text(
            alphabet=alphabet,
            min_size=min_word_len,
            max_size=max_word_len,
        ),
        min_size=min_number_of_words,
        max_size=max_number_of_words,
    ).map(lambda word: " ".join(word))
