import os
from django.core.management import BaseCommand

from cookbook.settings import BASE_DIR
from api.models import Recipe


static_dir = os.path.join(BASE_DIR, "static")


class Command(BaseCommand):
    """Команда для добавления информации об изображениях в БД (рецепт)."""

    def handle(self, *args, **options):
        for file in os.listdir(static_dir):
            filename = file[: file.rfind(".")]
            recipe = Recipe.objects.get(name=filename)
            recipe.image = os.path.join(static_dir, file)
            recipe.save()
