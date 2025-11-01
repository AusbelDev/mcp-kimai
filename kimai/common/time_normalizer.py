from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class NormalizerConfig:
    server_tz: str = "America/Mexico_City"  # your server zone (GMT-6)
    return_utc: bool = True  # True => output UTC; False => server-local
    business_start: int = 8  # 08:00
    business_end: int = 20  # 20:00 (exclusive)


class KimaiBeginNormalizer:
    _ISO_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
    _TRAILING_TZ = re.compile(r"(?:Z|[+-]\d{2}:\d{2})$")
    _ISO_TIME = re.compile(
        r"(?:(?<=^)|(?<=T)|(?<=\s))([01]\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?"
    )
    _HHMM = re.compile(r"(?:(?<=^)|(?<=T)|(?<=\s))([01]\d|2[0-3])([0-5]\d)(?!:)")
    _AMPM = re.compile(r"\b(1[0-2]|0?[1-9])\s*(am|pm)\b", re.IGNORECASE)
    _H_HOUR = re.compile(r"\b([01]?\d|2[0-3])\s*h\b", re.IGNORECASE)

    def __init__(self, config: NormalizerConfig = NormalizerConfig()):
        self.tz = ZoneInfo(config.server_tz)
        self.return_utc = config.return_utc
        self.bstart = config.business_start
        self.bend = config.business_end

    def normalize(self, begin: str | datetime | date | time) -> datetime:
        d = self._pick_date(begin)
        written_time = self._pick_wall_time(begin)

        # Candidate B: ignore offset, use written wall-clock as local
        local_B = datetime(
            d.year,
            d.month,
            d.day,
            written_time.hour,
            written_time.minute,
            written_time.second,
            tzinfo=self.tz,
        )

        # Candidate A: respect offset if present; otherwise equals B
        local_A = self._parse_respecting_offset(begin, d, default_if_missing=local_B)

        # Choose the better candidate
        choice = self._choose_best(local_A, local_B)

        return choice.astimezone(timezone.utc) if self.return_utc else choice

    # ---------- parsing helpers ----------
    def _pick_date(self, value: str | datetime | date | time) -> date:
        if isinstance(value, datetime):
            return date(value.year, value.month, value.day)
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        s = str(value)
        m = self._ISO_DATE.search(s)
        if m:
            y, mo, d = map(int, m.groups())
            return date(y, mo, d)
        return datetime.now(self.tz).date()

    def _pick_wall_time(self, value: str | datetime | date | time) -> time:
        if isinstance(value, datetime):
            return time(value.hour, value.minute, value.second)
        if isinstance(value, time):
            return time(value.hour, value.minute, value.second)

        s = str(value).strip()
        s_no_tz = self._TRAILING_TZ.sub("", s)

        m = self._ISO_TIME.search(s_no_tz)
        if m:
            hh = int(m.group(1))
            mm = int(m.group(2))
            ss = int(m.group(3) or 0)
            return time(hh, mm, ss)

        m = self._HHMM.search(s_no_tz)
        if m:
            hh = int(m.group(1))
            mm = int(m.group(2))
            return time(hh, mm, 0)

        m = self._AMPM.search(s_no_tz)
        if m:
            h = int(m.group(1)) % 12
            if m.group(2).lower() == "pm":
                h += 12
            return time(h, 0, 0)

        m = self._H_HOUR.search(s_no_tz)
        if m:
            return time(int(m.group(1)), 0, 0)

        # Bare hour after start/T/space
        m = re.search(r"(?:(?<=^)|(?<=T)|(?<=\s))([01]?\d|2[0-3])(?=\D|$)", s_no_tz)
        if m:
            return time(int(m.group(1)), 0, 0)

        return time(0, 0, 0)

    def _parse_respecting_offset(
        self, value: str | datetime | date | time, d: date, default_if_missing: datetime
    ) -> datetime:
        """Parse the full timestamp respecting its offset and convert to server TZ.
        If no usable offset is present, return default_if_missing."""
        if isinstance(value, datetime):
            # If it's timezone-aware, convert; if naive, treat as local (like B)
            if value.tzinfo is not None:
                return value.astimezone(self.tz).replace(
                    year=d.year, month=d.month, day=d.day
                )
            return default_if_missing

        s = str(value).strip()

        # If there is an explicit offset/Z, try parsing with fromisoformat
        if re.search(r"(Z|[+-]\d{2}:\d{2})$", s):
            try:
                # fromisoformat handles "YYYY-MM-DDTHH:MM:SS±HH:MM" and with seconds optional
                # If the string lacks seconds, add them safely for robustness.
                parsed = datetime.fromisoformat(s.replace("Z", "+00:00"))
                return parsed.astimezone(self.tz)
            except Exception:
                pass

        return default_if_missing

    # ---------- choice heuristic ----------
    def _choose_best(self, a_local: datetime, b_local: datetime) -> datetime:
        def in_business_hours(dt: datetime) -> bool:
            return self.bstart <= dt.hour < self.bend

        a_ok = in_business_hours(a_local)
        b_ok = in_business_hours(b_local)

        if a_ok and not b_ok:
            return a_local
        if b_ok and not a_ok:
            return b_local
        if a_ok and b_ok:
            # Both reasonable: pick the one closer to midday
            return self._closer_to_midday(a_local, b_local)

        # Neither in business hours: still pick the one closer to midday
        return self._closer_to_midday(a_local, b_local)

    def _closer_to_midday(self, a_local: datetime, b_local: datetime) -> datetime:
        def dist(dt: datetime) -> timedelta:
            target = dt.replace(hour=12, minute=0, second=0, microsecond=0)
            return abs(dt - target)

        return a_local if dist(a_local) <= dist(b_local) else b_local


# --------------------------- examples / quick test ---------------------------
if __name__ == "__main__":
    norm_utc = KimaiBeginNormalizer(
        NormalizerConfig(server_tz="America/Mexico_City", return_utc=True)
    )
    norm_local = KimaiBeginNormalizer(
        NormalizerConfig(server_tz="America/Mexico_City", return_utc=False)
    )

    samples = [
        "2025-10-31T13:00-06:00",  # 1pm local with local offset
        "2025-10-31T13:00+00:00",  # 1pm but labeled as UTC (we treat as 1pm local)
        "2025-10-31T19:00+00:00",  # 1pm local expressed in UTC
        "2025-10-31 13:00",  # no offset
        "2025-10-31 1 pm",  # am/pm form
        "2025-10-31 1300",  # HHMM form
        "2025-10-31 13h",  # '13h' form
    ]

    for s in samples:
        u = norm_utc.normalize(s)
        l = norm_local.normalize(s)
        print(f"{s:<25} -> UTC:   {u.isoformat()}   | local: {l.isoformat()}")
