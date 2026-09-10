"""
Unit tests for coldroom/safety.py.

All tests use MagicMock CAEN and plain dicts for system_status / caen_ch_status
so no real hardware or MQTT broker is required.

Minimal "fully safe" system_status:
    {
        "marta":    {"fsm_state": "RUNNING", "status": 2},  # status 2 = CO2 flowing
        "coldroom": {},   # required guard key in Is_it_safe_to_on_lv
    }
Extend per-test to trigger the specific condition under test.
"""


"""
# All tests, grouped by class with progress
python -m pytest tests/test_safety.py -v

# Just a quick pass/fail summary (no names)
python -m pytest tests/test_safety.py
"""

import datetime
import logging
import inspect
import unittest
from unittest.mock import MagicMock, call

# Silence safety.py's logger during tests — the interlock messages are expected
# output of intentional test conditions, not real alarms.
logging.getLogger("coldroom.safety").setLevel(logging.CRITICAL)

from coldroom.safety import (
    acknowledge_trip,
    check_door_safe_to_open,
    check_marta_on_for_IT,
    check_marta_on_for_OT,
    describe_trip,
    get_cable_channels,
    get_valve_state,
    interpret_soft_interlock,
    is_trip_unacknowledged,
    parse_valve_value,
    restrict_to_cable_channels,
    soft_interlock_loop,
    switch_all_hv_off,
    switch_all_lv_off,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _safe_status():
    """Minimal system_status for a fully connected, safe system.

    CO2 must be flowing (marta status == 2) for the system to be considered
    safe — FSM RUNNING alone is not sufficient.
    """
    return {
        "marta": {"fsm_state": "CO2_RUNNING", "status": 2},
        "coldroom": {},
    }


def _make_caen():
    """MagicMock CAEN that records every .off() call without touching hardware."""
    caen = MagicMock()
    caen.off = MagicMock()
    return caen


def _all_off(lv=("LV0.1",), hv=("HV0.1",)):
    """caen_ch_status dict with every listed channel reported as OFF."""
    status = {}
    for ch in lv:
        status[f"caen_{ch}_IsOn"] = False
    for ch in hv:
        status[f"caen_{ch}_IsOn"] = False
    return status


def _recent_ts():
    """A last_update timestamp that is less than 10 minutes old."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _stale_ts():
    """A last_update timestamp that is more than 10 minutes old."""
    return (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


USED = {"LV": ["LV0.1"], "HV": ["HV0.1"]}
USED_MULTI = {"LV": ["LV0.1", "LV0.2"], "HV": ["HV0.1", "HV0.2"]}


# ---------------------------------------------------------------------------
# soft_interlock_loop
# ---------------------------------------------------------------------------

class TestSoftInterlock(unittest.TestCase):
    """5-second safety loop: monitors MARTA state and cuts power if cooling is lost."""

    # ---- Condition 1: MARTA is not safe (FSM state bad / no coldroom data) --

    def test_marta_disconnected_lv_on_triggers_shutdown(self):
        """Classic danger: cooling lost, LV still energised."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}
        published = []

        is_safe, msg = soft_interlock_loop(
            status, ch_status, USED, caen, published.append
        )

        self.assertFalse(is_safe)
        caen.off.assert_called()
        self.assertEqual(len(published), 1)
        self.assertIn("SAFETY INTERLOCK", published[0])

    def test_marta_disconnected_hv_only_on_triggers_shutdown(self):
        """HV alone being on is sufficient to trigger the interlock."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV0.1_IsOn": False, "caen_HV0.1_IsOn": True}

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen)

        self.assertFalse(is_safe)
        caen.off.assert_called()

    def test_marta_disconnected_all_power_off_no_action(self):
        """MARTA gone but everything already off — nothing to protect, no action."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = _all_off()

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen)

        caen.off.assert_not_called()
        self.assertTrue(is_safe)

    def test_marta_fsm_none_treated_as_disconnected(self):
        """FSM state 'NONE' is an offline indicator."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "NONE"}}
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen)

        self.assertFalse(is_safe)
        caen.off.assert_called()

    def test_marta_fsm_empty_string_treated_as_disconnected(self):
        """Empty FSM state means MARTA has not reported yet — assume offline."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": ""}}
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen)

        self.assertFalse(is_safe)
        caen.off.assert_called()

    def test_missing_coldroom_key_with_power_on_triggers_shutdown(self):
        """Is_it_safe_to_on_lv requires 'coldroom' to be present; without it → unsafe."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "RUNNING"}}  # no 'coldroom'
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen)

        self.assertFalse(is_safe)
        caen.off.assert_called()

    # ---- Condition 2: MARTA connected but OT CO2 not flowing ----------------

    def test_marta_running_ot_valve_closed_triggers_shutdown(self):
        """MARTA connected but serviceroom reports OT valve closed → cut power."""
        caen = _make_caen()
        status = {
            "marta": {"fsm_state": "CO2_RUNNING", "status": 2},
            "coldroom": {},
            "serviceroom": {"outer_valve": 0},
        }
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}

        is_safe, msg = soft_interlock_loop(status, ch_status, USED, caen)

        self.assertFalse(is_safe)
        caen.off.assert_called()
        self.assertIn("OT CO2", msg)

    def test_marta_running_ot_valve_open_is_safe(self):
        """Valve confirmed open → no protective action."""
        caen = _make_caen()
        status = {
            "marta": {"fsm_state": "CO2_RUNNING", "status": 2},
            "coldroom": {},
            "serviceroom": {"outer_valve": 1},
        }
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen)

        self.assertTrue(is_safe)
        caen.off.assert_not_called()

    def test_marta_running_no_serviceroom_falls_back_to_fsm(self):
        """Without serviceroom data, CO2_RUNNING + CO2 flowing is trusted for OT."""
        caen = _make_caen()
        status = _safe_status()  # no 'serviceroom' key
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen)

        self.assertTrue(is_safe)
        caen.off.assert_not_called()

    def test_ot_valve_closed_but_power_off_no_action(self):
        """OT CO2 not flowing, but all channels already off — nothing to cut."""
        caen = _make_caen()
        status = {
            "marta": {"fsm_state": "CO2_RUNNING", "status": 2},
            "coldroom": {},
            "serviceroom": {"outer_valve": 0},
        }
        ch_status = _all_off()

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen)

        self.assertTrue(is_safe)
        caen.off.assert_not_called()

    # ---- Fully safe baseline ------------------------------------------------

    def test_fully_safe_baseline_no_action(self):
        """MARTA running, OT confirmed via FSM, all power off → safe."""
        caen = _make_caen()
        is_safe, _ = soft_interlock_loop(_safe_status(), _all_off(), USED, caen)
        self.assertTrue(is_safe)
        caen.off.assert_not_called()

    # ---- HV/LV shutdown ordering — critical safety invariant ----------------

    def test_hv_cut_before_lv(self):
        """
        HV must be switched off BEFORE LV.
        Cutting LV first while HV is still ramped risks an uncontrolled
        discharge through the silicon sensors.
        """
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": True}

        soft_interlock_loop(status, ch_status, USED, caen)

        calls = caen.off.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], call("HV0.1"))
        self.assertEqual(calls[1], call("LV0.1"))

    def test_all_channels_shut_down_and_hv_first(self):
        """With multiple channels, every channel is cut and all HV calls precede all LV calls."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {
            "caen_LV0.1_IsOn": True, "caen_LV0.2_IsOn": True,
            "caen_HV0.1_IsOn": True, "caen_HV0.2_IsOn": True,
        }

        soft_interlock_loop(status, ch_status, USED_MULTI, caen)

        turned_off = [c.args[0] for c in caen.off.call_args_list]
        for ch in ("HV0.1", "HV0.2", "LV0.1", "LV0.2"):
            self.assertIn(ch, turned_off)

        hv_last = max(i for i, ch in enumerate(turned_off) if ch.startswith("HV"))
        lv_first = min(i for i, ch in enumerate(turned_off) if ch.startswith("LV"))
        self.assertLess(hv_last, lv_first, "All HV calls must precede all LV calls")

    # ---- Alarm publishing ---------------------------------------------------

    def test_alarm_published_exactly_once_per_trip(self):
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}
        published = []

        soft_interlock_loop(status, ch_status, USED, caen, published.append)

        self.assertEqual(len(published), 1)

    def test_publish_alarm_none_does_not_crash(self):
        """publish_alarm=None is the test/dry-run mode — must not raise."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}

        is_safe, _ = soft_interlock_loop(status, ch_status, USED, caen, publish_alarm=None)

        self.assertFalse(is_safe)

    def test_no_alarm_when_everything_safe(self):
        caen = _make_caen()
        published = []

        soft_interlock_loop(_safe_status(), _all_off(), USED, caen, published.append)

        self.assertEqual(len(published), 0)


# ---------------------------------------------------------------------------
# check_door_safe_to_open
# ---------------------------------------------------------------------------

class TestDoorSafety(unittest.TestCase):
    """Door can be opened only when dew point is safe AND HV is off."""

    def _door_safe_status(self, min_temp=-5.0, dew_point=-10.0):
        """
        Fully safe status for door-open check:
          min internal temp (-5 °C) comfortably above dew point (-10 °C) + 1 °C margin.
        """
        return {
            "coldroom": {"ch_temperature": {"value": min_temp}},
            "marta": {"TT05_CO2": min_temp, "TT06_CO2": min_temp},
            "cleanroom": {"dewpoint": dew_point, "last_update": _recent_ts()},
        }

    # ---- Missing data guards ------------------------------------------------

    def test_no_coldroom_key_returns_false(self):
        is_safe, msg = check_door_safe_to_open({}, {}, USED)
        self.assertFalse(is_safe)
        self.assertIn("coldroom", msg.lower())

    def test_no_cleanroom_last_update_treats_as_expired(self):
        status = {"coldroom": {}, "cleanroom": {"dewpoint": -10.0}}  # no last_update
        is_safe, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertFalse(is_safe)
        self.assertIn("expired", msg)

    def test_stale_cleanroom_data_blocks_door(self):
        status = {
            "coldroom": {},
            "cleanroom": {"dewpoint": -10.0, "last_update": _stale_ts()},
        }
        is_safe, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertFalse(is_safe)
        self.assertIn("expired", msg)

    def test_unparseable_timestamp_treated_as_expired(self):
        status = {
            "coldroom": {},
            "cleanroom": {"dewpoint": -10.0, "last_update": "not-a-date"},
        }
        is_safe, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertFalse(is_safe)
        self.assertIn("expired", msg)

    def test_no_internal_temps_blocks_door(self):
        """No MARTA or coldroom temperatures → cannot verify dew point."""
        status = {
            "coldroom": {},  # no ch_temperature
            "cleanroom": {"dewpoint": -10.0, "last_update": _recent_ts()},
        }
        is_safe, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertFalse(is_safe)
        self.assertIn("temperature", msg.lower())

    def test_no_dewpoint_reading_blocks_door(self):
        status = {
            "coldroom": {"ch_temperature": {"value": -5.0}},
            "marta": {"TT05_CO2": -5.0},
            "cleanroom": {"last_update": _recent_ts()},  # no "dewpoint" key
        }
        is_safe, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertFalse(is_safe)
        self.assertIn("dew point", msg.lower())

    # ---- Dew point logic ----------------------------------------------------

    def test_safe_when_temp_well_above_dew_point(self):
        """-5 °C internal > -10 °C dew + 1 °C margin (-9 °C) → safe."""
        status = self._door_safe_status(min_temp=-5.0, dew_point=-10.0)
        is_safe, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertTrue(is_safe)
        self.assertIn("YES", msg)

    def test_unsafe_when_temp_below_dew_point_plus_margin(self):
        """-10 °C internal ≤ -9 °C margin → condensation risk."""
        status = self._door_safe_status(min_temp=-10.0, dew_point=-10.0)
        is_safe, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertFalse(is_safe)
        self.assertIn("NO", msg)

    def test_exact_margin_boundary_is_unsafe(self):
        """Condition is strictly >; equal to margin means not safe."""
        # min_temp == dew_point + 1  →  -9 == -10 + 1  →  NOT strictly greater
        status = self._door_safe_status(min_temp=-9.0, dew_point=-10.0)
        is_safe, _ = check_door_safe_to_open(status, _all_off(), USED)
        self.assertFalse(is_safe)

    def test_dew_point_reason_includes_actual_temperatures(self):
        """Message must show the numeric values so operators know the actual margin."""
        status = self._door_safe_status(min_temp=-5.0, dew_point=-10.0)
        _, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertIn("-5.0", msg)
        self.assertIn("-10.0", msg)

    # ---- HV checks ----------------------------------------------------------

    def test_hv_on_blocks_door_and_lists_channel(self):
        status = self._door_safe_status()
        ch_status = {"caen_HV0.1_IsOn": True}
        is_safe, msg = check_door_safe_to_open(status, ch_status, USED)
        self.assertFalse(is_safe)
        self.assertIn("NO", msg)
        self.assertIn("HV0.1", msg)

    def test_hv_off_passes_hv_check(self):
        status = self._door_safe_status()
        is_safe, msg = check_door_safe_to_open(status, _all_off(), USED)
        self.assertTrue(is_safe)
        self.assertIn("all HV channels are off", msg)

    def test_multiple_hv_channels_one_on_blocks_and_names_it(self):
        status = self._door_safe_status()
        ch_status = {"caen_HV0.1_IsOn": False, "caen_HV0.2_IsOn": True}
        used = {"LV": ["LV0.1"], "HV": ["HV0.1", "HV0.2"]}
        is_safe, msg = check_door_safe_to_open(status, ch_status, used)
        self.assertFalse(is_safe)
        self.assertIn("HV0.2", msg)
        self.assertNotIn("HV0.1", msg)  # off channels should not appear

    # ---- Combined verdict ---------------------------------------------------

    def test_both_conditions_met_allows_door(self):
        status = self._door_safe_status()
        is_safe, _ = check_door_safe_to_open(status, _all_off(), USED)
        self.assertTrue(is_safe)

    def test_dew_point_ok_but_hv_on_blocks_door(self):
        status = self._door_safe_status()
        is_safe, _ = check_door_safe_to_open(status, {"caen_HV0.1_IsOn": True}, USED)
        self.assertFalse(is_safe)

    def test_hv_off_but_dew_point_unsafe_blocks_door(self):
        # min_temp at margin → dew point not safe
        status = self._door_safe_status(min_temp=-9.0, dew_point=-10.0)
        is_safe, _ = check_door_safe_to_open(status, _all_off(), USED)
        self.assertFalse(is_safe)


# ---------------------------------------------------------------------------
# check_marta_on_for_OT / IT
# ---------------------------------------------------------------------------

class TestMartaCO2Flow(unittest.TestCase):
    """OT and IT cooling checks.

    Both return a ``(bool, reason)`` TUPLE — never assert on the raw return
    value, a non-empty tuple is always truthy.

    These cases deliberately use the FSM states MARTA really publishes
    (CONNECTED / CHILLER_RUNNING / CO2_RUNNING / ALARM / DISCONNECTED) and the
    valve field names the serviceroom really publishes (outer_valve /
    pixel_valve), so a branch that cannot run in production cannot pass here.
    """

    # ---- shape --------------------------------------------------------------

    def test_both_return_a_bool_reason_tuple(self):
        """Guards the truthy-tuple trap: callers must unpack, not test directly."""
        for fn in (check_marta_on_for_OT, check_marta_on_for_IT):
            result = fn(_safe_status())
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], bool)
            self.assertIsInstance(result[1], str)
            self.assertTrue(result[1], "reason must never be empty")

    # ---- FSM gating (Q3: only CO2_RUNNING counts) ---------------------------

    def test_no_marta_data(self):
        self.assertFalse(check_marta_on_for_OT({})[0])
        self.assertFalse(check_marta_on_for_IT({})[0])

    def test_only_co2_running_counts_as_cooling(self):
        """CONNECTED (idle), CHILLER_RUNNING and ALARM are NOT cooling."""
        for state in ("DISCONNECTED", "NONE", "", "CONNECTED", "CHILLER_RUNNING", "ALARM"):
            status = {"marta": {"fsm_state": state, "status": 2}}
            with self.subTest(fsm_state=state):
                on, reason = check_marta_on_for_OT(status)
                self.assertFalse(on)
                self.assertIn("not CO2_RUNNING", reason)
                self.assertFalse(check_marta_on_for_IT(status)[0])

    def test_co2_running_with_flow_is_cooling(self):
        status = {"marta": {"fsm_state": "CO2_RUNNING", "status": 2}}
        self.assertTrue(check_marta_on_for_OT(status)[0])
        self.assertTrue(check_marta_on_for_IT(status)[0])

    # ---- CO2 flow status (Q4: only status == 2 counts) ----------------------

    def test_co2_status_not_two_is_not_flowing(self):
        for value in (0, 1, 3, "x", None):
            status = {"marta": {"fsm_state": "CO2_RUNNING", "status": value}}
            with self.subTest(status=value):
                on, reason = check_marta_on_for_OT(status)
                self.assertFalse(on)
                self.assertIn("not 2", reason)

    def test_co2_status_missing_is_not_flowing(self):
        on, reason = check_marta_on_for_OT({"marta": {"fsm_state": "CO2_RUNNING"}})
        self.assertFalse(on)
        self.assertIn("not 2", reason)

    # ---- valve handling -----------------------------------------------------

    def test_outer_valve_closed_stops_ot(self):
        status = dict(_safe_status(), serviceroom={"outer_valve": 0})
        on, reason = check_marta_on_for_OT(status)
        self.assertFalse(on)
        self.assertIn("closed", reason)

    def test_outer_valve_open_allows_ot(self):
        status = dict(_safe_status(), serviceroom={"outer_valve": 1})
        on, reason = check_marta_on_for_OT(status)
        self.assertTrue(on)
        self.assertIn("open", reason)

    def test_it_uses_pixel_valve(self):
        """The IT valve is published as pixel_valve, not inner_valve."""
        closed = dict(_safe_status(), serviceroom={"pixel_valve": 0})
        self.assertFalse(check_marta_on_for_IT(closed)[0])

        open_ = dict(_safe_status(), serviceroom={"pixel_valve": 1})
        self.assertTrue(check_marta_on_for_IT(open_)[0])

    def test_live_payload_format_open_closed_strings(self):
        """The real /serviceroom/status payload: {"pixel":"open","outer":"open"}.

        Field names and value types both differ from what Grafana/Influx shows
        (Telegraf renames them to outer_valve/pixel_valve on ingest), so this
        pins the format actually seen on the broker.
        """
        status = dict(_safe_status(), serviceroom={"pixel": "open", "outer": "open"})
        self.assertTrue(get_valve_state(status, "OT")[0])
        self.assertTrue(get_valve_state(status, "IT")[0])
        self.assertTrue(check_marta_on_for_OT(status)[0])
        self.assertTrue(check_marta_on_for_IT(status)[0])

        status = dict(_safe_status(), serviceroom={"pixel": "open", "outer": "closed"})
        self.assertFalse(check_marta_on_for_OT(status)[0])
        self.assertTrue(check_marta_on_for_IT(status)[0])

    def test_valve_value_spellings(self):
        for raw, expected in [
            ("open", True), ("OPEN", True), (" Open ", True), (1, True), ("1", True),
            (True, True), (1.0, True),
            ("closed", False), ("CLOSED", False), (0, False), ("0", False),
            (False, False), (0.0, False),
            ("", None), ("unknown", None), (None, None), (7, None), ("ajar", None),
        ]:
            with self.subTest(raw=raw):
                self.assertIs(parse_valve_value(raw), expected)

    def test_it_accepts_inner_valve_alias(self):
        status = dict(_safe_status(), serviceroom={"inner_valve": 0})
        self.assertFalse(check_marta_on_for_IT(status)[0])

    def test_ot_and_it_valves_are_independent(self):
        """The whole point of having two functions: they must differ."""
        status = dict(_safe_status(), serviceroom={"outer_valve": 0, "pixel_valve": 1})
        self.assertFalse(check_marta_on_for_OT(status)[0])
        self.assertTrue(check_marta_on_for_IT(status)[0])

        status = dict(_safe_status(), serviceroom={"outer_valve": 1, "pixel_valve": 0})
        self.assertTrue(check_marta_on_for_OT(status)[0])
        self.assertFalse(check_marta_on_for_IT(status)[0])

    def test_ot_valve_does_not_answer_for_it(self):
        """An OT-only payload must leave IT UNKNOWN, not silently 'open'."""
        status = dict(_safe_status(), serviceroom={"outer_valve": 1})
        self.assertIsNone(get_valve_state(status, "IT")[0])

    # ---- UNKNOWN valve policy (Q2) -----------------------------------------

    def test_unknown_valve_is_permissive_by_default_but_reported(self):
        """Production case today: no serviceroom data at all."""
        on, reason = check_marta_on_for_OT(_safe_status())
        self.assertTrue(on)
        self.assertIn("UNKNOWN", reason)

    def test_empty_serviceroom_is_unknown_not_closed(self):
        """A serviceroom key with no valve fields must not read as 'closed'.

        System._status now always contains a 'serviceroom' key, so a
        `.get(field, 0)` style default would trip the interlock continuously.
        """
        status = dict(_safe_status(), serviceroom={})
        self.assertIsNone(get_valve_state(status, "OT")[0])
        self.assertTrue(check_marta_on_for_OT(status)[0])

        status = dict(_safe_status(), serviceroom={"outer_str": 5})
        self.assertIsNone(get_valve_state(status, "OT")[0])
        self.assertTrue(check_marta_on_for_OT(status)[0])

    def test_unknown_valve_fails_safe_when_required(self):
        on, reason = check_marta_on_for_OT(_safe_status(), require_valve_open=True)
        self.assertFalse(on)
        self.assertIn("UNKNOWN", reason)

    def test_closed_valve_overrides_the_permissive_policy(self):
        """require_valve_open only affects UNKNOWN; closed is always closed."""
        status = dict(_safe_status(), serviceroom={"outer_valve": 0})
        self.assertFalse(check_marta_on_for_OT(status, require_valve_open=False)[0])

    def test_unparseable_valve_is_unknown(self):
        """"open" now parses; a value with no known meaning must still be UNKNOWN."""
        status = dict(_safe_status(), serviceroom={"outer_valve": "moving"})
        state, reason = get_valve_state(status, "OT")
        self.assertIsNone(state)
        self.assertIn("not a known", reason)

    def test_out_of_range_valve_value_is_unknown(self):
        status = dict(_safe_status(), serviceroom={"outer_valve": 7})
        state, reason = get_valve_state(status, "OT")
        self.assertIsNone(state)
        self.assertIn("not a known", reason)

    # ---- staleness ----------------------------------------------------------

    def test_stale_valve_reading_is_unknown(self):
        """A dead publisher must not latch its last valve position forever."""
        old = datetime.datetime.now().timestamp() - 600
        status = dict(
            _safe_status(),
            serviceroom={"outer_valve": 1, "_received_epoch": old},
        )
        state, reason = get_valve_state(status, "OT", max_age_seconds=120)
        self.assertIsNone(state)
        self.assertIn("stale", reason)
        # ... and with no age limit the same reading is used normally.
        self.assertTrue(get_valve_state(status, "OT", max_age_seconds=0)[0])

    def test_fresh_valve_reading_is_used(self):
        now = datetime.datetime.now().timestamp()
        status = dict(
            _safe_status(),
            serviceroom={"outer_valve": 0, "_received_epoch": now},
        )
        self.assertFalse(get_valve_state(status, "OT", max_age_seconds=120)[0])

    def test_valve_without_timestamp_is_unknown_when_age_enforced(self):
        status = dict(_safe_status(), serviceroom={"outer_valve": 1})
        self.assertIsNone(get_valve_state(status, "OT", max_age_seconds=120)[0])


class TestProductionStatusShape(unittest.TestCase):
    """Guards against the class of bug this whole change was about.

    The old valve code was gated on ``if "serviceroom" in system_status``, which
    was never true in production, so six tests passed against a branch that could
    not run. These build the status dict the way System actually builds it.
    """

    @staticmethod
    def _production_status(**overrides):
        status = {
            "marta": {},
            "coldroom": {},
            "thermal_camera": {},
            "caen": {},
            "cleanroom": {},
            "coldroomair": {},
            "serviceroom": {},
        }
        status.update(overrides)
        return status

    def test_system_status_really_has_a_serviceroom_key(self):
        from coldroom.system import System

        src = inspect.getsource(System.__init__)
        self.assertIn('"serviceroom"', src)

    def test_ot_and_it_differ_on_the_production_shape(self):
        status = self._production_status(
            marta={"fsm_state": "CO2_RUNNING", "status": 2},
            serviceroom={"outer_valve": 1, "pixel_valve": 0},
        )
        self.assertTrue(check_marta_on_for_OT(status)[0])
        self.assertFalse(check_marta_on_for_IT(status)[0])

    def test_empty_serviceroom_does_not_read_as_closed(self):
        status = self._production_status(
            marta={"fsm_state": "CO2_RUNNING", "status": 2}
        )
        self.assertTrue(check_marta_on_for_OT(status)[0])
        self.assertIn("UNKNOWN", check_marta_on_for_OT(status)[1])


class TestItEnforcementFlag(unittest.TestCase):
    """Q5: a closed IT valve must NOT cut power unless explicitly enabled."""

    @staticmethod
    def _status():
        return {
            "marta": {"fsm_state": "CO2_RUNNING", "status": 2},
            "coldroom": {},
            "serviceroom": {"outer_valve": 1, "pixel_valve": 0},
        }

    def test_closed_it_valve_does_not_trip_by_default(self):
        caen = _make_caen()
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}
        is_safe, _ = soft_interlock_loop(self._status(), ch_status, USED, caen)
        self.assertTrue(is_safe)
        caen.off.assert_not_called()

    def test_closed_it_valve_trips_when_enforced(self):
        caen = _make_caen()
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}
        state = {"pending_count": 0}
        for _ in range(2):
            is_safe, msg = soft_interlock_loop(
                self._status(), ch_status, USED, caen,
                interlock_state=state, confirm_checks=2, enforce_it_valve=True,
            )
        self.assertFalse(is_safe)
        self.assertIn("IT CO2", msg)
        caen.off.assert_called()

    def test_open_it_valve_is_safe_even_when_enforced(self):
        caen = _make_caen()
        status = self._status()
        status["serviceroom"]["pixel_valve"] = 1
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}
        is_safe, _ = soft_interlock_loop(
            status, ch_status, USED, caen, enforce_it_valve=True
        )
        self.assertTrue(is_safe)
        caen.off.assert_not_called()


# ---------------------------------------------------------------------------
# switch_all_hv_off / switch_all_lv_off
# ---------------------------------------------------------------------------

class TestSwitchHelpers(unittest.TestCase):
    """Direct tests for the channel-switching primitives."""

    def test_switch_hv_off_calls_caen_off_for_each_channel(self):
        caen = _make_caen()
        used = {"LV": [], "HV": ["HV0.1", "HV0.2"]}
        result = switch_all_hv_off(caen, used)
        self.assertTrue(result)
        caen.off.assert_any_call("HV0.1")
        caen.off.assert_any_call("HV0.2")

    def test_switch_lv_off_calls_caen_off_for_each_channel(self):
        caen = _make_caen()
        used = {"LV": ["LV0.1", "LV0.2"], "HV": []}
        result = switch_all_lv_off(caen, used)
        self.assertTrue(result)
        caen.off.assert_any_call("LV0.1")
        caen.off.assert_any_call("LV0.2")

    def test_switch_hv_off_skips_none_entries(self):
        caen = _make_caen()
        used = {"LV": [], "HV": [None, "HV0.1"]}
        switch_all_hv_off(caen, used)
        caen.off.assert_called_once_with("HV0.1")

    def test_switch_lv_off_skips_none_entries(self):
        caen = _make_caen()
        used = {"LV": [None, "LV0.1"], "HV": []}
        switch_all_lv_off(caen, used)
        caen.off.assert_called_once_with("LV0.1")

    def test_switch_hv_returns_false_on_caen_error(self):
        caen = _make_caen()
        caen.off.side_effect = RuntimeError("TCP connection lost")
        result = switch_all_hv_off(caen, {"LV": [], "HV": ["HV0.1"]})
        self.assertFalse(result)

    def test_switch_lv_returns_false_on_caen_error(self):
        caen = _make_caen()
        caen.off.side_effect = RuntimeError("TCP connection lost")
        result = switch_all_lv_off(caen, {"LV": ["LV0.1"], "HV": []})
        self.assertFalse(result)

    def test_empty_channel_lists_return_true_without_calling_off(self):
        """No channels configured — nothing to do, still success."""
        caen = _make_caen()
        self.assertTrue(switch_all_hv_off(caen, {"LV": [], "HV": []}))
        self.assertTrue(switch_all_lv_off(caen, {"LV": [], "HV": []}))
        caen.off.assert_not_called()


class TestInterlockCableI1Scope(unittest.TestCase):
    """
    The soft interlock is scoped to cable I1: it may only ever switch off the
    LV/HV channels belonging to the modules on I1's ring. Powered channels are
    discovered crate-wide, so the I1 whitelist (allowed_channels) is what keeps
    channels belonging to other setups from being touched.
    """

    UNSAFE = {"marta": {"fsm_state": "DISCONNECTED"}, "coldroom": {}}
    I1_SCOPE = {"LV": ["LV9.2"], "HV": ["HV1.6"]}

    def _confirm(self, status, ch_status, scope, caen, publish=None, allowed="I1"):
        """Drive two consecutive unsafe cycles (debounce) to force the cut.

        `allowed` defaults to the I1 whitelist: the loop discovers powered
        channels crate-wide, so the whitelist is what confines the cut to I1.
        """
        state = {"pending_count": 0}
        whitelist = self.I1_SCOPE if allowed == "I1" else allowed
        for _ in range(2):
            result = soft_interlock_loop(
                status, ch_status, scope, caen,
                publish_alarm=publish, interlock_state=state,
                allowed_channels=whitelist,
            )
        return result

    def test_only_i1_channels_are_cut(self):
        """I1 channels are cut; a foreign powered channel is left alone."""
        caen = _make_caen()
        ch_status = {
            "caen_LV9.2_IsOn": True,   # on cable I1
            "caen_HV1.6_IsOn": True,   # on cable I1
            "caen_LV15.1_IsOn": True,  # foreign setup, NOT on I1
        }
        is_safe, _ = self._confirm(self.UNSAFE, ch_status, self.I1_SCOPE, caen)

        self.assertFalse(is_safe)
        off_calls = [c.args[0] for c in caen.off.call_args_list]
        self.assertIn("HV1.6", off_calls)
        self.assertIn("LV9.2", off_calls)
        self.assertNotIn("LV15.1", off_calls)  # foreign channel spared

    def test_hv_cut_before_lv_within_scope(self):
        """HV must be switched off before LV to avoid uncontrolled discharge."""
        caen = _make_caen()
        ch_status = {"caen_LV9.2_IsOn": True, "caen_HV1.6_IsOn": True}
        self._confirm(self.UNSAFE, ch_status, self.I1_SCOPE, caen)

        off_calls = [c.args[0] for c in caen.off.call_args_list]
        self.assertLess(off_calls.index("HV1.6"), off_calls.index("LV9.2"))

    def test_foreign_power_only_does_not_trip(self):
        """Power on a non-I1 channel is not the coldroom's concern → no cut."""
        caen = _make_caen()
        ch_status = {"caen_LV15.1_IsOn": True}  # only foreign power
        is_safe, _ = self._confirm(self.UNSAFE, ch_status, self.I1_SCOPE, caen)

        self.assertTrue(is_safe)
        caen.off.assert_not_called()

    def test_unknown_whitelist_cuts_but_says_the_cut_was_unscoped(self):
        """
        Whitelist unknown (DB down / nothing mounted) + cooling unsafe + power on
        → the cut GOES AHEAD to protect the modules, but the alarm must state it
        was not scoped to cable I1 and may have hit another setup.
        """
        caen = _make_caen()
        published = []
        ch_status = {"caen_LV9.2_IsOn": True, "caen_HV1.6_IsOn": True}
        is_safe, msg = self._confirm(
            self.UNSAFE, ch_status, {"LV": [], "HV": []}, caen,
            publish=published.append, allowed={"LV": [], "HV": []},
        )

        self.assertFalse(is_safe)
        caen.off.assert_called()
        self.assertIn("NOT scoped to cable I1", msg)
        self.assertIn("CHECK THE CRATE", msg)
        self.assertTrue(any("NOT scoped to cable I1" in p for p in published))

    def test_known_whitelist_cut_carries_no_unscoped_warning(self):
        """The warning must appear only when the whitelist really was unknown."""
        caen = _make_caen()
        ch_status = {"caen_LV9.2_IsOn": True, "caen_HV1.6_IsOn": True}
        _, msg = self._confirm(self.UNSAFE, ch_status, self.I1_SCOPE, caen)

        caen.off.assert_called()
        self.assertNotIn("NOT scoped to cable I1", msg)

    def test_no_power_anywhere_is_safe(self):
        """Nothing powered → nothing to protect, whatever the whitelist says."""
        caen = _make_caen()
        ch_status = {"caen_LV9.2_IsOn": False, "caen_HV1.6_IsOn": False}
        is_safe, _ = self._confirm(
            self.UNSAFE, ch_status, {"LV": [], "HV": []}, caen,
            allowed={"LV": [], "HV": []},
        )

        self.assertTrue(is_safe)
        caen.off.assert_not_called()


