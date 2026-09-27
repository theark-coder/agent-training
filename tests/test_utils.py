from agent_training.utils import Utils


def test_calculate_average():
    tils = Utils()
    assert tils.calculate_average([1, 2, 3, 4, 5]) == 3.0
def test_greet():
    tils = Utils()
    assert tils.greet("jack") == "Hello, jack!"    