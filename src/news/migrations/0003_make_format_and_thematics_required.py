# Generated manually on 2026-09-09

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Count


def check_no_news_without_format_or_thematics(apps, schema_editor):
    News = apps.get_model("news", "News")

    if News.objects.filter(format__isnull=True).exists():
        raise migrations.exceptions.MigrationError(
            "Cannot apply migration: some News objects have no format. "
            "Please assign a format to every News before migrating."
        )

    if (
        News.objects.annotate(thematic_count=Count("thematics"))
        .filter(thematic_count=0)
        .exists()
    ):
        raise migrations.exceptions.MigrationError(
            "Cannot apply migration: some News objects have no thematics. "
            "Please assign at least one thematic to every News before "
            "migrating."
        )


def reverse_check(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_news_format"),
    ]

    operations = [
        migrations.RunPython(
            check_no_news_without_format_or_thematics,
            reverse_check,
        ),
        migrations.AlterField(
            model_name="news",
            name="format",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="news",
                to="news_formats.newsformat",
                verbose_name="Format",
            ),
        ),
        migrations.AlterField(
            model_name="news",
            name="thematics",
            field=models.ManyToManyField(
                help_text="Thematics related to this news.",
                related_name="news",
                to="thematics.thematic",
                verbose_name="Thematics",
            ),
        ),
    ]
