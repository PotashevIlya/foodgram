from rest_framework import serializers


def validate_ingredients_or_tags(all_id, model, field):
    if not all_id:
        raise serializers.ValidationError(
            {field: 'Укажите хотя бы один элемент'}
        )
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
            {
                'id': non_unique_elements,
                'error': 'Значения повторяются'
            }
        )
    if non_existing_elements:
        raise serializers.ValidationError(
            {
                'id': non_existing_elements,
                'error': 'Значения(й) не существует'
            }
        )
