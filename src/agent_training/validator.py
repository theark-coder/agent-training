class AgeValidationError(ValueError):
    pass

def validate_age(age: int) -> None:
    if age<0:
        raise AgeValidationError("age cannot be negative")
    if age > 150:
        raise AgeValidationError("age cannot be greater than 150")