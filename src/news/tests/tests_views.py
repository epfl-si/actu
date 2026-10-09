from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import override

from entities.models import Entity
from news.models import News
from news_formats.models import NewsFormat
from topics.models import Topic
from translations.models import NewsTranslation

User = get_user_model()


class ManageNewsViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.format = NewsFormat.objects.create(label_en="Article")
        self.topic = Topic.objects.create(label_en="Research")

    def _create_news(self):
        news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        news.topics.add(self.topic)
        return news

    def test_limits_to_ten_news_per_page(self):
        for index in range(12):
            news = self._create_news()
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

    def test_filters_news_by_translation_status(self):
        draft_news = self._create_news()
        NewsTranslation.objects.create(
            news=draft_news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
        )
        published_news = self._create_news()
        NewsTranslation.objects.create(
            news=published_news,
            language="en",
            status=NewsTranslation.Status.PUBLISHED,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("manage_news"),
            {"status": NewsTranslation.Status.PUBLISHED},
        )

        self.assertEqual(
            [row["news"] for row in response.context["news_rows"]],
            [published_news],
        )
        self.assertEqual(
            response.context["filters"]["status"],
            {NewsTranslation.Status.PUBLISHED},
        )

    def test_filters_news_by_search_term(self):
        matching_news = self._create_news()
        NewsTranslation.objects.create(
            news=matching_news,
            language="en",
            title="DNS: Skis not found",
            created_by=self.user,
        )
        non_matching_news = self._create_news()
        NewsTranslation.objects.create(
            news=non_matching_news,
            language="en",
            title="DNF: Lost in the forest",
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("manage_news"),
            {"search": "dns"},
        )

        self.assertEqual(
            [row["news"] for row in response.context["news_rows"]],
            [matching_news],
        )
        self.assertEqual(response.context["filters"]["search"], "dns")

    def test_filters_news_by_topic_entity_creator_and_format(self):
        other_user = User.objects.create_user(
            username="cologna",
            sciper="88888888",
        )
        topic = Topic.objects.create(label_en="Cross-country skiing")
        other_topic = Topic.objects.create(label_en="Giant slalom")
        entity = Entity.objects.create(label_en="Finland Team")
        other_entity = Entity.objects.create(label_en="Swiss Team")
        news_format = NewsFormat.objects.create(label_en="News")
        other_format = NewsFormat.objects.create(label_en="Portrait")

        matching_news = News.objects.create(
            created_by=self.user,
            format=news_format,
        )
        matching_news.topics.add(topic)
        matching_news.entities.add(entity)
        NewsTranslation.objects.create(
            news=matching_news,
            language="en",
            title="Niskanen brings the Finnish power",
            created_by=self.user,
        )

        non_matching_news = News.objects.create(
            created_by=other_user,
            format=other_format,
        )
        non_matching_news.topics.add(other_topic)
        non_matching_news.entities.add(other_entity)
        NewsTranslation.objects.create(
            news=non_matching_news,
            language="en",
            title="Odermatt too fast for his own skis",
            created_by=other_user,
        )

        self.client.force_login(self.user)
        filters = {
            "topics": topic.id,
            "entities": entity.id,
            "created_by": self.user.id,
            "formats": news_format.id,
        }
        response = self.client.get(reverse("manage_news"), filters)

        self.assertEqual(
            [row["news"] for row in response.context["news_rows"]],
            [matching_news],
        )
        self.assertEqual(
            response.context["filters"]["topics"],
            {topic.id},
        )
        self.assertEqual(response.context["filters"]["entities"], {entity.id})
        self.assertEqual(
            response.context["filters"]["created_by"],
            {self.user.id},
        )
        self.assertEqual(
            response.context["filters"]["formats"],
            {news_format.id},
        )

    def test_selecting_all_active_entities_does_not_filter_news(self):
        first_entity = Entity.objects.create(label_en="Jamaica Team")
        second_entity = Entity.objects.create(label_en="Japan Team")
        first_news = self._create_news()
        first_news.entities.add(first_entity)
        NewsTranslation.objects.create(
            news=first_news,
            language="en",
            title="Sanka asks for more ice",
            created_by=self.user,
        )
        second_news = self._create_news()
        second_news.entities.add(second_entity)
        NewsTranslation.objects.create(
            news=second_news,
            language="en",
            title="Japan: gravity is optional",
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("manage_news"),
            {"entities": [first_entity.id, second_entity.id]},
        )

        self.assertEqual(
            {row["news"] for row in response.context["news_rows"]},
            {first_news, second_news},
        )
        self.assertEqual(response.context["filters"]["entities"], set())

    def test_manage_news_supports_show_metadata_query_parameter(self):
        news = self._create_news()
        NewsTranslation.objects.create(
            news=news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
            title="Hidden metadata test",
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("manage_news"),
            {"show_metadata": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["show_metadata"])


class DeleteNewsTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.format = NewsFormat.objects.create(label_en="Article")
        self.topic = Topic.objects.create(label_en="Research")
        self.news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.news.topics.add(self.topic)
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
        self.format = NewsFormat.objects.create(label_en="Article")
        self.topic = Topic.objects.create(label_en="Research")
        self.news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.news.topics.add(self.topic)
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


class ListNewsViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.format = NewsFormat.objects.create(label_en="Article")
        self.topic = Topic.objects.create(label_en="Research")
        self.entity = Entity.objects.create(label_en="EPFL")

        self.news_pub_en = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.news_pub_en.topics.add(self.topic)
        self.news_pub_en.entities.add(self.entity)
        self.trans_pub_en = NewsTranslation.objects.create(
            news=self.news_pub_en,
            language="en",
            status=NewsTranslation.Status.PUBLISHED,
            created_by=self.user,
            title="English Published Space News",
            published_at=timezone.now(),
        )

        self.news_draft_en = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.news_draft_en.topics.add(self.topic)
        self.news_draft_en.entities.add(self.entity)
        self.trans_draft_en = NewsTranslation.objects.create(
            news=self.news_draft_en,
            language="en",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
            title="English Draft News",
        )

        self.news_pub_fr = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        self.news_pub_fr.topics.add(self.topic)
        self.news_pub_fr.entities.add(self.entity)
        self.trans_pub_fr = NewsTranslation.objects.create(
            news=self.news_pub_fr,
            language="fr",
            status=NewsTranslation.Status.PUBLISHED,
            created_by=self.user,
            title="Actualité Publiée en Français",
            published_at=timezone.now(),
        )

    def _create_news(self):
        news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        news.topics.add(self.topic)
        news.entities.add(self.entity)
        return news

    def test_view_url_exists_at_desired_location_and_uses_correct_template(
        self,
    ):
        url = reverse("list_news")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")

        self.assertIn(self.topic, response.context["topics"])
        self.assertIn(self.entity, response.context["entities"])
        self.assertIn(self.format, response.context["formats"])

    def test_shows_only_published_news_in_english(self):
        url = reverse("list_news")
        with override("en"):
            response = self.client.get(url)
            news_in_context = list(response.context["news_translations"])

            self.assertIn(self.trans_pub_en, news_in_context)
            self.assertNotIn(self.trans_draft_en, news_in_context)
            self.assertNotIn(self.trans_pub_fr, news_in_context)

    def test_shows_only_published_news_in_french(self):
        with override("fr"):
            url = reverse("list_news")
            response = self.client.get(url)
            news_in_context = list(response.context["news_translations"])

            self.assertIn(self.trans_pub_fr, news_in_context)
            self.assertNotIn(self.trans_pub_en, news_in_context)

    def test_filters_by_search_query(self):
        url = reverse("list_news")
        with override("en"):
            response = self.client.get(url, {"search": "space"})
            news_in_context = list(response.context["news_translations"])

            self.assertIn(self.trans_pub_en, news_in_context)
            self.assertEqual(response.context["filters"]["search"], "space")

            response_empty = self.client.get(url, {"search": "foobar"})
            self.assertEqual(
                len(list(response_empty.context["news_translations"])), 0
            )

    def test_filters_by_topic_entity_and_format(self):
        url = reverse("list_news")
        with override("en"):
            filters = {
                "topics": self.topic.id,
                "entities": self.entity.id,
                "formats": self.format.id,
            }
            response = self.client.get(url, filters)
            news_in_context = list(response.context["news_translations"])

            self.assertIn(self.trans_pub_en, news_in_context)
            self.assertIn(self.topic.id, response.context["filters"]["topics"])
            self.assertIn(
                self.entity.id, response.context["filters"]["entities"]
            )
            self.assertIn(
                self.format.id, response.context["filters"]["formats"]
            )

    def test_pagination_limits_to_10_items_per_page(self):
        with override("fr"):
            for i in range(14):
                news = self._create_news()
                NewsTranslation.objects.create(
                    news=news,
                    language="fr",
                    status=NewsTranslation.Status.PUBLISHED,
                    created_by=self.user,
                    title=f"Actualité FR {i}",
                    published_at=timezone.now() - timezone.timedelta(days=i),
                )

            url = reverse("list_news")
            response = self.client.get(url)
            news_list = list(response.context["news_translations"])

            self.assertEqual(len(news_list), 10)
            self.assertEqual(response.context["paginator"].count, 15)
            self.assertEqual(response.context["paginator"].num_pages, 2)

    def test_pagination_loads_second_page_correctly(self):
        with override("fr"):
            for i in range(14):
                news = self._create_news()
                NewsTranslation.objects.create(
                    news=news,
                    language="fr",
                    status=NewsTranslation.Status.PUBLISHED,
                    created_by=self.user,
                    title=f"Actualité FR {i}",
                    published_at=timezone.now() - timezone.timedelta(days=i),
                )

            url = reverse("list_news")
            response = self.client.get(url, {"page": "2"})
            news_list = list(response.context["news_translations"])

            self.assertEqual(len(news_list), 5)
            self.assertEqual(response.context["page_obj"].number, 2)

    def test_pagination_preserves_query_string_without_page_parameter(self):
        with override("en"):
            url = reverse("list_news")
            response = self.client.get(
                url,
                {
                    "search": "space",
                    "topics": self.topic.id,
                    "page": "2",
                },
            )

            query_string = response.context["query_string"]
            self.assertIn("search=space", query_string)
            self.assertIn(f"topics={self.topic.id}", query_string)
            self.assertNotIn("page=", query_string)


class CreateNewsTranslationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.topic = Topic.objects.create(label_en="Research", is_active=True)
        self.topic_2 = Topic.objects.create(
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
        self.assertIn(self.topic, response.context["topics"])
        self.assertIn(self.entity, response.context["entities"])
        self.assertIn(self.format, response.context["formats"])
        self.assertEqual(response.context["selected_topic_ids"], set())
        self.assertEqual(response.context["selected_entity_ids"], set())
        self.assertIsNone(response.context["selected_format_id"])

    def test_get_excludes_inactive_topics_and_entities(self):
        Topic.objects.create(label_en="Old Topic", is_active=False)
        Entity.objects.create(label_en="Old Entity", is_active=False)

        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        response = self.client.get(url)

        topic_labels = {t.label_en for t in response.context["topics"]}
        entity_labels = {e.label_en for e in response.context["entities"]}
        self.assertNotIn("Old Topic", topic_labels)
        self.assertNotIn("Old Entity", entity_labels)

    def test_valid_post_creates_news_and_translation(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "title": "New EPFL article",
            "topics": [self.topic.id],
            "entities": [self.entity.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "0",
            "urls-INITIAL_FORMS": "0",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        news = News.objects.get()
        self.assertEqual(news.created_by, self.user)
        self.assertEqual(
            set(news.topics.values_list("id", flat=True)),
            {self.topic.id},
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

    def test_valid_post_with_multiple_topics_and_entities(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "title": "Research and education",
            "topics": [self.topic.id, self.topic_2.id],
            "entities": [self.entity.id, self.entity_2.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "0",
            "urls-INITIAL_FORMS": "0",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        news = News.objects.get()
        self.assertEqual(
            set(news.topics.values_list("id", flat=True)),
            {self.topic.id, self.topic_2.id},
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
            "topics": [],
            "entities": [self.entity.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "0",
            "urls-INITIAL_FORMS": "0",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(News.objects.count(), 0)
        self.assertEqual(NewsTranslation.objects.count(), 0)
        self.assertIn(
            "A news must have at least one topic.",
            response.content.decode(),
        )

    def test_invalid_post_preserves_selected_values(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "topics": [self.topic.id, self.topic_2.id],
            "entities": [self.entity.id, self.entity_2.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "0",
            "urls-INITIAL_FORMS": "0",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["selected_topic_ids"],
            {self.topic.id, self.topic_2.id},
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

    def test_injection_of_invalid_data(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "topics": ["foobar", self.topic_2.id],
            "entities": ["foobar", self.entity_2.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "0",
            "urls-INITIAL_FORMS": "0",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["selected_topic_ids"],
            {self.topic_2.id},
        )
        self.assertEqual(
            response.context["selected_entity_ids"],
            {self.entity_2.id},
        )

    def test_success_message_is_shown_after_creation(self):
        self.client.force_login(self.user)
        url = reverse("create_news", args=["en"])
        data = {
            "title": "New article",
            "topics": [self.topic.id],
            "entities": [self.entity.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "0",
            "urls-INITIAL_FORMS": "0",
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
        self.topic = Topic.objects.create(
            label_en="Research",
            is_active=True,
        )
        self.topic_2 = Topic.objects.create(
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
        self.news.topics.add(self.topic)
        self.news.entities.add(self.entity)
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            title="Original title",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
        )
        self.existing_url = self.translation.urls.create(
            url="https://example.com",
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
            response.context["selected_topic_ids"],
            {self.topic.id},
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
        self.assertEqual(
            response.context["news_blocks_editor_props"],
            {"newsId": self.news.id, "language": "en"},
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
            "topics": [self.topic_2.id],
            "entities": [self.entity_2.id],
            "format": self.format_2.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "1",
            "urls-INITIAL_FORMS": "1",
            "urls-0-id": self.existing_url.id,
            "urls-0-url": self.existing_url.url,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.news.refresh_from_db()
        self.translation.refresh_from_db()

        self.assertEqual(
            set(self.news.topics.values_list("id", flat=True)),
            {self.topic_2.id},
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
            "topics": [self.topic_2.id],
            "entities": [self.entity_2.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "1",
            "urls-INITIAL_FORMS": "1",
            "urls-0-id": self.existing_url.id,
            "urls-0-url": self.existing_url.url,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required.", response.content.decode())
        self.assertEqual(
            response.context["selected_topic_ids"],
            {self.topic_2.id},
        )
        self.assertEqual(
            response.context["selected_entity_ids"],
            {self.entity_2.id},
        )

    def test_update_urls(self):
        self.client.force_login(self.user)
        url = reverse(
            "edit_news",
            kwargs={
                "news_id": self.news.id,
                "lang": "en",
            },
        )
        data = {
            "title": "Original title",
            "topics": [self.topic.id],
            "entities": [self.entity.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "2",
            "urls-INITIAL_FORMS": "1",
            "urls-0-id": self.existing_url.id,
            "urls-0-url": self.existing_url.url,
            "urls-1-url": "https://example.epfl.ch/article2",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.news.refresh_from_db()
        self.translation.refresh_from_db()

        self.assertEqual(
            set(self.translation.urls.values_list("url", flat=True)),
            {"https://example.com", "https://example.epfl.ch/article2"},
        )

    def test_delete_url(self):
        self.client.force_login(self.user)
        url = reverse(
            "edit_news",
            kwargs={
                "news_id": self.news.id,
                "lang": "en",
            },
        )
        data = {
            "title": "Original title",
            "topics": [self.topic.id],
            "entities": [self.entity.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "1",
            "urls-INITIAL_FORMS": "1",
            "urls-0-id": self.existing_url.id,
            "urls-0-url": self.existing_url.url,
            "urls-0-DELETE": "on",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.news.refresh_from_db()
        self.translation.refresh_from_db()

        self.assertEqual(
            set(self.translation.urls.values_list("url", flat=True)),
            set(),
        )

    def test_duplicate_url_in_submitted_forms_shows_error(self):
        self.client.force_login(self.user)
        url = reverse(
            "edit_news",
            kwargs={
                "news_id": self.news.id,
                "lang": "en",
            },
        )
        data = {
            "title": "Original title",
            "topics": [self.topic.id],
            "entities": [self.entity.id],
            "format": self.format.id,
            "author": "Lindsey Vonn",
            "standfirst": "This is a standfirst",
            "urls-TOTAL_FORMS": "2",
            "urls-INITIAL_FORMS": "1",
            "urls-0-id": self.existing_url.id,
            "urls-0-url": "https://example.com",
            "urls-1-url": "https://example.com",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The same link cannot be added twice.",
            response.content.decode(),
        )
        self.assertEqual(
            set(self.translation.urls.values_list("url", flat=True)),
            {"https://example.com"},
        )


class PreviewNewsTranslationViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="bentoumi",
            sciper="99999999",
        )
        self.format = NewsFormat.objects.create(label_en="Article")
        self.topic = Topic.objects.create(label_en="Research")

    def _create_news(self):
        news = News.objects.create(
            created_by=self.user,
            format=self.format,
        )
        news.topics.add(self.topic)
        return news

    def _create_translation(
        self,
        news,
        language="en",
        status=NewsTranslation.Status.DRAFT,
        **kwargs,
    ):
        return NewsTranslation.objects.create(
            news=news,
            language=language,
            title=f"Test news {language}",
            status=status,
            created_by=self.user,
            **kwargs,
        )

    def test_preview_news_displays_draft(self):
        news = self._create_news()
        translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "preview_news",
                kwargs={
                    "news_id": news.id,
                    "lang": translation.language,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "preview_news.html")
        self.assertEqual(response.context["translation"], translation)

    def test_preview_news_displays_published_translation(self):
        news = self._create_news()
        translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "preview_news",
                kwargs={
                    "news_id": news.id,
                    "lang": translation.language,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "preview_news.html")
        self.assertEqual(response.context["translation"], translation)

    def test_view_news_displays_published_translation(self):
        news = self._create_news()
        translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        with override("en"):
            response = self.client.get(
                reverse(
                    "view_news",
                    kwargs={"slug": translation.slug},
                )
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_news.html")
        self.assertEqual(response.context["translation"], translation)

    def test_view_news_does_not_display_draft(self):
        news = self._create_news()
        translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
        )

        with override("en"):
            response = self.client.get(
                reverse(
                    "view_news",
                    kwargs={"slug": translation.slug},
                )
            )

        self.assertEqual(response.status_code, 404)

    def test_view_news_redirects_to_current_language_translation(self):
        news = self._create_news()

        fr_translation = self._create_translation(
            news=news,
            language="fr",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        en_translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        with override("en"):
            response = self.client.get(
                reverse(
                    "view_news",
                    kwargs={"slug": fr_translation.slug},
                )
            )

        self.assertRedirects(
            response,
            reverse(
                "view_news",
                kwargs={"slug": en_translation.slug},
            ),
        )

    def test_view_news_returns_404_when_current_language_is_unavailable(
        self,
    ):
        news = self._create_news()

        fr_translation = self._create_translation(
            news=news,
            language="fr",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
        )

        with override("en"):
            response = self.client.get(
                reverse(
                    "view_news",
                    kwargs={"slug": fr_translation.slug},
                )
            )

        self.assertEqual(response.status_code, 404)

    def test_publish_news_translation_publishes_draft(self):
        news = self._create_news()

        translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
        )

        self.client.force_login(self.user)

        before = timezone.now()

        response = self.client.post(
            reverse(
                "publish_news_translation",
                kwargs={
                    "news_id": news.id,
                    "lang": translation.language,
                },
            )
        )

        after = timezone.now()

        translation.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse(
                "preview_news",
                kwargs={
                    "news_id": news.id,
                    "lang": translation.language,
                },
            ),
        )

        self.assertEqual(
            translation.status,
            NewsTranslation.Status.PUBLISHED,
        )
        self.assertIsNotNone(translation.published_at)
        self.assertGreaterEqual(translation.published_at, before)
        self.assertLessEqual(translation.published_at, after)

    def test_publish_news_translation_does_not_publish_published_translation(
        self,
    ):
        news = self._create_news()

        translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "publish_news_translation",
                kwargs={
                    "news_id": news.id,
                    "lang": translation.language,
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_unpublish_news_translation_changes_published_to_draft(self):
        news = self._create_news()

        published_at = timezone.now()

        translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.PUBLISHED,
            published_at=published_at,
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "unpublish_news_translation",
                kwargs={
                    "news_id": news.id,
                    "lang": translation.language,
                },
            )
        )

        translation.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse(
                "preview_news",
                kwargs={
                    "news_id": news.id,
                    "lang": translation.language,
                },
            ),
        )

        self.assertEqual(
            translation.status,
            NewsTranslation.Status.DRAFT,
        )
        self.assertEqual(translation.published_at, published_at)

    def test_unpublish_news_translation_does_not_unpublish_draft(self):
        news = self._create_news()

        translation = self._create_translation(
            news=news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "unpublish_news_translation",
                kwargs={
                    "news_id": news.id,
                    "lang": translation.language,
                },
            )
        )

        self.assertEqual(response.status_code, 404)
