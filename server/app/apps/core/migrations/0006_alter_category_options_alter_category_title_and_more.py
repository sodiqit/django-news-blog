# Generated by Django 4.0.5 on 2022-07-05 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_category_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['category_id'], 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterField(
            model_name='category',
            name='title',
            field=models.CharField(db_index=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='tag',
            name='title',
            field=models.CharField(db_index=True, max_length=128),
        ),
    ]
