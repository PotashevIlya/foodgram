from django.core.management.base import BaseCommand

from .utils import import_objects
from ...models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_objects('ingredients', 'csv', Ingredient)
