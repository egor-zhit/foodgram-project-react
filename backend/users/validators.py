import re
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation as p

LEGAL_CHARACTERS = re.compile(r'^[\w.@+-]+\Z')


def username_validator(value):
    """Проверка символов в логине."""
    forbidden_chars = ''.join(set(LEGAL_CHARACTERS.sub('', value)))
    if forbidden_chars:
        raise ValidationError(
            f'Нельзя использовать символ(ы): {forbidden_chars}'
        )
    return value


def password_validator(value):
    validators = p.get_default_password_validators()
    errors = []
    for validator in validators:
        try:
            validator.validate(value)
        except ValidationError as error:
            errors.append(error)
    if errors:
        raise ValidationError(errors)
    return value
