from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from entities.models import Entity
from news.models import News
from news_formats.models import NewsFormat
from thematics.models import Thematic
from translations.models import NewsTranslation

User = get_user_model()


class ManageNewsViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )

    def test_limits_to_ten_news_per_page(self):
        for index in range(12):
            news = News.objects.create(created_by=self.user)
            NewsTranslation.objects.create(
                news=news,
                language="en",
                status=NewsTranslation.Status.DRAFT,
                created_by=self.user,
            )

        self.client.force_login(self.user)
        response = self.client.get(reverse("manage_news"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["news_rows"]), 10)
        self.assertEqual(response.context["page_obj"].paginator.per_page, 10)
        self.assertTrue(response.context["page_obj"].has_next())


class DeleteNewsTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.news = News.objects.create(created_by=self.user)
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
        )

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_archives_translation_successfully(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.translation.refresh_from_db()
        self.assertEqual(
            self.translation.status,
            NewsTranslation.Status.ARCHIVED,
        )
        self.assertEqual(self.translation.updated_by, self.user)

    def test_already_archived_shows_warning(self):
        self.translation.status = NewsTranslation.Status.ARCHIVED
        self.translation.save()

        self.client.force_login(self.user)
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("already archived", str(messages[0]))

    def test_nonexistent_translation_gets_404(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "fr"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_success_message_shown(self):
        self.client.force_login(self.user)
        url = reverse(
            "delete_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("archived successfully", str(messages[0]))


class RestoreNewsTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.news = News.objects.create(created_by=self.user)
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            status=NewsTranslation.Status.ARCHIVED,
            created_by=self.user,
        )

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_restores_translation_to_draft(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.translation.refresh_from_db()
        self.assertEqual(
            self.translation.status,
            NewsTranslation.Status.DRAFT,
        )
        self.assertEqual(self.translation.updated_by, self.user)

    def test_not_archived_shows_warning(self):
        self.translation.status = NewsTranslation.Status.DRAFT
        self.translation.save()

        self.client.force_login(self.user)
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url, follow=True)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("not archived", str(messages[0]))

    def test_nonexistent_translation_gets_404(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "fr"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_success_message_shown(self):
        self.client.force_login(self.user)
        url = reverse(
            "restore_news_translation",
            args=[self.news.id, "en"],
        )
        response = self.client.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("restored successfully", str(messages[0]))


class CreateNewsTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.thematic = Thematic.objects.create(
            label_en="Research", is_active=True
        )
        self.thematic_2 = Thematic.objects.create(
            label_en="Innovation", is_active=True
        )
        self.entity = Entity.objects.create(label_en="EPFL", is_active=True)
        self.entity_2 = Entity.objects.create(
            label_en="ETH Zurich", is_active=True
        )
        self.format = NewsFormat.objects.create(label_en="Article")

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "create_news",
            args=["en"],
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_get_renders_empty_form_with_context(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_news.html")
        self.assertIn(self.thematic, response.context["thematics"])
        self.assertIn(self.entity, response.context["entities"])
        self.assertIn(self.format, response.context["formats"])
        self.assertEqual(response.context["selected_thematic_ids"], set())
        self.assertEqual(response.context["selected_entity_ids"], set())
        self.assertIsNone(response.context["selected_format_id"])

    def test_get_excludes_inactive_thematics_and_entities(self):
        Thematic.objects.create(label_en="Old Thematic", is_active=False)
        Entity.objects.create(label_en="Old Entity", is_active=False)

        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        response = self.client.get(url)

        thematic_labels = {t.label_en for t in response.context["thematics"]}
        entity_labels = {e.label_en for e in response.context["entities"]}
        self.assertNotIn("Old Thematic", thematic_labels)
        self.assertNotIn("Old Entity", entity_labels)

    def test_valid_post_creates_news_and_translation(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "title": "New EPFL article",
            "thematics": [self.thematic.id],
            "entities": [self.entity.id],
            "format": self.format.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        news = News.objects.get()
        self.assertEqual(news.created_by, self.user)
        self.assertEqual(
            set(news.thematics.values_list("id", flat=True)),
            {self.thematic.id},
        )
        self.assertEqual(
            set(news.entities.values_list("id", flat=True)),
            {self.entity.id},
        )
        self.assertEqual(news.format, self.format)
        translation = NewsTranslation.objects.get(
            news=news,
            language="en",
        )
        self.assertEqual(translation.title, "New EPFL article")
        self.assertEqual(translation.created_by, self.user)
        self.assertEqual(
            response.url,
            reverse(
                "edit_news",
                kwargs={
                    "news_id": news.id,
                    "lang": "en",
                },
            ),
        )

    def test_valid_post_with_multiple_thematics_and_entities(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "title": "Research and education",
            "thematics": [self.thematic.id, self.thematic_2.id],
            "entities": [self.entity.id, self.entity_2.id],
            "format": self.format.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        news = News.objects.get()
        self.assertEqual(
            set(news.thematics.values_list("id", flat=True)),
            {self.thematic.id, self.thematic_2.id},
        )
        self.assertEqual(
            set(news.entities.values_list("id", flat=True)),
            {self.entity.id, self.entity_2.id},
        )

    def test_invalid_post_renders_form_again(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "title": "Incomplete article",
            "thematics": [],
            "entities": [self.entity.id],
            "format": self.format.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(News.objects.count(), 0)
        self.assertEqual(NewsTranslation.objects.count(), 0)
        self.assertIn("No thematic provided.", response.content.decode())

    def test_invalid_post_preserves_selected_values(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "thematics": [self.thematic.id, self.thematic_2.id],
            "entities": [self.entity.id, self.entity_2.id],
            "format": self.format.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["selected_thematic_ids"],
            {self.thematic.id, self.thematic_2.id},
        )
        self.assertEqual(
            response.context["selected_entity_ids"],
            {self.entity.id, self.entity_2.id},
        )
        self.assertEqual(
            response.context["selected_format_id"],
            self.format.id,
        )
        self.assertIn("This field is required.", response.content.decode())

    def test_success_message_is_shown_after_creation(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "title": "New article",
            "thematics": [self.thematic.id],
            "entities": [self.entity.id],
            "format": self.format.id,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        message_list = list(response.context["messages"])
        self.assertEqual(len(message_list), 1)
        self.assertEqual(
            str(message_list[0]),
            "The news has been saved successfully.",
        )


class EditNewsTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.thematic = Thematic.objects.create(
            label_en="Research",
            is_active=True,
        )
        self.thematic_2 = Thematic.objects.create(
            label_en="Education",
            is_active=True,
        )
        self.entity = Entity.objects.create(
            label_en="EPFL",
            is_active=True,
        )
        self.entity_2 = Entity.objects.create(
            label_en="UNIL",
            is_active=True,
        )
        self.format = NewsFormat.objects.create(
            label_en="Article",
        )
        self.format_2 = NewsFormat.objects.create(
            label_en="Press release",
        )
        self.news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.news.thematics.add(self.thematic)
        self.news.entities.add(self.entity)
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            title="Original title",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
        )

    def test_redirects_anonymous_user_to_login(self):
        url = reverse(
            "edit_news",
            kwargs={
                "news_id": self.news.id,
                "lang": "en",
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_get_renders_existing_news(self):
        self.client.force_login(self.user)
        url = reverse(
            "edit_news",
            kwargs={
                "news_id": self.news.id,
                "lang": "en",
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_news.html")
        self.assertEqual(
            response.context["selected_thematic_ids"],
            {self.thematic.id},
        )
        self.assertEqual(
            response.context["selected_entity_ids"],
            {self.entity.id},
        )
        self.assertEqual(
            response.context["selected_format_id"],
            self.format.id,
        )

        form = response.context["form"]
        self.assertEqual(
            form.translation.initial["title"],
            "Original title",
        )

    def test_post_updates_news_and_translation(self):
        self.client.force_login(self.user)
        url = reverse(
            "edit_news",
            kwargs={
                "news_id": self.news.id,
                "lang": "en",
            },
        )
        data = {
            "title": "Updated title",
            "thematics": [self.thematic_2.id],
            "entities": [self.entity_2.id],
            "format": self.format_2.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.news.refresh_from_db()
        self.translation.refresh_from_db()

        self.assertEqual(
            set(self.news.thematics.values_list("id", flat=True)),
            {self.thematic_2.id},
        )
        self.assertEqual(
            set(self.news.entities.values_list("id", flat=True)),
            {self.entity_2.id},
        )
        self.assertEqual(self.news.format, self.format_2)
        self.assertEqual(self.translation.title, "Updated title")
        self.assertEqual(self.news.created_by, self.user)
        self.assertEqual(self.translation.created_by, self.user)

    def test_invalid_post_renders_form_again(self):
        self.client.force_login(self.user)
        url = reverse(
            "edit_news",
            kwargs={
                "news_id": self.news.id,
                "lang": "en",
            },
        )
        data = {
            "title": "",
            "thematics": [self.thematic_2.id],
            "entities": [self.entity_2.id],
            "format": self.format.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required.", response.content.decode())
        self.assertEqual(
            response.context["selected_thematic_ids"],
            {self.thematic_2.id},
        )
        self.assertEqual(
            response.context["selected_entity_ids"],
            {self.entity_2.id},
        )
