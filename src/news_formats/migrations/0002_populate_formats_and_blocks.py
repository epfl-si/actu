from django.core.management.color import no_style
from django.db import connection, migrations

BLOCK_TYPES = [
    (1, "WYSIWYG", "WYSIWYG", "WYSIWYG", "WYSIWYG"),
    (2, "Image", "Image", "Bild", "Immagine"),
    (3, "Galerie", "Gallery", "Galerie", "Galleria"),
    (4, "Texte + image", "Text + image", "Text + Bild", "Testo + immagine"),
    (5, "Son", "Audio", "Audio", "Audio"),
    (6, "Infographie", "Infographics", "Infografik", "Infografica"),
    (7, "Vidéo", "Video", "Video", "Video"),
    (8, "Citation", "Quote", "Zitat", "Citazione"),
    (
        9,
        "Découvrez également",
        "Discover also",
        "Entdecken Sie auch",
        "Scopri anche",
    ),
]

NEWS_FORMATS = [
    (1, "Nouvelle", "News", "News", "News", ""),
    (2, "Brève", "Brief", "Kurz", "Breve", ""),
    (3, "Galerie", "Gallery", "Galerie", "Galleria", "#image"),
    (
        4,
        "Infographie",
        "Infographics",
        "Infografik",
        "Infografica",
        "#pie-chart",
    ),
    (5, "Longread", "Longread", "Longread", "Longread", "#book-open"),
    (6, "Podcast", "Podcast", "Podcast", "Podcast", "#mic"),
    (7, "Portrait", "Portrait", "Porträt", "Ritratto", "#user"),
    (8, "Vidéo", "Video", "Video", "Video", "#play-circle"),
]

ALLOWED_BLOCKS = {
    1: [1, 2, 3, 4, 5, 6, 7, 8, 9],
    3: [1, 3, 9],
    4: [1, 6, 9],
    5: [1, 2, 3, 4, 5, 6, 7, 8, 9],
    6: [1, 2, 3, 4, 5, 7, 8, 9],
    7: [1, 2, 3, 4, 5, 7, 8, 9],
    8: [1, 7, 9],
}


def populate_data(apps, schema_editor):
    BlockType = apps.get_model("block_types", "BlockType")
    NewsFormat = apps.get_model("news_formats", "NewsFormat")

    block_types_dict = {}
    for pk, label_fr, label_en, label_de, label_it in BLOCK_TYPES:
        block_types_dict[pk], _ = BlockType.objects.update_or_create(
            id=pk,
            defaults={
                "label_fr": label_fr,
                "label_en": label_en,
                "label_de": label_de,
                "label_it": label_it,
            },
        )

    news_formats_dict = {}
    for pk, label_fr, label_en, label_de, label_it, icon in NEWS_FORMATS:
        news_formats_dict[pk], _ = NewsFormat.objects.update_or_create(
            id=pk,
            defaults={
                "label_fr": label_fr,
                "label_en": label_en,
                "label_de": label_de,
                "label_it": label_it,
                "icon": icon,
            },
        )

    for format_id, block_ids in ALLOWED_BLOCKS.items():
        news_formats_dict[format_id].allowed_blocks.set(
            [block_types_dict[block_id] for block_id in block_ids]
        )

    sequence_sql = connection.ops.sequence_reset_sql(
        no_style(), [BlockType, NewsFormat]
    )
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)


def reverse_populate_data(apps, schema_editor):
    BlockType = apps.get_model("block_types", "BlockType")
    NewsFormat = apps.get_model("news_formats", "NewsFormat")

    NewsFormat.objects.filter(id__in=[f[0] for f in NEWS_FORMATS]).delete()
    BlockType.objects.filter(id__in=[b[0] for b in BLOCK_TYPES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("news_formats", "0001_initial"),
        ("block_types", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(populate_data, reverse_populate_data),
    ]
