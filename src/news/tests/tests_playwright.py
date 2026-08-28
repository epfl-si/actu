import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import expect

from news.models import News
from translations.models import NewsTranslation
from utils.testing import PlaywrightTestCase

User = get_user_model()


class EditNewsDragAndDropPlaywrightTests(PlaywrightTestCase):

    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(
            username="dragdropuser",
            sciper="99999999",
        )
        self.login_as(self.user)

        self.news = News.objects.create(created_by=self.user)
        self.translation = NewsTranslation.objects.create(
            news=self.news,
            language="en",
            status=NewsTranslation.Status.DRAFT,
            created_by=self.user,
            title="Drag and drop test",
            body={
                "time": 1234567890,
                "blocks": [
                    {"type": "paragraph", "data": {"text": "First block"}},
                    {"type": "paragraph", "data": {"text": "Second block"}},
                ],
                "version": "2.31.6",
            },
        )

    def test_drag_and_drop_reorders_blocks(self):
        self.page.goto(
            self.live_server_url
            + reverse("edit_news", args=[self.news.id, "en"])
        )

        editor_holder = self.page.locator("#id_body_editorjs_holder")
        expect(editor_holder).to_be_visible()

        blocks = editor_holder.locator(".ce-block")
        expect(blocks).to_have_count(2)

        first_block = blocks.nth(0)
        second_block = blocks.nth(1)

        expect(first_block).to_contain_text("First block")
        expect(second_block).to_contain_text("Second block")

        # Focus the second block's content so the toolbar moves to that block.
        second_block.locator(".ce-block__content").click()

        settings_button = editor_holder.locator(".ce-toolbar__settings-btn")
        expect(settings_button).to_be_visible()

        # Drag the toolbar's settings button (now the drag handle) above the
        # first block to reorder the blocks.
        settings_button.drag_to(first_block)

        # Wait for Editor.js onChange to update the hidden textarea.
        textarea = self.page.locator("textarea[name='body']")
        expect(textarea).to_have_value(
            lambda value: value and "Second block" in value
        )

        body_json = json.loads(textarea.input_value())
        texts = [block["data"]["text"] for block in body_json["blocks"]]
        self.assertEqual(texts, ["Second block", "First block"])
