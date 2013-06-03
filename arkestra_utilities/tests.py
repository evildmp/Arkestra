from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client

from news_and_events.models import NewsArticle

class NewsManagerTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        # create a news item
        self.tootharticle = NewsArticle(
            title = "All about teeth",
            slug = "all-about-teeth",
            )

    def test_published_items_no_saved_items(self):
        self.assertEqual(
            list(NewsArticle.objects.published_items()),
            []
            )

    def test_published_items_one_saved_item_unpublished(self):
        self.tootharticle.date = datetime.now() - timedelta(minutes=30)
        self.tootharticle.save()
        self.assertEqual(
            list(NewsArticle.objects.published_items()),
            []
            )

    def test_published_items_one_saved_published_but_future_item(self):
        self.tootharticle.published = True
        self.tootharticle.date = datetime.now() + timedelta(minutes=30)
        self.tootharticle.save()
        self.assertEqual(
            list(NewsArticle.objects.published_items()),
            []
            )

    def test_published_items_one_saved_published_item(self):
        self.tootharticle.published = True
        self.tootharticle.date = datetime.now() - timedelta(minutes=30)
        self.tootharticle.save()
        self.assertEqual(
            list(NewsArticle.objects.published_items()),
            [self.tootharticle]
            )
  
    def test_published_items_one_saved_published_item_not_in_list(self):
        self.tootharticle.published = True
        self.tootharticle.date = datetime.now() - timedelta(minutes=30)
        self.tootharticle.save()
        self.assertEqual(
            list(NewsArticle.objects.listable_published_items()),
            []
            )

    def test_published_items_one_saved_published_item_in_list(self):
        self.tootharticle.published = True
        self.tootharticle.date = datetime.now() - timedelta(minutes=30)
        self.tootharticle.save()
        self.assertEqual(
            list(NewsArticle.objects.listable_published_items()),
            [self.tootharticle]
            )
