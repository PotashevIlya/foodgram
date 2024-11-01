import json
from csv import DictReader


def import_objects(filename, file_format, model):
    with open(
        f'data/{filename}.{file_format}', 'r', encoding='utf-8'
    ) as file:
        if file_format == 'json':
            reader = json.load
        else:
            reader = DictReader
        objects_list = [model(**record) for record in reader(file)]
        model.objects.bulk_create(objects_list, ignore_conflicts=True)
