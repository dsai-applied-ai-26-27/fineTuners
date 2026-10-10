"""The rules that bring two copies of someone's progress together.

Each test plays one or two devices against `sync()` directly. A "device" here is nothing
but the cursor it remembers and what it sends.
"""

import json
import time

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from progress.models import Attempt, Clear, Day, Ledger, Record
from progress.sync import sync

NOW = int(time.time() * 1000)
HOUR = 3_600_000


def rec(s, t, k=0, n=1):
    return {"s": s, "t": t, "k": k, "n": n}


class SyncTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("ada")

    def push(self, cursor=0, **sections):
        return sync(self.user, {"cursor": cursor, **sections})

    # -- records ---------------------------------------------------------------------------

    def test_a_first_sync_stores_what_the_device_has(self):
        answer = self.push(records={"mlpr/fisher-01": rec(3, NOW - HOUR, k=2, n=5)})
        row = Record.objects.get()
        self.assertEqual(
            (row.course, row.key, row.state, row.streak, row.count),
            ("mlpr", "fisher-01", 3, 2, 5),
        )
        self.assertEqual(answer["cursor"], 1)
        self.assertEqual(Ledger.objects.get(user=self.user).version, 1)

    def test_another_device_receives_it(self):
        self.push(records={"mlpr/fisher-01": rec(3, NOW - HOUR)})
        answer = self.push(cursor=0)  # a device that has never synced
        self.assertEqual(answer["records"]["mlpr/fisher-01"]["s"], 3)
        self.assertEqual(self.push(cursor=answer["cursor"])["records"], {})  # nothing new now

    def test_the_grade_made_later_wins_whichever_arrives_first(self):
        self.push(records={"mlpr/a": rec(3, NOW - HOUR)})
        self.push(records={"mlpr/a": rec(1, NOW - 2 * HOUR)})  # older, arriving late
        self.assertEqual(Record.objects.get().state, 3)
        self.push(records={"mlpr/a": rec(2, NOW - 60_000)})  # newer
        self.assertEqual(Record.objects.get().state, 2)

    def test_sending_the_same_thing_twice_changes_nothing(self):
        first = self.push(records={"mlpr/a": rec(3, NOW - HOUR)})
        again = self.push(cursor=first["cursor"], records={"mlpr/a": rec(3, NOW - HOUR)})
        self.assertEqual(again["cursor"], first["cursor"])
        self.assertEqual(Record.objects.count(), 1)

    def test_a_cleared_grade_travels_as_a_record_too(self):
        self.push(records={"mlpr/a": rec(3, NOW - HOUR)})
        self.push(records={"mlpr/a": rec(0, NOW - 60_000, n=1)})
        self.assertEqual(Record.objects.get().state, 0)

    def test_a_clock_in_the_future_is_pulled_back_to_now(self):
        """Otherwise one wrong clock would win every comparison for years."""
        self.push(records={"mlpr/a": rec(3, NOW + 400 * 24 * HOUR)})
        self.assertLess(Record.objects.get().graded_at, NOW + HOUR)

    def test_many_records_take_a_fixed_number_of_queries(self):
        # One SELECT and one INSERT for all 300; the rest is the ledger, the clears and
        # the four queries that build the answer.
        records = {f"mlpr/card-{i}": rec(3, NOW - HOUR) for i in range(300)}
        with self.assertNumQueries(14):
            self.push(records=records)
        self.assertEqual(Record.objects.count(), 300)

    # -- attempts and activity ---------------------------------------------------------------

    def test_attempts_are_added_once(self):
        sitting = {"score": 11, "max": 15, "seconds": 1800, "t": NOW - HOUR}
        self.push(attempts={"mlpr/final-mock-1": [sitting]})
        self.push(attempts={"mlpr/final-mock-1": [sitting, {**sitting, "t": NOW - 60_000}]})
        self.assertEqual(Attempt.objects.count(), 2)
        answer = self.push(cursor=0)
        self.assertEqual([a["score"] for a in answer["attempts"]["mlpr/final-mock-1"]], [11, 11])

    def test_the_same_day_on_two_devices_keeps_the_larger_count(self):
        self.push(activity={"2026-10-09": {"cards": 12, "minutes": 25}})
        self.push(activity={"2026-10-09": {"cards": 7, "minutes": 50}})
        day = Day.objects.get()
        self.assertEqual((day.cards, day.minutes), (12, 50))

    # -- clears --------------------------------------------------------------------------------

    def test_clearing_a_course_removes_what_is_older_and_only_that(self):
        self.push(
            records={"mlpr/a": rec(3, NOW - 2 * HOUR), "rl/b": rec(3, NOW - 2 * HOUR)},
            attempts={"mlpr/mock": [{"score": 1, "max": 2, "t": NOW - 2 * HOUR}]},
        )
        self.push(clears={"mlpr": NOW - HOUR}, records={"mlpr/c": rec(2, NOW - 60_000)})
        self.assertEqual(
            sorted(Record.objects.values_list("course", "key")), [("mlpr", "c"), ("rl", "b")]
        )
        self.assertFalse(Attempt.objects.exists())

    def test_a_device_that_missed_the_clear_cannot_bring_the_old_grades_back(self):
        self.push(records={"mlpr/a": rec(3, NOW - 2 * HOUR)})
        self.push(clears={"mlpr": NOW - HOUR})
        # The other device still holds the old record and offers it.
        answer = self.push(cursor=1, records={"mlpr/a": rec(3, NOW - 2 * HOUR)})
        self.assertFalse(Record.objects.exists())
        self.assertIn("mlpr", answer["clears"])  # and it is told to forget it

    def test_clearing_everything(self):
        self.push(
            records={"mlpr/a": rec(3, NOW - 2 * HOUR), "rl/b": rec(3, NOW - 2 * HOUR)},
            activity={"2026-10-01": {"cards": 5, "minutes": 0}},
        )
        self.push(clears={"*": NOW - HOUR})
        self.assertFalse(Record.objects.exists())
        self.assertFalse(Day.objects.exists())
        self.assertEqual(Clear.objects.get().scope, "*")

    def test_an_earlier_clear_does_not_replace_a_later_one(self):
        self.push(clears={"mlpr": NOW - HOUR})
        self.push(clears={"mlpr": NOW - 5 * HOUR})
        self.assertEqual(Clear.objects.get().cleared_at, NOW - HOUR)

    # -- robustness --------------------------------------------------------------------------

    def test_bad_entries_are_skipped_and_good_ones_kept(self):
        self.push(
            records={
                "mlpr/ok": rec(3, NOW - HOUR),
                "no-slash": rec(3, NOW - HOUR),
                "Bad Course/x": rec(3, NOW - HOUR),
                "mlpr/nine": {"s": 9, "t": NOW},
                "mlpr/text": "not a record",
                "mlpr/list": [1, 2],
            },
            attempts={"mlpr/mock": "nope"},
            activity={"yesterday": {"cards": 1}},
            clears={"Bad Scope": NOW, "mlpr": "soon"},
        )
        self.assertEqual(list(Record.objects.values_list("key", flat=True)), ["ok"])
        self.assertFalse(Clear.objects.exists() or Attempt.objects.exists() or Day.objects.exists())

    def test_a_rebuilt_database_asks_the_device_for_everything(self):
        answer = self.push(cursor=57)  # the server knows nothing of version 57
        self.assertTrue(answer["resync"])
        self.assertEqual(answer["cursor"], 0)

    def test_people_never_see_each_other(self):
        other = get_user_model().objects.create_user("bob")
        self.push(records={"mlpr/a": rec(3, NOW - HOUR)})
        self.assertEqual(sync(other, {"cursor": 0})["records"], {})
        sync(other, {"clears": {"*": NOW}})
        self.assertEqual(Record.objects.filter(user=self.user).count(), 1)


class SyncViewTests(TestCase):
    URL = "/api/progress/sync/"

    def setUp(self):
        self.user = get_user_model().objects.create_user("ada")

    def post(self, client, payload):
        return client.post(self.URL, json.dumps(payload), content_type="application/json")

    def test_signed_out_gets_a_plain_401_not_a_redirect(self):
        response = self.post(self.client, {})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_round_trip(self):
        self.client.force_login(self.user)
        response = self.post(self.client, {"records": {"mlpr/a": rec(2, NOW - HOUR)}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["records"]["mlpr/a"]["s"], 2)

    def test_only_post_and_only_json_objects(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.URL).status_code, 405)
        self.assertEqual(self.post(self.client, [1, 2]).status_code, 400)
        bad = self.client.post(self.URL, "{not json", content_type="application/json")
        self.assertEqual(bad.status_code, 400)

    def test_a_post_without_the_csrf_token_is_refused(self):
        """The test client normally skips this check; a browser never does."""
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.user)
        self.assertEqual(self.post(strict, {}).status_code, 403)
        self.assertFalse(Ledger.objects.exists())
