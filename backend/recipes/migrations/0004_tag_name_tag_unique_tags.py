# Generated by Django 4.2.11 on 2024-04-28 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_taginrecipe_shoppingcart_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='name',
            field=models.CharField(default='name', max_length=200, unique=True, verbose_name='Название тэга'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('name', 'color', 'slug'), name='unique_tags'),
        ),
    ]
