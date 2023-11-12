import os
from dotenv import load_dotenv

from django.contrib.auth.models import User
from django.core.management import BaseCommand

load_dotenv()


class Command(BaseCommand):
    """Команда для создания администратора."""

    def handle(self, *args, **options):
        username = os.environ.get("USERNAME")
        user = User.objects.filter(username=username)

        if not user:
            User.objects.create_superuser(
                username=username,
                email=os.environ.get("EMAIL"),
                password=os.environ.get("PASSWORD")
            )
