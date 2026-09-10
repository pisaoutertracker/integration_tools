"""Cross-process alarm journal and shared soft-interlock trip latch.

Why this module exists
----------------------
More than one ``cold.py`` can be running at the same time (deliberately, or by
accident when an operator starts a second copy). Each process holds its own
in-memory ``interlock_state``, and before this module that had two visible
consequences:

* every instance published its own copy of each alarm to ``/alarm``, so Slack
  showed duplicated "unconfirmed 1/2" warnings with nothing to tell them apart;
* the TRIPPED latch and its acknowledgement lived in ONE process's memory, so a
  trip raised by instance A was invisible to instance B — and the operator could
  open B's window and see a trip presented as already acknowledged, because B
  had never seen it raised in the first place.

This module gives all instances two shared files:

``alarm_journal.jsonl``
    An append-only JSON Lines record of every alarm-relevant event, each stamped
    with host + pid + the full condition snapshot that produced it. This is the
    forensic trail: it answers "what was ``fsm_state`` at the moment we tripped,
    and which instance did it?" after the fact.

``interlock_latch.json``
    The single source of truth for "is there an unacknowledged trip?". Any
    instance that trips writes it; every instance reads it each cycle; one
    acknowledgement, in any instance, clears it for all of them.

Both files are guarded with ``fcntl.flock`` so concurrent access from several
processes is safe.

Safety note
-----------
This is a *diagnostic* facility attached to a safety interlock. It must never be
able to break the interlock, so every public method swallows its own exceptions
and degrades to in-memory-only behaviour rather than propagating. A failure to
write the journal is logged once and never raised into the interlock loop.
"""

import datetime
import errno
import fcntl
import json
import logging
import os
import socket
import uuid

logger = logging.getLogger(__name__)

# Journal is rotated once it grows past this; one previous generation is kept.
DEFAULT_MAX_BYTES = 5 * 1024 * 1024

# Events always written. "check" cycles are written only on a change of the
# watched condition fields, or every `heartbeat_every` cycles, so the journal
# stays readable instead of accumulating one line every 5 s forever.
_TS_FORMAT = "%Y-%m-%d %H:%M:%S"

# Condition fields whose change makes a routine cycle worth journalling. These
# are exactly the values that decide a trip, so any transition that could lead
# to a cutoff leaves a record even when no alarm fired.
WATCHED_FIELDS = (
    "fsm_state",
    "co2_status",
    "marta_ot",
    "marta_it",
    "lv_on",
    "hv_on",
    "cooling_unsafe",
    "cooling_reason",
    "scope_empty",
    # Tri-state valve readings: a valve opening/closing, or its data going
    # unknown/stale, is exactly the kind of transition worth a journal line.
    "ot_valve",
    "it_valve",
)


# Values that explicitly switch the mirror OFF in settings_coldroom.yaml.
_MIRROR_OFF_VALUES = {"none", "false", "off", "no", "0"}


def resolve_mirror_dir(value, default_dir):
    """Turn the settings value for alarm_log_mirror_dir into a path or None.

    A key present with no value parses as ``None`` in YAML, which must mean
    "use the default" -- NOT "disabled". Only an explicit string like "none"
    turns the mirror off. (Getting this backwards silently disabled the mirror:
    ``str(None).lower()`` is the string "none".)
    """
    if value is None:
        return default_dir
    text = str(value).strip()
    if not text:
        return default_dir
    if text.lower() in _MIRROR_OFF_VALUES:
        return None
    return os.path.expanduser(text)


def format_record(record):
    """One readable line for a journal record, for the plain-text mirror."""
    conditions = record.get("conditions") or {}
    bits = []
    for key in ("fsm_state", "marta_msg_age_s", "ot_valve", "it_valve", "lv_on", "hv_on"):
        if key in conditions:
            bits.append(f"{key}={conditions[key]}")
    detail = f"  [{', '.join(bits)}]" if bits else ""
    message = (record.get("message") or "").replace("\n", " ")
    return (
        f"{record.get('ts', '')}  pid={record.get('pid', '?')}  "
        f"{str(record.get('event', '')).upper():<18}{message}{detail}"
    )


