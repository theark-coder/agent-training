from agent_training.type_demo import find_user_name
from agent_training.type_demo import get_users


def test_get_users():
    users = get_users()

    assert len(users) == 2
    assert users[0].name == "Jack"
    assert users[1].role == "Backend Engineer"

def test_find_user_name():
    assert find_user_name(1) == "Jack"


def test_find_user_name_not_found():
    assert find_user_name(2) is None