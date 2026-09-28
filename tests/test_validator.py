import pytest

from agent_training.validator import AgeValidationError, validate_age
def test_validate_age():
    validate_age(22)
def test_validate_age_negative():
    with pytest.raises(AgeValidationError, match="age cannot be negative"):
        validate_age(-1)
def test_validate_age_too_large():
    with pytest.raises(AgeValidationError):
        validate_age(151)        