# Generated by Django 4.0.5 on 2022-06-30 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_user_avatar_alter_user_username"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("category_id", models.CharField(blank=True, max_length=128)),
                ("title", models.CharField(max_length=128)),
            ],
        ),
    ]
