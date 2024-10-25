from django.core.management.base import BaseCommand

from ...models import Tag
from .utils import import_objects


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_objects('tags', 'json', Tag)
