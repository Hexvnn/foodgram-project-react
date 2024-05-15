import csv

from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILES_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов в базу данных """

    help = 'Загрузка ингредиентов в базу данных'

    def handle(self, *args, **kwargs):
        with open(
                f'{CSV_FILES_DIR}/ingredients.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                name, measurement_unit = row[0], row[1]
                if not Ingredient.objects.filter(name=name, measurement_unit=measurement_unit).exists():
                    Ingredient.objects.create(name=name, measurement_unit=measurement_unit)
            self.stdout.write(self.style.SUCCESS('Ингредиенты в базу данных загружены'))
            self.stdout.write(self.style.SUCCESS(f'Добавлено {Ingredient.objects.count()} ингредиентов'))
