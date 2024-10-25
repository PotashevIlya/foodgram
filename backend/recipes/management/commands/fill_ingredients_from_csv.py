from django.core.management.base import BaseCommand

from ...models import Ingredient
from .utils import import_objects


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_objects('ingredients', 'csv', Ingredient)