class TestInterlockTripLatch(unittest.TestCase):
    """
    A confirmed protective cutoff must LATCH interlock_state["tripped"] = True so
    the UI can hold a 'TRIPPED' state until the operator acknowledges. The latch
    is set only on an actual cut, and the loop never clears it on its own.
    """

    UNSAFE = {"marta": {"fsm_state": "DISCONNECTED"}, "coldroom": {}}
    SAFE = {"marta": {"fsm_state": "RUNNING", "status": 2}, "coldroom": {}}
    I1_SCOPE = {"LV": ["LV9.2"], "HV": ["HV1.6"]}

    def test_confirmed_trip_sets_latch(self):
        caen = _make_caen()
        ch_on = {"caen_LV9.2_IsOn": True, "caen_HV1.6_IsOn": True}
        state = {"pending_count": 0, "tripped": False}
        # First cycle only warns (debounce); second cycle cuts and latches.
        soft_interlock_loop(self.UNSAFE, ch_on, self.I1_SCOPE, caen, interlock_state=state)
        self.assertFalse(state["tripped"])
        soft_interlock_loop(self.UNSAFE, ch_on, self.I1_SCOPE, caen, interlock_state=state)
        self.assertTrue(state["tripped"])
        self.assertIn("trip_time", state)

    def test_warning_only_does_not_latch(self):
        """A single unconfirmed unsafe cycle warns but must not latch a trip."""
        caen = _make_caen()
        ch_on = {"caen_LV9.2_IsOn": True, "caen_HV1.6_IsOn": True}
        state = {"pending_count": 0, "tripped": False}
        soft_interlock_loop(self.UNSAFE, ch_on, self.I1_SCOPE, caen, interlock_state=state)
        self.assertFalse(state["tripped"])
        caen.off.assert_not_called()

    def test_latch_persists_after_conditions_return_safe(self):
        """Once tripped, the latch stays set even when the next cycle is safe."""
        caen = _make_caen()
        ch_on = {"caen_LV9.2_IsOn": True, "caen_HV1.6_IsOn": True}
        state = {"pending_count": 0, "tripped": False}
        # Force a trip (two unsafe cycles).
        soft_interlock_loop(self.UNSAFE, ch_on, self.I1_SCOPE, caen, interlock_state=state)
        soft_interlock_loop(self.UNSAFE, ch_on, self.I1_SCOPE, caen, interlock_state=state)
        self.assertTrue(state["tripped"])
        # Power now off and cooling restored → loop reports safe, but latch holds.
        ch_off = {"caen_LV9.2_IsOn": False, "caen_HV1.6_IsOn": False}
        is_safe, _ = soft_interlock_loop(
            self.SAFE, ch_off, self.I1_SCOPE, caen, interlock_state=state
        )
        self.assertTrue(is_safe)
        self.assertTrue(state["tripped"])  # still latched until acknowledged


