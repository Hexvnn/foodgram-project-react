import csv

from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILES_DIR
from recipes.models import Tag


class Command(BaseCommand):
    """Команда для загрузки ингредиентов в базу данных """

    help = 'Загрузка ингредиентов в базу данных'

    def handle(self, *args, **kwargs):
        with open(
                f'{CSV_FILES_DIR}/tags.csv', encoding='utf-8'
        ) as file:
            csv_reader = csv.reader(file, delimiter=',', quotechar='"')
            new_tags = []
            for row in csv_reader:
                name, color, slug = row[0], row[1], row[2]
                if not Tag.objects.filter(name=name, color=color, slug=slug).exists():
                    new_tags.append(Tag(name=name, color=color, slug=slug))
            Tag.objects.bulk_create(new_tags)
            self.stdout.write(self.style.SUCCESS('Теги в базу данных загружены'))
            self.stdout.write(self.style.SUCCESS(f'Добавлено {len(new_tags)} тегов'))
