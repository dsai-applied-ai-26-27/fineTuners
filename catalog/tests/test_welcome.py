"""What is put in front of a person unasked: the tour once, then the news
(catalog/welcome.py, catalog/news.py, accounts.Profile)."""

import importlib
from datetime import date
from unittest import mock

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import Enrollment, Profile
from catalog import news
from catalog.models import Course
from catalog.news import Point, Update
from catalog.welcome import mark_seen

User = get_user_model()
SEEN = "/whats-new/seen/"
OPEN_MIDDLEWARE = [name for name in settings.MIDDLEWARE if "LoginRequired" not in name]

OFFER = 'x-data="tour(true)"'
NEWS = '<dialog class="dialog tour news"'


class NewsListTests(SimpleTestCase):
    """The list is written by hand, so its rules are checked here."""

    def test_numbers_only_go_down_from_the_top(self):
        numbers = [update.number for update in news.UPDATES]
        self.assertEqual(numbers, sorted(set(numbers), reverse=True))
        self.assertGreater(min(numbers), 0)
        self.assertEqual(news.LATEST, numbers[0])

    def test_every_link_leads_somewhere(self):
        for update in news.UPDATES:
            for point in update.points:
                with self.subTest(update=update.number, point=point.title):
                    self.assertTrue(point.title and point.text)
                    if point.link:
                        self.assertTrue(reverse(point.link).startswith("/"))
                        self.assertTrue(point.label)

    def test_since_gives_what_came_after(self):
        self.assertEqual(news.since(news.LATEST), [])
        self.assertEqual(news.since(0), list(news.UPDATES))


