from csv import DictReader

from django.core.management.base import BaseCommand

from ...models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
            'data/ingredients.csv', 'r', encoding='utf-8'
        ) as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                ingredient = Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                ingredient.save()