# --- Tests carried over from main (PR #4): cable-I1 whitelist + trip latch ---

MOUNTED_I1 = {
    "PS_16_10_IPG-00005": {"LV": "LV0.1", "HV": "HV0.1", "FC7": "FC7OT5_OG1"},
    "PS_16_10_IPG-00006": {"LV": "LV0.2", "HV": "HV0.2", "FC7": "FC7OT5_OG2"},
}


class TestCableChannels(unittest.TestCase):
    """get_cable_channels: derive the I1 channel whitelist from mounted modules."""

    def test_collects_lv_and_hv_endpoints(self):
        self.assertEqual(
            get_cable_channels(MOUNTED_I1),
            {"LV": ["LV0.1", "LV0.2"], "HV": ["HV0.1", "HV0.2"]},
        )

    def test_missing_and_none_endpoints_are_skipped(self):
        mounted = {
            "mod_a": {"LV": "LV0.1", "HV": None},
            "mod_b": {"FC7": "FC7OT5_OG1"},
            "mod_c": {"LV": "LV0.1", "HV": "HV0.3"},  # duplicate LV
        }
        self.assertEqual(
            get_cable_channels(mounted), {"LV": ["LV0.1"], "HV": ["HV0.3"]}
        )

    def test_no_module_info_returns_empty_lists(self):
        self.assertEqual(get_cable_channels(None), {"LV": [], "HV": []})
        self.assertEqual(get_cable_channels({}), {"LV": [], "HV": []})


