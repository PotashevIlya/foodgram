import json
from csv import DictReader


def import_objects(filename, file_format, model):
    with open(
        f'data/{filename}.{file_format}', 'r', encoding='utf-8'
    ) as file:
        reader = json.load if file_format == 'json' else DictReader
        objects_list = [model(**record) for record in reader(file)]
        model.objects.bulk_create(objects_list, ignore_conflicts=True)
