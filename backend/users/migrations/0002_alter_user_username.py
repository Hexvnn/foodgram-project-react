# Generated by Django 4.2.11 on 2024-03-25 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, max_length=150, unique=True, verbose_name='Уникальный юзернейм'),
        ),
    ]
