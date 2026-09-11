"""
Unit tests for coldroom/safety_view.py (and safety.check_co2_safe).

The view module is pure formatting — no Qt, no hardware — so these tests only
need dicts. What they protect is the promise the module exists for: every check
appears exactly once, with its verdict in its own column, and nothing that
already has a row is repeated as prose underneath.
"""

import logging
import unittest

logging.getLogger("coldroom.safety").setLevel(logging.CRITICAL)

from coldroom.safety import check_co2_safe, check_door_safe_to_open
from coldroom.safety_view import (
    co2_row,
    interlock_notes,
    interlock_rows,
    make_row,
    render_door_safety,
    render_safety_table,
    render_soft_interlock,
)

import datetime


def _recent_ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


USED = {"LV": ["LV0.1"], "HV": ["HV0.1"]}


def _safe_conditions(**over):
    conditions = {
        "lv_on": False,
        "hv_on": False,
        "marta_ot": True,
        "marta_it": True,
        "marta_ot_reason": "MARTA CO2 running and OT valve is open (outer='open' (open))",
        "marta_it_reason": "MARTA CO2 running and IT valve is open (pixel='open' (open))",
        "ot_valve": True,
        "it_valve": True,
        "ot_valve_reason": "outer='open' (open)",
        "it_valve_reason": "pixel='open' (open)",
        "lv_safe_to_on": True,
        "lv_safe_reason": "MARTA safe: True (MARTA status OK)\n",
        "enforce_it_valve": False,
        "scope_lv": [],
        "scope_hv": [],
        "scope_empty": True,
        "pending_count": 0,
        "confirm_checks": 2,
    }
    conditions.update(over)
    return conditions


def _states(rows):
    return {row["name"]: row["state"] for row in rows}


def _levels(rows):
    return {row["name"]: row["level"] for row in rows}


# ---------------------------------------------------------------------------
# render_safety_table
# ---------------------------------------------------------------------------


class TestRenderSafetyTable(unittest.TestCase):
    def test_headline_and_one_row_per_check(self):
        html = render_safety_table(
            "DO NOT OPEN",
            "bad",
            [make_row("Dew point", "NO", "bad", "too cold"), make_row("HV", "YES", "ok")],
        )
        self.assertIn("DO NOT OPEN", html)
        # header row + 2 check rows
        self.assertEqual(html.count("<tr>"), 3)
        self.assertIn("Dew point", html)
        self.assertIn("too cold", html)

    def test_level_colours_the_state_cell(self):
        html = render_safety_table("x", "ok", [make_row("A", "NO", "bad")])
        self.assertIn("#c0362c", html)  # bad → red

    def test_detail_newlines_are_collapsed(self):
        html = render_safety_table(
            "x", "ok", [make_row("A", "YES", "ok", "line one\nline two\n")]
        )
        self.assertIn("line one line two", html)
        self.assertNotIn("\n", html.split("<table")[1])

    def test_no_rows_renders_headline_only(self):
        html = render_safety_table("just the verdict", "warn", [])
        self.assertIn("just the verdict", html)
        self.assertNotIn("<table", html)

    def test_notes_are_rendered_after_the_table(self):
        html = render_safety_table("v", "ok", [make_row("A", "YES", "ok")], ["a note"])
        self.assertLess(html.index("</table>"), html.index("a note"))

    def test_markup_in_values_is_escaped(self):
        html = render_safety_table("v", "ok", [make_row("<b>x</b>", "YES", "ok")])
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", html)


# ---------------------------------------------------------------------------
# Door table
# ---------------------------------------------------------------------------