def default_log_dir():
    """Directory holding the journal + latch, honouring XDG_STATE_HOME."""
    base = os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state")
    return os.path.join(base, "coldroom_interlock")


class AlarmLog:
    """Append-only alarm journal plus the shared trip latch.

    Args:
        log_dir: directory for both files; created if missing.
        max_bytes: rotate the journal once it exceeds this size.
        heartbeat_every: journal an unchanged cycle every N calls to
            ``log_cycle`` so the file also proves the interlock is alive.
            0 disables heartbeats.
    """

    def __init__(
        self,
        log_dir=None,
        max_bytes=DEFAULT_MAX_BYTES,
        heartbeat_every=60,
        mirror_dir=None,
    ):
        self.log_dir = log_dir or default_log_dir()
        self.journal_path = os.path.join(self.log_dir, "alarm_journal.jsonl")
        self.latch_path = os.path.join(self.log_dir, "interlock_latch.json")

        # Optional second copy of the journal somewhere easy to find (in
        # practice: a logs/ folder beside cold.py). It is a CONVENIENCE MIRROR,
        # never the source of truth -- the canonical journal and, crucially, the
        # shared trip latch stay in `log_dir`, which every instance on the
        # machine resolves to identically. Putting the latch in a per-checkout
        # folder would silently break cross-instance acknowledgement.
        self.mirror_dir = mirror_dir
        self.mirror_json_path = (
            os.path.join(mirror_dir, "alarm_journal.jsonl") if mirror_dir else None
        )
        # Same events, one readable line each, for when you just want to look.
        self.mirror_text_path = (
            os.path.join(mirror_dir, "alarm_log.txt") if mirror_dir else None
        )

        self.max_bytes = max_bytes
        self.heartbeat_every = heartbeat_every
        self.host = socket.gethostname()
        self.pid = os.getpid()
        # Identifies this process in the journal even when host+pid are reused.
        self.instance_id = f"{self.host}:{self.pid}:{uuid.uuid4().hex[:6]}"

        self._cycles_since_log = 0
        self._last_watched = None
        self._degraded = False  # set once if the journal proves unwritable
        self._mirror_degraded = False  # mirror failing must not stop the journal

        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Cannot create alarm log dir {self.log_dir}: {e}")
            self._degraded = True

        if self.mirror_dir:
            try:
                os.makedirs(self.mirror_dir, exist_ok=True)
            except OSError as e:
                logger.error(f"Cannot create alarm mirror dir {self.mirror_dir}: {e}")
                self._mirror_degraded = True

    # -- journal --------------------------------------------------------------

    def log(self, event, message="", conditions=None, **extra):
        """Append one record. Never raises."""
        now = datetime.datetime.now()
        record = {
            "ts": now.strftime(_TS_FORMAT),
            "epoch": now.timestamp(),
            "host": self.host,
            "pid": self.pid,
            "instance": self.instance_id,
            "event": event,
            "message": message,
        }
        if conditions:
            record["conditions"] = conditions
        record.update(extra)
        self._append(record)
        return record

    def log_cycle(self, conditions, message=""):
        """Journal a routine interlock cycle, but only when it is informative.

        Writes a record when any field in ``WATCHED_FIELDS`` changed since the
        previous cycle, or every ``heartbeat_every`` cycles. This is what makes
        a latched-stale value visible after the fact: the transition into
        ``fsm_state="DISCONNECTED"`` is recorded even though no alarm fired yet.
        """
        conditions = conditions or {}
        watched = {k: conditions.get(k) for k in WATCHED_FIELDS}
        changed = watched != self._last_watched
        self._cycles_since_log += 1
        due = self.heartbeat_every and self._cycles_since_log >= self.heartbeat_every

        if not changed and not due:
            return None

        self._last_watched = watched
        self._cycles_since_log = 0
        return self.log(
            "condition_change" if changed else "heartbeat",
            message,
            conditions=conditions,
        )

    def _append(self, record):
        if self._degraded:
            return
        try:
            self._rotate_if_needed()
            line = json.dumps(record, default=str, sort_keys=False)
            # Open per write: several processes append to the same file, and an
            # exclusive flock around the write keeps their lines from interleaving.
            with open(self.journal_path, "a", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write(line + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            # Log once, then stay quiet: a broken journal must not spam the
            # console every 5 s, and must never break the interlock.
            logger.error(f"Alarm journal write failed, disabling journal: {e}")
            self._degraded = True

        self._append_mirror(record)

    def _append_mirror(self, record):
        """Copy the record to the easy-to-find mirror. Failures are swallowed.

        Deliberately independent of the canonical write above: a full disk or a
        read-only checkout must cost you the convenience copy, never the real
        journal and never the interlock.
        """
        if not self.mirror_dir or self._mirror_degraded:
            return
        try:
            self._rotate_path_if_needed(self.mirror_json_path)
            self._rotate_path_if_needed(self.mirror_text_path)
            with open(self.mirror_json_path, "a", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write(json.dumps(record, default=str) + "\n")
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            with open(self.mirror_text_path, "a", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write(format_record(record) + "\n")
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Alarm mirror write failed, disabling mirror: {e}")
            self._mirror_degraded = True

    def _rotate_if_needed(self):
        self._rotate_path_if_needed(self.journal_path)

    def _rotate_path_if_needed(self, path):
        try:
            if os.path.getsize(path) < self.max_bytes:
                return
        except OSError as e:
            if e.errno == errno.ENOENT:
                return  # not created yet
            raise
        os.replace(path, path + ".1")

    # -- shared trip latch ----------------------------------------------------

    def read_latch(self):
        """Return the current unacknowledged trip record, or None.

        Every instance calls this each cycle, which is how a trip raised by one
        process becomes visible in the others.
        """
        try:
            with open(self.latch_path, "r", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    content = f.read()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            if not content.strip():
                return None
            return json.loads(content)
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Cannot read interlock latch {self.latch_path}: {e}")
            return None

    def record_trip(self, message, conditions=None, reason=""):
        """Latch a trip so every instance sees it, and journal it.

        If a trip is already latched and unacknowledged, the ORIGINAL record is
        kept — that is the one the operator is looking at and will acknowledge —
        while ``repeat_count`` and ``last_trip_ts`` are updated so a repeatedly
        re-tripping condition is still visible.
        """
        now = datetime.datetime.now()
        existing = self.read_latch()
        if existing:
            existing["repeat_count"] = int(existing.get("repeat_count", 1)) + 1
            existing["last_trip_ts"] = now.strftime(_TS_FORMAT)
            existing["last_trip_host"] = self.host
            existing["last_trip_pid"] = self.pid
            record = existing
        else:
            record = {
                "trip_id": uuid.uuid4().hex[:12],
                "ts": now.strftime(_TS_FORMAT),
                "epoch": now.timestamp(),
                "host": self.host,
                "pid": self.pid,
                "instance": self.instance_id,
                "message": message,
                "reason": reason,
                "conditions": conditions or {},
                "repeat_count": 1,
            }
        self._write_latch(record)
        self.log(
            "trip",
            message,
            conditions=conditions,
            reason=reason,
            trip_id=record.get("trip_id"),
            repeat_count=record.get("repeat_count"),
        )
        return record

    def clear_latch(self, operator=""):
        """Acknowledge the latched trip for ALL instances. Returns the cleared record."""
        record = self.read_latch()
        try:
            if os.path.exists(self.latch_path):
                os.remove(self.latch_path)
        except Exception as e:
            logger.error(f"Cannot clear interlock latch {self.latch_path}: {e}")
        self.log(
            "ack",
            "Soft interlock trip acknowledged by operator",
            trip_id=(record or {}).get("trip_id"),
            original_trip_ts=(record or {}).get("ts"),
            original_trip_host=(record or {}).get("host"),
            original_trip_pid=(record or {}).get("pid"),
            acknowledged_by=operator or os.environ.get("USER", "unknown"),
        )
        return record

    def _write_latch(self, record):
        try:
            tmp = f"{self.latch_path}.{self.pid}.tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(record, f, default=str, indent=2)
                f.flush()
                os.fsync(f.fileno())
            # Atomic replace, so a reader never sees a half-written latch.
            os.replace(tmp, self.latch_path)
        except Exception as e:
            logger.error(f"Cannot write interlock latch {self.latch_path}: {e}")
