"""Being an educator: the tour shown once on getting the role, the guide, being told about
a new version of the kit, and the e-mail that goes with those."""

from datetime import date
from unittest import mock

from django.core import mail as outbox
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import Enrollment, Profile
from catalog import news
from desk import kit, mail
from desk.models import Educator, EducatorApplication, KitAnnouncement

from .test_desk import DeskTestCase

OFFERED = "x-data=\"tour(true, 'educator')\""
THERE = "x-data=\"tour(false, 'educator')\""
SEEN = "/whats-new/seen/"
PAGE = "/educators/"
# Mail is sent from a thread; in a test it is delivered on the spot, into Django's outbox.
INLINE = mock.patch("desk.mail._dispatch", side_effect=mail.deliver)


class EducatorCase(DeskTestCase):
    def setUp(self):
        super().setUp()
        outbox.outbox.clear()
        # Ada has used the site for a while: the first tour and the news are behind her.
        Enrollment.objects.create(user=self.ada, series="rl")
        Profile.objects.create(user=self.ada, tour_seen_at=timezone.now(), news_seen=news.LATEST)


class EducatorTourTests(EducatorCase):
    def test_someone_who_writes_no_course_never_meets_it(self):
        for path in ("/", "/settings/", PAGE):
            with self.subTest(path=path):
                page = self.client.get(path)
                self.assertNotContains(page, "tour--educator")
                self.assertNotContains(page, "Show the educator tour")

    def test_it_is_offered_once_on_getting_the_role(self):
        Educator.objects.create(user=self.ada, series="rl")
        for path in ("/", "/courses/rl/", PAGE):
            with self.subTest(path=path):
                self.assertContains(self.client.get(path), OFFERED)
        # Showing it is not seeing it: only the browser saying so counts.
        self.assertIsNone(Profile.objects.get(user=self.ada).educator_tour_seen_at)

        self.assertEqual(self.client.post(SEEN, {"what": "educator", "upto": 0}).status_code, 204)
        self.assertIsNotNone(Profile.objects.get(user=self.ada).educator_tour_seen_at)
        elsewhere = self.client_class()  # another device, the same account
        elsewhere.force_login(self.ada)
        for path in ("/", PAGE):
            page = elsewhere.get(path)
            self.assertNotContains(page, OFFERED)
            self.assertContains(page, THERE)  # still there to be asked for

    def test_it_comes_before_the_news_and_never_with_it(self):
        Profile.objects.filter(user=self.ada).update(news_seen=0)
        Educator.objects.create(user=self.ada, series="rl")
        home = self.client.get("/")
        self.assertContains(home, OFFERED)
        self.assertNotContains(home, 'class="dialog tour news"')
        self.client.post(SEEN, {"what": "educator", "upto": 0})
        self.assertContains(self.client.get("/"), 'class="dialog tour news"')

    def test_it_stays_where_the_first_tour_is_and_on_the_educators_page(self):
        Educator.objects.create(user=self.ada, series="rl")
        settings_page = self.client.get("/settings/")
        self.assertContains(settings_page, "Show the tour</button>")
        self.assertContains(settings_page, "Show the educator tour</button>")
        self.assertContains(settings_page, "$dispatch('educator-tour')")
        self.assertContains(settings_page, THERE)  # asked for there, never offered
        self.assertContains(self.client.get(PAGE), "$dispatch('educator-tour')")

    def test_it_walks_from_the_kit_to_the_hand_in(self):
        Educator.objects.create(user=self.ada, series="rl")
        page = self.client.get(PAGE).content.decode()
        tour = page[page.index("tour--educator") :]
        for said in (
            "You are an educator now",
            "Get the educator kit",
            "uv run tools/unpack.py",
            "Update the CMS for this course",
            "uv run tools/pack.py",
            "A hand-in may only add",
            "git stash pop",
            'href="/educators/guide/"',
        ):
            self.assertIn(said, tour)
        self.assertEqual(tour.count("data-step"), 6)

    def test_the_guide_gives_the_repository_and_every_step_to_anyone_signed_in(self):
        page = self.client.get("/educators/guide/")
        for said in (
            "https://github.com/vrosi21/dsai-educator-kit",
            "git clone",
            "git remote set-url --push origin no-pushing",
            "Download the course files",
            "uv run tools/unpack.py",
            "Update the CMS for this course: rl",
            "uv run tools/pack.py rl",
            "Not remove, and not rewrite",
            "git stash pop",
            f"version {kit.LATEST}",
        ):
            self.assertContains(page, said)
        self.assertContains(self.client.get(PAGE), 'href="/educators/guide/"')

    def test_being_accepted_is_also_said_by_mail(self):
        self.client.post("/educators/apply/", self.application())
        offer = EducatorApplication.objects.get()
        with INLINE, self.captureOnCommitCallbacks(execute=True):
            offer.decide(EducatorApplication.Status.ACCEPTED)
        (message,) = outbox.outbox
        self.assertEqual(message.to, ["ada@example.test"])
        self.assertIn("You are an educator", message.subject)
        self.assertIn("/educators/guide/", message.body)
        # Accepting twice, or declining, writes to nobody.
        with INLINE, self.captureOnCommitCallbacks(execute=True):
            offer.decide(EducatorApplication.Status.ACCEPTED)
            offer.decide(EducatorApplication.Status.DECLINED)
        self.assertEqual(len(outbox.outbox), 1)


