"""Telling the owner's bot. Nothing here touches the network: the one function that does
(`_post`) is replaced, or handed a stand-in for the connection."""

from unittest import mock

from django.apps import apps
from django.core.cache import caches
from django.test import SimpleTestCase, override_settings

from desk import notify

BOT = override_settings(BMO_NOTIFY_URL="https://bot.example.test/hook", BMO_NOTIFY_TOKEN="s3cret")


class ConfiguredTests(SimpleTestCase):
    def test_without_the_address_or_the_token_nothing_is_sent(self):
        for url, token in (("", ""), ("https://bot.example.test/hook", ""), ("", "s3cret")):
            with (
                self.subTest(url=url, token=token),
                override_settings(BMO_NOTIFY_URL=url, BMO_NOTIFY_TOKEN=token),
                mock.patch("desk.notify._dispatch") as dispatch,
            ):
                self.assertFalse(notify.notify("Something arrived"))
                dispatch.assert_not_called()

    def test_the_token_is_never_sent_over_plain_http(self):
        with (
            override_settings(BMO_NOTIFY_URL="http://bot.example.test/hook", BMO_NOTIFY_TOKEN="s"),
            mock.patch("desk.notify._dispatch") as dispatch,
        ):
            self.assertFalse(notify.configured())
            self.assertFalse(notify.notify("Something arrived"))
            dispatch.assert_not_called()


class StartUpTests(SimpleTestCase):
    """A server without the bot's settings says so when it starts, and only then."""

    def ready(self, argv):
        with mock.patch("desk.apps.sys.argv", argv), override_settings(DEBUG=False, TESTING=False):
            apps.get_app_config("desk").ready()

    @override_settings(BMO_NOTIFY_URL="", BMO_NOTIFY_TOKEN="")
    def test_the_server_warns_and_a_management_command_does_not(self):
        with self.assertLogs("desk.apps", "WARNING") as logs:
            self.ready(["/usr/local/bin/gunicorn", "config.wsgi:application"])
        self.assertIn("nobody is notified", logs.output[0])
        with self.assertNoLogs("desk.apps", "WARNING"):
            self.ready(["manage.py", "migrate"])

    @BOT
    def test_with_the_settings_there_is_nothing_to_say(self):
        with self.assertNoLogs("desk.apps", "WARNING"):
            self.ready(["/usr/local/bin/gunicorn", "config.wsgi:application"])


@BOT
class NotifyTests(SimpleTestCase):
    def setUp(self):
        caches["limits"].clear()

    def test_the_message_has_the_shape_the_bot_expects(self):
        with mock.patch("desk.notify._dispatch") as dispatch:
            sent = notify.notify(
                "T" * 300, "M" * 3000, level="warning", url="https://x.test/a", dedupe_key="k" * 300
            )
        self.assertTrue(sent)
        (payload,) = dispatch.call_args.args
        self.assertEqual(payload["source"], "DSAI Vault")
        self.assertEqual(payload["level"], "warning")
        self.assertEqual(payload["url"], "https://x.test/a")
        self.assertEqual(
            (len(payload["title"]), len(payload["message"]), len(payload["dedupe_key"])),
            (120, 2000, 100),
        )
        self.assertNotIn("silent", payload)

    def test_a_burst_rings_once(self):
        with mock.patch("desk.notify._dispatch") as dispatch:
            for number in range(3):
                notify.notify(f"Request {number}")
        first, second, third = (call.args[0] for call in dispatch.call_args_list)
        self.assertNotIn("silent", first)
        self.assertTrue(second["silent"] and third["silent"])
        # Once it has been quiet for a while, the next one rings again.
        caches["limits"].delete("bmo:rang")
        with mock.patch("desk.notify._dispatch") as dispatch:
            notify.notify("Later")
        self.assertNotIn("silent", dispatch.call_args.args[0])

    def test_what_is_empty_is_left_out(self):
        with mock.patch("desk.notify._dispatch") as dispatch:
            notify.notify("Only a title")
        self.assertEqual(
            dispatch.call_args.args[0],
            {"title": "Only a title", "level": "info", "source": "DSAI Vault"},
        )

    def test_a_burst_stops_below_the_bots_own_limit(self):
        with mock.patch("desk.notify._dispatch") as dispatch, self.assertLogs("desk.notify"):
            results = [notify.notify(f"Request {number}") for number in range(notify.PER_HOUR + 5)]
        self.assertEqual(results.count(True), notify.PER_HOUR)
        self.assertEqual(dispatch.call_count, notify.PER_HOUR)
        self.assertLess(notify.PER_HOUR, 30)

    def test_it_is_handed_to_a_thread_and_does_not_wait(self):
        with mock.patch("desk.notify.threading.Thread") as thread:
            notify.notify("Something arrived")
        self.assertTrue(thread.call_args.kwargs["daemon"])
        self.assertIs(thread.call_args.kwargs["target"], notify.deliver)
        thread.return_value.start.assert_called_once()


@BOT
class DeliverTests(SimpleTestCase):
    """One try, then at most two more, and only when another try could help."""

    def deliver(self, *answers):
        waits = []
        with mock.patch("desk.notify._post", side_effect=answers) as post:
            delivered = notify.deliver({"title": "x"}, sleep=waits.append)
        return delivered, post.call_count, waits

    def test_accepted_at_once(self):
        self.assertEqual(self.deliver(200), (True, 1, []))

    def test_a_failure_that_may_pass_is_tried_again_with_a_pause(self):
        self.assertEqual(self.deliver(None, 502, 200), (True, 3, [2, 6]))
        self.assertEqual(self.deliver(503, 200), (True, 2, [2]))

    def test_it_gives_up_after_three_tries(self):
        with self.assertLogs("desk.notify", "WARNING"):
            self.assertEqual(self.deliver(None, None, None), (False, 3, [2, 6]))

    def test_a_refusal_is_final(self):
        for status in (400, 403, 429):
            with self.subTest(status=status), self.assertLogs("desk.notify", "WARNING") as logs:
                self.assertEqual(self.deliver(status), (False, 1, []))
                self.assertNotIn("s3cret", " ".join(logs.output))

    def test_the_same_body_is_sent_each_time_so_the_bot_can_drop_a_repeat(self):
        with mock.patch("desk.notify._post", side_effect=[502, 200]) as post:
            notify.deliver({"title": "x", "dedupe_key": "dsai-request-1"}, sleep=lambda _: None)
        first, second = (call.args[0] for call in post.call_args_list)
        self.assertEqual(first, second)
        self.assertIn(b"dsai-request-1", first)

    def test_the_request_carries_the_token_in_a_header_and_has_a_time_limit(self):
        answer = mock.MagicMock()
        answer.__enter__.return_value.status = 200
        with mock.patch("desk.notify.urllib.request.urlopen", return_value=answer) as urlopen:
            self.assertEqual(notify._post(b"{}"), 200)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://bot.example.test/hook")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("X-bmo-token"), "s3cret")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 5)

    def test_no_answer_is_not_an_error_for_the_caller(self):
        for failure in (TimeoutError(), OSError("down")):
            with (
                self.subTest(failure=failure),
                mock.patch("desk.notify.urllib.request.urlopen", side_effect=failure),
            ):
                self.assertIsNone(notify._post(b"{}"))
