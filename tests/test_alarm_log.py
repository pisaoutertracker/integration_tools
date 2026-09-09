"""Tests for the shared alarm journal and cross-instance trip latch.

The point of `coldroom/alarm_log.py` is behaviour ACROSS processes, so the
important cases here use two independent AlarmLog objects (and, in one case, a
genuinely separate OS process) pointed at the same directory.
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coldroom.alarm_log import AlarmLog, default_log_dir


def _read_journal(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


class _TmpDirCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="alarmlog_test_")
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def make(self, **kw):
        kw.setdefault("heartbeat_every", 0)
        return AlarmLog(log_dir=self.dir, **kw)


class TestJournal(_TmpDirCase):
    def test_log_writes_one_json_line_with_provenance(self):
        log = self.make()
        log.log("trip", "cut power", conditions={"fsm_state": "DISCONNECTED"})

        records = _read_journal(log.journal_path)
        self.assertEqual(len(records), 1)
        rec = records[0]
        self.assertEqual(rec["event"], "trip")
        self.assertEqual(rec["message"], "cut power")
        self.assertEqual(rec["conditions"]["fsm_state"], "DISCONNECTED")
        # host+pid are what let duplicate Slack alarms be attributed later.
        self.assertEqual(rec["pid"], os.getpid())
        self.assertIn("host", rec)
        self.assertIn("ts", rec)

    def test_appends_do_not_overwrite(self):
        log = self.make()
        for i in range(5):
            log.log("alarm_published", f"msg {i}")
        self.assertEqual(len(_read_journal(log.journal_path)), 5)

    def test_two_instances_append_to_the_same_journal(self):
        a, b = self.make(), self.make()
        a.log("startup", "A up")
        b.log("startup", "B up")
        a.log("alarm_published", "from A")

        records = _read_journal(a.journal_path)
        self.assertEqual(len(records), 3)
        self.assertEqual([r["message"] for r in records], ["A up", "B up", "from A"])

    def test_extra_kwargs_are_stored(self):
        log = self.make()
        log.log("ack", "acknowledged", trip_id="abc123", acknowledged_by="operator")
        rec = _read_journal(log.journal_path)[0]
        self.assertEqual(rec["trip_id"], "abc123")
        self.assertEqual(rec["acknowledged_by"], "operator")


class TestLogCycle(_TmpDirCase):
    def test_unchanged_cycles_are_not_journalled(self):
        log = self.make()
        cond = {"fsm_state": "CO2_RUNNING", "lv_on": True}
        log.log_cycle(cond)
        for _ in range(10):
            log.log_cycle(dict(cond))
        # Only the first cycle is a change; the rest are silent.
        self.assertEqual(len(_read_journal(log.journal_path)), 1)

    def test_changed_condition_is_journalled(self):
        log = self.make()
        log.log_cycle({"fsm_state": "CO2_RUNNING"})
        log.log_cycle({"fsm_state": "DISCONNECTED"})

        records = _read_journal(log.journal_path)
        self.assertEqual(len(records), 2)
        # This transition is precisely what was invisible before: the moment
        # MARTA's state flipped, recorded before any alarm fired.
        self.assertEqual(records[1]["conditions"]["fsm_state"], "DISCONNECTED")
        self.assertEqual(records[1]["event"], "condition_change")

    def test_non_watched_field_change_does_not_spam(self):
        log = self.make()
        log.log_cycle({"fsm_state": "CO2_RUNNING", "marta_msg_age_s": 1.0})
        log.log_cycle({"fsm_state": "CO2_RUNNING", "marta_msg_age_s": 6.0})
        self.assertEqual(len(_read_journal(log.journal_path)), 1)

    def test_heartbeat_records_liveness(self):
        log = self.make(heartbeat_every=3)
        cond = {"fsm_state": "CO2_RUNNING"}
        for _ in range(7):
            log.log_cycle(dict(cond))
        records = _read_journal(log.journal_path)
        events = [r["event"] for r in records]
        self.assertEqual(events[0], "condition_change")
        self.assertIn("heartbeat", events)


class TestSharedLatch(_TmpDirCase):
    def test_no_latch_initially(self):
        self.assertIsNone(self.make().read_latch())

    def test_trip_in_one_instance_is_visible_in_another(self):
        """The core fix: instance B must see a trip raised by instance A."""
        a, b = self.make(), self.make()
        self.assertIsNone(b.read_latch())

        a.record_trip("SAFETY INTERLOCK: cut power", conditions={"fsm_state": "DISCONNECTED"})

        latch = b.read_latch()
        self.assertIsNotNone(latch)
        self.assertEqual(latch["message"], "SAFETY INTERLOCK: cut power")
        self.assertEqual(latch["conditions"]["fsm_state"], "DISCONNECTED")

    def test_ack_in_one_instance_clears_it_for_another(self):
        """One acknowledgement must clear the trip everywhere."""
        a, b = self.make(), self.make()
        a.record_trip("SAFETY INTERLOCK: cut power")
        self.assertIsNotNone(b.read_latch())

        b.clear_latch(operator="tester")

        self.assertIsNone(a.read_latch())
        self.assertIsNone(b.read_latch())

    def test_ack_is_journalled_with_the_original_trip_details(self):
        a, b = self.make(), self.make()
        trip = a.record_trip("SAFETY INTERLOCK: cut power")
        b.clear_latch(operator="tester")

        acks = [r for r in _read_journal(a.journal_path) if r["event"] == "ack"]
        self.assertEqual(len(acks), 1)
        self.assertEqual(acks[0]["trip_id"], trip["trip_id"])
        self.assertEqual(acks[0]["acknowledged_by"], "tester")
        # The ack is attributed to the process that made it, not the one that tripped.
        self.assertEqual(acks[0]["pid"], os.getpid())

    def test_repeat_trip_keeps_the_original_record(self):
        a = self.make()
        first = a.record_trip("first trip")
        second = a.record_trip("second trip")

        self.assertEqual(second["trip_id"], first["trip_id"])
        self.assertEqual(second["ts"], first["ts"])
        self.assertEqual(second["message"], "first trip")
        self.assertEqual(second["repeat_count"], 2)
        self.assertIn("last_trip_ts", second)

    def test_latch_survives_a_new_instance(self):
        """Restarting must not silently erase an unacknowledged trip."""
        self.make().record_trip("SAFETY INTERLOCK: cut power")
        self.assertIsNotNone(self.make().read_latch())

    def test_latch_file_is_valid_json(self):
        a = self.make()
        a.record_trip("SAFETY INTERLOCK: cut power", conditions={"lv_on": True})
        with open(a.latch_path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["conditions"]["lv_on"], True)


class TestSeparateProcesses(_TmpDirCase):
    def test_latch_crosses_a_real_process_boundary(self):
        """Same as the shared-latch test, but with a genuinely separate process."""
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script = (
            "import sys; sys.path.insert(0, %r)\n"
            "from coldroom.alarm_log import AlarmLog\n"
            "AlarmLog(log_dir=%r, heartbeat_every=0)"
            ".record_trip('trip from a separate process')\n" % (repo, self.dir)
        )
        subprocess.run([sys.executable, "-c", script], check=True, timeout=30)

        latch = self.make().read_latch()
        self.assertIsNotNone(latch)
        self.assertEqual(latch["message"], "trip from a separate process")
        # Raised by a different OS process, which is what the UI reports.
        self.assertNotEqual(latch["pid"], os.getpid())


class TestRobustness(_TmpDirCase):
    def test_rotation_keeps_one_previous_generation(self):
        log = self.make(max_bytes=500)
        for i in range(60):
            log.log("alarm_published", f"padding message number {i} " + "x" * 40)
        self.assertTrue(os.path.exists(log.journal_path + ".1"))
        self.assertLess(os.path.getsize(log.journal_path), 2000)

    def test_unwritable_directory_never_raises(self):
        """A broken journal must not be able to break the interlock."""
        log = AlarmLog(log_dir="/proc/nonexistent/cannot/create", heartbeat_every=0)
        log.log("trip", "should not raise")
        log.log_cycle({"fsm_state": "DISCONNECTED"})
        self.assertIsNone(log.read_latch())
        # clear_latch on a broken path is also survivable
        self.assertIsNone(log.clear_latch())

    def test_corrupt_latch_reads_as_no_latch(self):
        log = self.make()
        with open(log.latch_path, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        self.assertIsNone(log.read_latch())

    def test_default_log_dir_honours_xdg(self):
        old = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = "/tmp/xdg_test_state"
        try:
            self.assertEqual(
                default_log_dir(), "/tmp/xdg_test_state/coldroom_interlock"
            )
        finally:
            if old is None:
                del os.environ["XDG_STATE_HOME"]
            else:
                os.environ["XDG_STATE_HOME"] = old


if __name__ == "__main__":
    unittest.main()
