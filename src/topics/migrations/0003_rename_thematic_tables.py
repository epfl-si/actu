# Generated manually on 2026-09-28
# Renames database objects still using the old "thematics" naming to their
# "topics" equivalents. Databases migrated before the rename (production)
# are renamed here; fresh databases already get the new names from the
# migrations above, so every step below is skipped there.

from django.db import migrations


def align_database_names(apps, schema_editor):
    connection = schema_editor.connection
    quote = connection.ops.quote_name
    with connection.cursor() as cursor:
        tables = set(connection.introspection.table_names(cursor))

        def rename_table(old_name, new_name):
            if old_name not in tables:
                return
            schema_editor.execute(
                "ALTER TABLE {} RENAME TO {}".format(
                    quote(old_name), quote(new_name)
                )
            )
            tables.remove(old_name)
            tables.add(new_name)

        def rename_column(table_name, old_name, new_name):
            if table_name not in tables:
                return
            columns = {
                column.name
                for column in connection.introspection.get_table_description(
                    cursor, table_name
                )
            }
            if old_name not in columns:
                return
            schema_editor.execute(
                "ALTER TABLE {} RENAME COLUMN {} TO {}".format(
                    quote(table_name), quote(old_name), quote(new_name)
                )
            )

        rename_table("thematics_thematic", "topics_topic")

        rename_column("news_news_thematics", "thematic_id", "topic_id")
        rename_table("news_news_thematics", "news_news_topics")

        rename_column("homepages_homepage", "thematic_id", "topic_id")

        ContentType = apps.get_model("contenttypes", "ContentType")
        ContentType.objects.filter(
            app_label="thematics", model="thematic"
        ).update(app_label="topics", model="topic")
        ContentType.objects.clear_cache()


class Migration(migrations.Migration):

    dependencies = [
        ("topics", "0002_remove_thematic_has_homepage"),
    ]

    operations = [
        migrations.RunPython(align_database_names, align_database_names),
    ]
