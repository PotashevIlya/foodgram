import json
from csv import DictReader


def import_objects(filename, file_format, model):
    with open(
        f'data/{filename}.{file_format}', 'r', encoding='utf-8'
    ) as file:
        objects_list = []
        if file_format == 'json':
            records = json.load(file)
        else:
            records = DictReader(file)
        for record in records:
            objects_list.append(
                model(
                    **record
                )
            )
        model.objects.bulk_create(objects_list)
