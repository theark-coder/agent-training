from agent_training.http_demo import fetch_example


def test_fetch_example():
    assert fetch_example() == 200