class TestRestrictToCableChannels(unittest.TestCase):
    """restrict_to_cable_channels: keep only I1 channels, fail-safe when unknown."""

    def test_channels_outside_cable_are_dropped(self):
        restricted, note = restrict_to_cable_channels(
            {"LV": ["LV0.1", "LV9.9"], "HV": ["HV0.1", "HV9.9"]},
            get_cable_channels(MOUNTED_I1),
        )
        self.assertEqual(restricted, {"LV": ["LV0.1"], "HV": ["HV0.1"]})
        self.assertIn("LV9.9", note)

    def test_empty_whitelist_leaves_everything_unrestricted(self):
        """DB unreachable → must NOT silently disable the interlock."""
        used = {"LV": ["LV0.1"], "HV": ["HV0.1"]}
        restricted, note = restrict_to_cable_channels(used, {"LV": [], "HV": []})
        self.assertEqual(restricted, used)
        self.assertIn("fail-safe", note)

    def test_none_whitelist_leaves_everything_unrestricted(self):
        used = {"LV": ["LV0.1"], "HV": ["HV0.1"]}
        restricted, _ = restrict_to_cable_channels(used, None)
        self.assertEqual(restricted, used)

    def test_per_rail_whitelist_is_independent(self):
        """An HV-only whitelist must not restrict LV as a side effect."""
        restricted, _ = restrict_to_cable_channels(
            {"LV": ["LV9.9"], "HV": ["HV0.1", "HV9.9"]},
            {"LV": [], "HV": ["HV0.1"]},
        )
        self.assertEqual(restricted, {"LV": ["LV9.9"], "HV": ["HV0.1"]})