class WelcomeTests(TestCase):
    def setUp(self):
        cache.clear()
        Course.objects.create(slug="rl", series="rl", title="Reinforcement Learning", code="RL")
        self.ada = User.objects.create_user("ada", email="ada@example.test")
        Enrollment.objects.create(user=self.ada, series="rl")
        self.client.force_login(self.ada)

    def seen(self, what, upto=None):
        return self.client.post(SEEN, {"what": what, "upto": news.LATEST if upto is None else upto})

    # -- the tour ---------------------------------------------------------------------------

    def test_a_first_visit_is_offered_the_tour_and_no_news(self):
        home = self.client.get("/")
        self.assertContains(home, OFFER)
        self.assertNotContains(home, NEWS)
        self.assertContains(home, f'data-seen="{SEEN}" data-upto="{news.LATEST}"')
        # Looking at the page records nothing: only the browser saying it was shown does.
        self.assertFalse(Profile.objects.exists())
        self.assertContains(self.client.get("/"), OFFER)

    def test_once_shown_it_is_not_offered_again_on_any_device(self):
        self.assertEqual(self.seen("tour").status_code, 204)
        profile = Profile.objects.get(user=self.ada)
        self.assertIsNotNone(profile.tour_seen_at)
        self.assertEqual((profile.tour_update, profile.news_seen), (news.LATEST, news.LATEST))
        # Another browser has no memory of its own; the account does.
        elsewhere = self.client_class()
        elsewhere.force_login(self.ada)
        home = elsewhere.get("/")
        self.assertNotContains(home, OFFER)
        self.assertContains(home, 'x-data="tour(false)"')  # still there to be asked for
        self.assertNotContains(home, NEWS)  # the tour was the current one: nothing is news

    def test_it_is_offered_on_the_dashboard_only(self):
        for path in ("/courses/rl/", "/settings/", "/whats-new/"):
            with self.subTest(path=path):
                self.assertNotContains(self.client.get(path), OFFER)

    def test_asking_for_the_tour_again_changes_nothing_about_the_first_time(self):
        self.seen("tour", upto=0)
        first = Profile.objects.get(user=self.ada)
        self.seen("tour")  # opened again from Settings, later
        again = Profile.objects.get(user=self.ada)
        self.assertEqual((again.tour_seen_at, again.tour_update), (first.tour_seen_at, 0))
        self.assertEqual(again.news_seen, news.LATEST)  # the tour they just saw is current

    def test_it_has_a_step_about_asking_and_about_educators(self):
        home = self.client.get("/")
        self.assertContains(home, "Missing something? Say so")
        self.assertContains(home, "Ask or report</strong> in the menu")
        self.assertContains(home, "<strong>educator</strong>")
        self.assertEqual(home.content.decode().count("data-step"), 6)

    # -- the news ---------------------------------------------------------------------------

    def test_someone_who_took_the_tour_earlier_is_shown_what_changed_since(self):
        Profile.objects.create(user=self.ada, tour_seen_at=timezone.now(), tour_update=0)
        home = self.client.get("/")
        self.assertNotContains(home, OFFER)
        self.assertContains(home, NEWS)
        self.assertContains(home, news.UPDATES[0].title)
        self.assertContains(home, 'href="/ask/"')
        # A course's front page is the other place people arrive at.
        self.assertContains(self.client.get("/courses/rl/"), NEWS)
        self.assertNotContains(self.client.get("/settings/"), NEWS)

    def test_the_news_is_shown_once(self):
        Profile.objects.create(user=self.ada, tour_seen_at=timezone.now(), tour_update=0)
        self.assertEqual(self.seen("news").status_code, 204)
        self.assertNotContains(self.client.get("/"), NEWS)
        profile = Profile.objects.get(user=self.ada)
        self.assertEqual((profile.news_seen, profile.tour_update), (news.LATEST, 0))

    def test_only_what_was_on_screen_counts_as_seen(self):
        """A tab opened before a release reports the number it was built with."""
        Profile.objects.create(user=self.ada, tour_seen_at=timezone.now(), tour_update=0)
        self.seen("news")  # shown the news as it is today
        today = news.UPDATES[0].title
        newer = Update(
            number=news.LATEST + 1,
            date=date(2027, 1, 5),
            title="Something newer still",
            points=(Point("A thing", "It does a thing."),),
        )
        # Then a release adds an update. patch.multiple swaps both names for the length of
        # the block and puts the real ones back afterwards.
        with mock.patch.multiple(news, UPDATES=(newer, *news.UPDATES), LATEST=newer.number):
            home = self.client.get("/")
            self.assertContains(home, "Something newer still")
            self.assertNotContains(home, today)  # already seen: not repeated
            self.assertNotContains(home, "See it in the tour")  # it has no step of its own
            # An old tab closing now still reports the number it was built with.
            self.seen("news", upto=newer.number - 1)
            self.assertContains(self.client.get("/"), "Something newer still")

    def test_the_number_sent_cannot_run_ahead_or_go_back(self):
        Profile.objects.create(user=self.ada, tour_seen_at=timezone.now(), news_seen=news.LATEST)
        self.seen("news", upto=10**9)
        self.assertEqual(Profile.objects.get(user=self.ada).news_seen, news.LATEST)
        self.seen("news", upto=0)
        self.assertEqual(Profile.objects.get(user=self.ada).news_seen, news.LATEST)

    def test_the_address_takes_a_post_with_something_it_knows(self):
        self.assertEqual(self.client.get(SEEN).status_code, 405)
        self.assertEqual(self.client.post(SEEN, {"what": "everything", "upto": 1}).status_code, 400)
        self.assertEqual(self.client.post(SEEN, {"what": "news", "upto": "soon"}).status_code, 400)
        self.assertFalse(Profile.objects.exists())

    # -- the page that keeps them all ---------------------------------------------------------

    def test_the_page_marks_what_came_after_the_persons_tour(self):
        page = self.client.get("/whats-new/")
        self.assertContains(page, news.UPDATES[0].title)
        self.assertNotContains(page, "New since your tour")  # no tour yet: nothing to compare
        mark_seen(self.ada, "tour", 0)
        self.assertContains(self.client.get("/whats-new/"), "New since your tour")
        Profile.objects.filter(user=self.ada).update(tour_update=news.LATEST)
        self.assertNotContains(self.client.get("/whats-new/"), "New since your tour")

    def test_settings_keeps_the_tour_and_leads_to_the_news(self):
        page = self.client.get("/settings/")
        self.assertContains(page, "Show the tour</button>")
        self.assertContains(page, 'href="/whats-new/"')

    # -- nobody signed in ---------------------------------------------------------------------

    def test_on_the_open_site_the_browser_remembers_and_there_is_no_news(self):
        with override_settings(REQUIRE_LOGIN=False, MIDDLEWARE=OPEN_MIDDLEWARE):
            visitor = self.client_class()
            home = visitor.get("/")
            self.assertContains(home, OFFER)  # tour.js then asks the browser's own memory
            self.assertNotContains(home, NEWS)
            self.assertNotContains(home, "Missing something? Say so")  # the forms need an account
            self.assertEqual(home.content.decode().count("data-step"), 5)
            self.assertEqual(visitor.post(SEEN, {"what": "tour", "upto": 1}).status_code, 204)
        self.assertFalse(Profile.objects.exists())


class ExistingPeopleTests(TestCase):
    """The migration that carries accounts over from when the browser remembered the tour."""

    def test_everyone_already_here_counts_as_shown_around(self):
        ada = User.objects.create_user("ada", email="ada@example.test")
        bob = User.objects.create_user("bob", email="bob@example.test")
        Profile.objects.create(user=bob, tour_seen_at=timezone.now(), tour_update=1, news_seen=1)
        # A module whose name starts with a digit cannot be imported with `import`.
        migration = importlib.import_module("accounts.migrations.0003_people_before_profiles")
        migration.mark_as_toured(apps, None)

        profile = Profile.objects.get(user=ada)
        self.assertEqual(profile.tour_seen_at, ada.date_joined)
        self.assertEqual((profile.tour_update, profile.news_seen), (0, 0))
        self.assertEqual(Profile.objects.get(user=bob).news_seen, 1)  # left as it was

        Course.objects.create(slug="rl", series="rl", title="Reinforcement Learning", code="RL")
        Enrollment.objects.create(user=ada, series="rl")
        self.client.force_login(ada)
        home = self.client.get("/")
        self.assertNotContains(home, OFFER)  # not walked through the site a second time
        self.assertContains(home, NEWS)  # told what is new instead