class TestDoorRows(unittest.TestCase):
    def _status(self, min_temp=-5.0, dew_point=-10.0):
        return {
            "coldroom": {"ch_temperature": {"value": min_temp}},
            "marta": {"TT05_CO2": min_temp, "TT06_CO2": min_temp},
            "cleanroom": {"dewpoint": dew_point, "last_update": _recent_ts()},
        }

    def test_checks_out_collects_dew_point_and_hv_rows(self):
        rows = []
        is_safe, _ = check_door_safe_to_open(
            self._status(), {"caen_HV0.1_IsOn": False}, USED, checks_out=rows
        )
        self.assertTrue(is_safe)
        self.assertEqual(_states(rows), {"Dew point": "YES", "High voltage off": "YES"})

    def test_failing_check_is_flagged_bad_with_the_numbers(self):
        rows = []
        check_door_safe_to_open(
            self._status(min_temp=-10.0), {"caen_HV0.1_IsOn": False}, USED, checks_out=rows
        )
        dew = [r for r in rows if r["name"] == "Dew point"][0]
        self.assertEqual((dew["state"], dew["level"]), ("NO", "bad"))
        self.assertIn("-10.0", dew["detail"])

    def test_hv_on_row_names_the_channel(self):
        rows = []
        check_door_safe_to_open(
            self._status(), {"caen_HV0.1_IsOn": True}, USED, checks_out=rows
        )
        hv = [r for r in rows if r["name"] == "High voltage off"][0]
        self.assertEqual(hv["state"], "NO")
        self.assertIn("HV0.1", hv["detail"])

    def test_missing_coldroom_data_still_yields_a_row(self):
        rows = []
        is_safe, _ = check_door_safe_to_open({}, {}, USED, checks_out=rows)
        self.assertFalse(is_safe)
        self.assertEqual(_states(rows), {"Coldroom data": "MISSING"})

    def test_prose_message_is_unchanged_by_checks_out(self):
        """The log/journal text must not depend on the GUI asking for rows."""
        with_rows = check_door_safe_to_open(
            self._status(), {}, USED, checks_out=[]
        )
        without = check_door_safe_to_open(self._status(), {}, USED)
        self.assertEqual(with_rows, without)

    def test_render_door_safety_is_green_when_safe(self):
        html = render_door_safety(True, "SAFE TO OPEN", [make_row("A", "YES", "ok")])
        self.assertIn("#1a7f37", html)
        self.assertIn("SAFE TO OPEN", html)


class TestCO2Check(unittest.TestCase):
    def test_below_threshold_is_safe(self):
        safe, detail = check_co2_safe({"co2_sensor": {"CO2": 523}})
        self.assertTrue(safe)
        self.assertIn("523", detail)

    def test_above_threshold_is_unsafe(self):
        safe, detail = check_co2_safe({"co2_sensor": {"CO2": 1200}})
        self.assertFalse(safe)
        self.assertIn("oxygen", detail)

    def test_no_sensor_is_unknown_not_unsafe(self):
        safe, detail = check_co2_safe({})
        self.assertIsNone(safe)
        self.assertIn("not available", detail)

    def test_sensor_without_reading_is_unknown(self):
        safe, _ = check_co2_safe({"co2_sensor": {"temperature": 20}})
        self.assertIsNone(safe)

    def test_unreadable_value_is_unknown(self):
        safe, _ = check_co2_safe({"co2_sensor": {"CO2": "n/a"}})
        self.assertIsNone(safe)

    def test_unknown_row_is_warn_not_bad(self):
        row = co2_row(*check_co2_safe({}))
        self.assertEqual((row["state"], row["level"]), ("UNKNOWN", "warn"))


# ---------------------------------------------------------------------------
# Interlock table
# ---------------------------------------------------------------------------


