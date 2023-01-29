import re


LEGAL_CHARACTERS = re.compile(r'[\w.@+-]')


def username_validator(value):
    """Проверка символов в логине."""
    forbidden_chars = ''.join(set(LEGAL_CHARACTERS.sub('', value)))
    if forbidden_chars:
        raise ValueError(
            f'Нельзя использовать символ(ы): {forbidden_chars}'
        )
