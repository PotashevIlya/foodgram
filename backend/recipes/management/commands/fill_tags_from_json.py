from django.core.management.base import BaseCommand

from .utils import import_objects
from ...models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_objects('tags', 'json', Tag)
