from rest_framework import serializers

from recipes.constants import MIN_AMOUNT

def validate_ingredients_or_tags(all_id, model):
    if not all_id:
        raise serializers.ValidationError(
            {'Укажите хотя бы один элемент'}
        )
    # if mode == 'ingredients':
    #     all_id = [element['id'] for element in array]
    #     small_amount_ingredients = [
    #         element['id'] for element in array if element['amount']
    #         < MIN_AMOUNT
    #     ]
    #     if small_amount_ingredients:
    #         raise serializers.ValidationError(
    #             f'Кол-во меньше {MIN_AMOUNT}: {small_amount_ingredients}'
    #         )
    all_elements = []
    non_unique_elements = []
    non_existing_elements = []
    for id in all_id:
        if id in all_elements:
            non_unique_elements.append(id)
        if not model.objects.filter(id=id).exists():
            non_existing_elements.append(id)
        all_elements.append(id)
    if non_unique_elements:
        raise serializers.ValidationError(
            f'Значения не должны повторяться: {non_unique_elements}'
        )
    if non_existing_elements:
        raise serializers.ValidationError(
            f'Значений не существует: {non_existing_elements}'
        )