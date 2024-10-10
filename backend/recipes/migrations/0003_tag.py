# Generated by Django 3.2.3 on 2024-10-10 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20241009_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название тега', max_length=32, unique=True, verbose_name='Название тега')),
                ('slug', models.SlugField(help_text='Укажите слаг тега', max_length=32, unique=True, verbose_name='Слаг тега')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
    ]