TWO = (
    kit.Version(
        2, date(2026, 11, 2), "Clearer rules for cards", ("AGENTS.md says more about cloze cards.",)
    ),
    kit.Version(1, date(2026, 10, 12), "The first kit", ("Everything.",)),
)


@mock.patch.multiple(kit, VERSIONS=TWO, LATEST=2)
class KitNewsTests(EducatorCase):
    """A new version of the kit is announced by the owner, in the admin. Only then are
    educators told: on their page, and by e-mail."""

    def setUp(self):
        super().setUp()
        Educator.objects.create(user=self.ada, series="rl")
        Profile.objects.filter(user=self.ada).update(educator_tour_seen_at=timezone.now())
        self.nameless = self.bob.__class__.objects.create_user("carol")  # an educator without mail
        Educator.objects.create(user=self.nameless, series="aai")
        self.ADD = reverse("admin:desk_kitannouncement_add")
        self.NOTICE = "Version 2 of the educator kit is out"

    def announce(self, number=2):
        self.client.force_login(self.admin)
        with INLINE:
            answer = self.client.post(self.ADD, {"number": number})
        self.client.force_login(self.ada)
        return answer

    def test_nothing_is_said_until_it_is_announced(self):
        self.assertNotContains(self.client.get(PAGE), self.NOTICE)
        self.assertEqual(outbox.outbox, [])

    def test_announcing_tells_educators_on_their_page_and_by_mail(self):
        self.assertEqual(self.announce().status_code, 302)
        told = KitAnnouncement.objects.get()
        self.assertEqual((told.number, told.recipients), (2, 1))
        (message,) = outbox.outbox  # Ada; not Bob, who writes nothing; not the one without mail
        self.assertEqual(message.to, ["ada@example.test"])
        self.assertIn("run git pull", message.subject)
        self.assertIn("AGENTS.md says more about cloze cards.", message.body)
        self.assertIn("because you are an educator", message.body)

        page = self.client.get(PAGE)
        self.assertContains(page, self.NOTICE)
        self.assertContains(page, "<code>git pull</code>")
        self.client.force_login(self.bob)
        self.assertNotContains(self.client.get(PAGE), self.NOTICE)

    def test_the_notice_goes_once_it_has_been_seen(self):
        self.announce()
        self.assertEqual(self.client.post(SEEN, {"what": "kit", "upto": 2}).status_code, 204)
        self.assertEqual(Profile.objects.get(user=self.ada).kit_seen, 2)
        self.assertNotContains(self.client.get(PAGE), self.NOTICE)

    def test_someone_made_an_educator_afterwards_is_not_told_old_news(self):
        self.announce()
        Profile.objects.filter(user=self.ada).update(educator_tour_seen_at=None)
        self.client.post(SEEN, {"what": "educator", "upto": 0})  # takes the tour today
        self.assertNotContains(self.client.get(PAGE), self.NOTICE)

    def test_a_version_is_announced_once_and_only_one_that_exists(self):
        self.announce()
        self.client.force_login(self.admin)
        form = self.client.get(self.ADD).context["adminform"].form
        self.assertEqual([number for number, _ in form.fields["number"].choices], [1])
        with INLINE:
            self.client.post(self.ADD, {"number": 2})
            self.client.post(self.ADD, {"number": 7})
        self.assertEqual(KitAnnouncement.objects.count(), 1)
        self.assertEqual(len(outbox.outbox), 1)

    def test_the_kit_carries_its_own_list_of_versions(self):
        text = kit.changelog()
        self.assertLess(
            text.index("## 2: Clearer rules for cards"), text.index("## 1: The first kit")
        )
        self.assertEqual([v.number for v in kit.news_for(0)], [])  # nothing announced yet
        self.announce()
        self.assertEqual([v.number for v in kit.news_for(0)], [2, 1])
        self.assertEqual([v.number for v in kit.news_for(2)], [])


class MailTests(EducatorCase):
    def test_only_people_who_can_be_reached_are_written_to_one_by_one(self):
        self.bob.is_active = False
        self.bob.save()
        nobody = self.bob.__class__.objects.create_user("carol")
        with INLINE:
            count = mail.send([self.ada, self.bob, nobody, self.admin], "Hello", "A line.")
        self.assertEqual(count, 2)
        self.assertEqual(
            sorted(m.to[0] for m in outbox.outbox), ["ada@example.test", "root@example.test"]
        )
        self.assertTrue(all(len(m.to) == 1 and not m.cc and not m.bcc for m in outbox.outbox))

    @override_settings(
        MAILERS={"default": {"BACKEND": "django.core.mail.backends.dummy.EmailBackend"}}
    )
    def test_without_a_mail_server_nothing_is_sent_and_nothing_fails(self):
        self.assertFalse(mail.configured())
        with mock.patch("desk.mail._dispatch") as dispatch:
            self.assertEqual(mail.send([self.ada], "Hello", "A line."), 0)
        dispatch.assert_not_called()

    def test_a_mail_server_that_fails_is_a_log_line_not_an_error(self):
        with (
            mock.patch("desk.mail.mailers") as mailers,
            self.assertLogs("desk.mail", "WARNING"),
        ):
            mailers.default.send_messages.side_effect = OSError("no route")
            self.assertEqual(mail.deliver([object()]), 0)