class TestInterlockRows(unittest.TestCase):
    def test_no_snapshot_yields_no_rows(self):
        self.assertEqual(interlock_rows(None), [])
        self.assertEqual(interlock_rows({}), [])

    def test_every_condition_gets_exactly_one_row(self):
        rows = interlock_rows(_safe_conditions())
        self.assertEqual(
            [r["name"] for r in rows],
            [
                "LV power",
                "HV power",
                "MARTA OT cooling",
                "MARTA IT cooling",
                "LV safe to turn on",
                "Cable-I1 scope",
            ],
        )

    def test_power_and_cooling_states(self):
        rows = interlock_rows(_safe_conditions(lv_on=True, hv_on=False))
        states = _states(rows)
        self.assertEqual(states["LV power"], "ON")
        self.assertEqual(states["HV power"], "OFF")
        self.assertEqual(states["MARTA OT cooling"], "RUNNING")

    def test_running_cooling_detail_drops_the_repeated_reason(self):
        rows = interlock_rows(_safe_conditions())
        detail = {r["name"]: r["detail"] for r in rows}["MARTA IT cooling"]
        self.assertEqual(detail, "CO2 flowing, IT valve open")

    def test_closed_valve_detail_is_short(self):
        rows = interlock_rows(
            _safe_conditions(
                marta_ot=False,
                ot_valve=False,
                marta_ot_reason="OT valve is closed (outer='closed' (closed))",
            )
        )
        detail = {r["name"]: r["detail"] for r in rows}["MARTA OT cooling"]
        self.assertEqual(detail, "OT valve closed")

    def test_unknown_valve_is_reported_in_the_detail(self):
        rows = interlock_rows(_safe_conditions(ot_valve=None, ot_valve_reason="no serviceroom data"))
        detail = {r["name"]: r["detail"] for r in rows}["MARTA OT cooling"]
        self.assertIn("UNKNOWN", detail)
        self.assertIn("no serviceroom data", detail)

    def test_stopped_cooling_is_red_only_when_power_is_on(self):
        off = interlock_rows(_safe_conditions(marta_ot=False, lv_on=False, hv_on=False))
        self.assertEqual(_levels(off)["MARTA OT cooling"], "warn")
        on = interlock_rows(_safe_conditions(marta_ot=False, lv_on=True))
        self.assertEqual(_levels(on)["MARTA OT cooling"], "bad")

    def test_it_row_says_it_is_not_enforced(self):
        rows = interlock_rows(_safe_conditions(marta_it=False, lv_on=True))
        it = {r["name"]: r for r in rows}["MARTA IT cooling"]
        self.assertIn("not enforced", it["detail"])
        self.assertEqual(it["level"], "warn")  # cannot trip → not an alarm

    def test_enforced_it_row_is_an_alarm_when_power_is_on(self):
        rows = interlock_rows(
            _safe_conditions(marta_it=False, lv_on=True, enforce_it_valve=True)
        )
        it = {r["name"]: r for r in rows}["MARTA IT cooling"]
        self.assertNotIn("not enforced", it["detail"])
        self.assertEqual(it["level"], "bad")

    def test_empty_scope_says_nothing_to_protect(self):
        rows = interlock_rows(_safe_conditions())
        scope = {r["name"]: r for r in rows}["Cable-I1 scope"]
        self.assertEqual(scope["state"], "EMPTY")
        self.assertIn("nothing to protect", scope["detail"])

    def test_populated_scope_lists_the_channels(self):
        rows = interlock_rows(
            _safe_conditions(scope_lv=["LV0.1"], scope_hv=["HV0.1"], scope_empty=False)
        )
        scope = {r["name"]: r for r in rows}["Cable-I1 scope"]
        self.assertEqual(scope["state"], "2 ch")
        self.assertIn("HV0.1", scope["detail"])
        self.assertIn("LV0.1", scope["detail"])

    def test_lv_safe_row_only_explains_itself_when_it_fails(self):
        ok = interlock_rows(_safe_conditions())
        self.assertEqual({r["name"]: r for r in ok}["LV safe to turn on"]["detail"], "")
        bad = interlock_rows(
            _safe_conditions(
                lv_safe_to_on=False,
                lv_safe_reason="MARTA safe: False (MARTA is disconnected)\n",
            )
        )
        row = {r["name"]: r for r in bad}["LV safe to turn on"]
        self.assertEqual((row["state"], row["level"]), ("NO", "bad"))
        self.assertIn("disconnected", row["detail"])

    def test_missing_lv_safe_field_drops_the_row(self):
        conditions = _safe_conditions()
        conditions.pop("lv_safe_to_on")
        names = [r["name"] for r in interlock_rows(conditions)]
        self.assertNotIn("LV safe to turn on", names)


class TestInterlockNotes(unittest.TestCase):
    def test_safe_cycle_has_no_notes(self):
        self.assertEqual(interlock_notes(_safe_conditions()), [])

    def test_pending_countdown_is_reported(self):
        notes = interlock_notes(_safe_conditions(pending_count=1, confirm_checks=2))
        self.assertEqual(len(notes), 1)
        self.assertIn("1/2", notes[0])

    def test_countdown_is_dropped_when_the_alarm_already_states_it(self):
        notes = interlock_notes(
            _safe_conditions(pending_count=1, confirm_checks=2),
            alarm="SAFETY WARNING (unconfirmed 1/2): ...",
        )
        self.assertEqual(notes, ["SAFETY WARNING (unconfirmed 1/2): ..."])

    def test_trip_comes_before_the_alarm_text(self):
        notes = interlock_notes(
            _safe_conditions(),
            trip_description="Trip #1 at 10:00: reason.",
            latch_origin=" Raised by another instance.",
            alarm="SAFETY INTERLOCK: ...",
        )
        self.assertEqual(
            notes, ["Trip #1 at 10:00: reason. Raised by another instance.", "SAFETY INTERLOCK: ..."]
        )

    def test_notes_survive_a_missing_snapshot(self):
        self.assertEqual(interlock_notes(None, alarm="boom"), ["boom"])


class TestRenderSoftInterlock(unittest.TestCase):
    def test_tripped_is_red_latched_is_amber_ok_is_green(self):
        rows = [make_row("A", "OFF", "info")]
        self.assertIn("#c0362c", render_soft_interlock(False, False, "v", rows))
        self.assertIn("#b26a00", render_soft_interlock(True, True, "v", rows))
        self.assertIn("#1a7f37", render_soft_interlock(True, False, "v", rows))


if __name__ == "__main__":
    unittest.main()
