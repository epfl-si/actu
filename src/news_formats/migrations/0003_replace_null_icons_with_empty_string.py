from django.db import migrations


def replace_null_icons_with_empty_string(apps, schema_editor):
    news_format = apps.get_model("news_formats", "NewsFormat")
    news_format.objects.filter(icon__isnull=True).update(icon="")


def restore_null_icons(apps, schema_editor):
    news_format = apps.get_model("news_formats", "NewsFormat")
    news_format.objects.filter(icon="").update(icon=None)


class Migration(migrations.Migration):
    dependencies = [
        ("news_formats", "0002_populate_formats_and_blocks"),
    ]

    operations = [
        migrations.RunPython(
            replace_null_icons_with_empty_string,
            restore_null_icons,
        ),
    ]
