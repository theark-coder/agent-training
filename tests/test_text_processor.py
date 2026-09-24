from agent_training.text_processor import TextProcessor


def test_normalize():
    processor = TextProcessor()

    assert processor.normalize("Hello Agent") == "hello agent"
def test_word_count():
    processor = TextProcessor()

    assert processor.word_count("Hello Agent Agent") == 3
def test_most_common_words():
    processor = TextProcessor()

    result = processor.most_common_words(
        "Hello Agent Agent Python Python Python",
        2,
    )

    assert result == [
        ("python", 3),
        ("agent", 2),
    ]
def test_word_count_empty():
    processor = TextProcessor()

    assert processor.word_count("") == 0