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
    unique_elements = []
    non_unique_elements = []
    non_existing_elements = []
    not_allowed_amount = []
    if mode == 'list':
        for element in array:
            if element.id in unique_elements:
                non_unique_elements.append(element.id)
            if not model.objects.filter(id=element.id).exists():
                non_existing_elements.append(element)
            unique_elements.append(element.id)
        if non_unique_elements:
            raise serializers.ValidationError(
                f'Значения не должны повторяться: {non_unique_elements}'
            )
        if non_existing_elements:
            raise serializers.ValidationError(
                f'Значений не существует: {non_existing_elements}'
            )
    if mode == 'objects':
        for element in array:
            if element['id'] in unique_elements:
                non_unique_elements.append(element['id'])
            if not model.objects.filter(id=element['id']).exists():
                non_existing_elements.append(element['id'])
            if element['amount'] < 1:
                not_allowed_amount.append(element['id'])
            unique_elements.append(element['id'])
        if non_unique_elements:
            raise serializers.ValidationError(
                f'Значения не должны повторяться: {non_unique_elements}'
            )
        if non_existing_elements:
            raise serializers.ValidationError(
                f'Значений не существует: {non_existing_elements}'
            )
        if not_allowed_amount:
            raise serializers.ValidationError(
                f'Укажите кол-во больше {MIN_AMOUNT}: {not_allowed_amount}'
            )