class TestSoftInterlockCableScope(unittest.TestCase):
    """The interlock only cuts channels connected to cable I1."""

    def test_only_cable_channels_are_switched_off(self):
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {
            "caen_LV0.1_IsOn": True,   # on cable I1
            "caen_HV0.1_IsOn": True,   # on cable I1
            "caen_LV9.9_IsOn": True,   # another cable — must be left alone
            "caen_HV9.9_IsOn": True,   # another cable — must be left alone
        }

        soft_interlock_loop(
            status,
            ch_status,
            {"LV": [], "HV": []},
            caen,
            allowed_channels=get_cable_channels(MOUNTED_I1),
        )

        switched = [c.args[0] for c in caen.off.call_args_list]
        self.assertIn("LV0.1", switched)
        self.assertIn("HV0.1", switched)
        self.assertNotIn("LV9.9", switched)
        self.assertNotIn("HV9.9", switched)

    def test_power_on_only_outside_cable_does_not_trip(self):
        """Channels on other cables are not this GUI's responsibility."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV9.9_IsOn": True, "caen_HV9.9_IsOn": True}

        is_safe, _ = soft_interlock_loop(
            status,
            ch_status,
            {"LV": [], "HV": []},
            caen,
            allowed_channels=get_cable_channels(MOUNTED_I1),
        )

        self.assertTrue(is_safe)
        caen.off.assert_not_called()

    def test_unknown_cable_channels_fall_back_to_cutting_everything(self):
        """No DB info → protection must stay as broad as before."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV9.9_IsOn": True}

        is_safe, _ = soft_interlock_loop(
            status,
            ch_status,
            {"LV": [], "HV": []},
            caen,
            allowed_channels={"LV": [], "HV": []},
        )

        self.assertFalse(is_safe)
        caen.off.assert_any_call("LV9.9")

    def test_omitting_allowed_channels_keeps_legacy_behaviour(self):
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV9.9_IsOn": True}

        is_safe, _ = soft_interlock_loop(status, ch_status, {"LV": [], "HV": []}, caen)

        self.assertFalse(is_safe)
        caen.off.assert_any_call("LV9.9")


