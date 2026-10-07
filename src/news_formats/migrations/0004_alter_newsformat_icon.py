from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news_formats", "0003_replace_null_icons_with_empty_string"),
    ]

    operations = [
        migrations.AlterField(
            model_name="newsformat",
            name="icon",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
