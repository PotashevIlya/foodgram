import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


MIN_AMOUNT = 1
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


def validate_ingredients_or_tags(array, mode, model):
    if not array:
        raise serializers.ValidationError(
            'Укажите хотя бы один элемент'
        )
    if mode == 'ingredients':
        all_id = [element['id'] for element in array]
        small_amount_ingredients = [
            element['id'] for element in array if element['amount']
            < MIN_AMOUNT
        ]
        if small_amount_ingredients:
            raise serializers.ValidationError(
                f'Кол-во меньше {MIN_AMOUNT}: {small_amount_ingredients}'
            )
    if mode == 'tags':
        all_id = [element.id for element in array]
    all_elements = []
    non_unique_elements = []
    non_existing_elements = []
    for element in all_id:
        if element in all_elements:
            non_unique_elements.append(element)
        if not model.objects.filter(id=element).exists():
            non_existing_elements.append(element)
        all_elements.append(element)
    if non_unique_elements:
        raise serializers.ValidationError(
            f'Значения не должны повторяться: {non_unique_elements}'
        )
    if non_existing_elements:
        raise serializers.ValidationError(
            f'Значений не существует: {non_existing_elements}'
        )