# ---------------------------------------------------------------------------
# Trip acknowledgement latch
# ---------------------------------------------------------------------------

class TestTripAcknowledgement(unittest.TestCase):
    """A confirmed trip stays latched until the operator acknowledges it."""

    def _trip(self, state):
        """Drive the loop into a confirmed trip, honouring the debounce."""
        caen = _make_caen()
        status = {"marta": {"fsm_state": "DISCONNECTED"}}
        ch_status = {"caen_LV0.1_IsOn": True, "caen_HV0.1_IsOn": False}
        for _ in range(state.get("_confirm", 2) if state else 2):
            soft_interlock_loop(
                status, ch_status, USED, caen, interlock_state=state, confirm_checks=2
            )
        return caen

    def test_no_trip_means_nothing_to_acknowledge(self):
        state = {"pending_count": 0}
        soft_interlock_loop(
            _safe_status(), _all_off(), USED, caen := _make_caen(),
            interlock_state=state,
        )
        self.assertFalse(is_trip_unacknowledged(state))
        self.assertEqual(acknowledge_trip(state), "")
        caen.off.assert_not_called()

    def test_confirmed_trip_latches_state(self):
        state = {"pending_count": 0}
        caen = self._trip(state)
        caen.off.assert_called()
        self.assertTrue(is_trip_unacknowledged(state))
        self.assertEqual(state["trip_count"], 1)
        self.assertIn("MARTA", state["trip_reason"])

    def test_unconfirmed_warning_does_not_latch(self):
        """The first, unconfirmed detection only warns — no trip to acknowledge."""
        state = {"pending_count": 0}
        caen = _make_caen()
        soft_interlock_loop(
            {"marta": {"fsm_state": "DISCONNECTED"}},
            {"caen_LV0.1_IsOn": True},
            USED,
            caen,
            interlock_state=state,
            confirm_checks=2,
        )
        caen.off.assert_not_called()
        self.assertFalse(is_trip_unacknowledged(state))

    def test_latch_survives_recovery_until_acknowledged(self):
        """Conditions recovering must NOT clear the latch on their own."""
        state = {"pending_count": 0}
        self._trip(state)

        is_safe, _ = soft_interlock_loop(
            _safe_status(), _all_off(), USED, _make_caen(), interlock_state=state
        )

        self.assertTrue(is_safe)                      # conditions are fine again
        self.assertTrue(is_trip_unacknowledged(state))  # but the trip is still latched
        self.assertEqual(state["pending_count"], 0)

    def test_acknowledge_clears_latch(self):
        state = {"pending_count": 0}
        self._trip(state)

        description = acknowledge_trip(state)

        self.assertIn("Trip #1", description)
        self.assertFalse(is_trip_unacknowledged(state))
        self.assertEqual(acknowledge_trip(state), "")  # idempotent

    def test_describe_trip_names_the_switched_channels(self):
        state = {"pending_count": 0}
        self._trip(state)
        description = describe_trip(state)
        self.assertIn("LV0.1", description)
        self.assertIn("HV0.1", description)

    def test_second_trip_relatches_after_acknowledgement(self):
        state = {"pending_count": 0}
        self._trip(state)
        acknowledge_trip(state)
        soft_interlock_loop(
            _safe_status(), _all_off(), USED, _make_caen(), interlock_state=state
        )
        self._trip(state)
        self.assertTrue(is_trip_unacknowledged(state))
        self.assertEqual(state["trip_count"], 2)

    def test_no_persistent_state_does_not_crash(self):
        """interlock_state=None acts immediately and simply cannot latch."""
        caen = _make_caen()
        is_safe, _ = soft_interlock_loop(
            {"marta": {"fsm_state": "DISCONNECTED"}},
            {"caen_LV0.1_IsOn": True},
            USED,
            caen,
        )
        self.assertFalse(is_safe)
        caen.off.assert_called()
        self.assertFalse(is_trip_unacknowledged(None))

    def test_verdict_reports_unacknowledged_trip_after_recovery(self):
        self.assertIn("TRIPPED EARLIER", interpret_soft_interlock(True, True))
        self.assertIn("OK", interpret_soft_interlock(True, False))
        # A live unsafe verdict outranks the latch.
        self.assertIn("INTERLOCK TRIPPED", interpret_soft_interlock(False, True))


if __name__ == "__main__":
    unittest.main()
