import re

from django.core.exceptions import ValidationError

WRONG_SYMBOLS_MESSAGE = (
    'Допустимы буквы, цифры и символы @ . + - _ .'
    'Нельзя использовать символы: {wrong_symbols}'
)


def validate_username(username):
    wrong_symbols = re.findall(r'[^\w.@+-]', username)
    if wrong_symbols:
        raise ValidationError(
            WRONG_SYMBOLS_MESSAGE.format(
                wrong_symbols=''.join(set(wrong_symbols))
            )
        )
    return username
