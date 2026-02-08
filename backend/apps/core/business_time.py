"""Business-hours-aware deadline calculator.

Pure functions only -- no Django model imports.
Uses zoneinfo from Python 3.9+ stdlib.
"""

import datetime as dt
from zoneinfo import ZoneInfo

DAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def add_business_minutes(start, minutes, hours_cfg, holidays_cfg, tz_name):
    """Add business minutes to a datetime, returning the deadline.

    Args:
        start: aware datetime (UTC)
        minutes: int, business minutes to add
        hours_cfg: dict like {"mon": [["09:00","17:00"]], ...}
        holidays_cfg: dict like {"2026-12-25": "Weihnachten"}
        tz_name: str like "Europe/Berlin"

    Returns:
        aware datetime (UTC) of the deadline
    """
    tz = ZoneInfo(tz_name)
    local = start.astimezone(tz)
    current = _snap_to_next_open(local, hours_cfg, holidays_cfg)
    return _consume_minutes(current, minutes, hours_cfg, holidays_cfg, tz)


def remaining_business_minutes(deadline, now, hours_cfg, holidays_cfg, tz_name):
    """Calculate remaining business minutes between now and deadline.

    Returns 0 if deadline is already passed.
    """
    if not deadline or deadline <= now:
        return 0
    tz = ZoneInfo(tz_name)
    local_now = now.astimezone(tz)
    local_deadline = deadline.astimezone(tz)
    return _count_minutes_between(local_now, local_deadline, hours_cfg, holidays_cfg)


# ── Core algorithm ───────────────────────────────────────────


def _consume_minutes(current, remaining, hours_cfg, holidays_cfg, tz):
    """Walk through business windows consuming minutes."""
    max_iterations = 366 * 10
    for _ in range(max_iterations):
        window_end = _current_window_end(current, hours_cfg)
        available = _minutes_between(current, window_end)
        if available >= remaining:
            return _add_minutes_utc(current, remaining, tz)
        remaining -= available
        current = _next_business_window(
            window_end, hours_cfg, holidays_cfg,
        )
    raise ValueError('Could not resolve deadline within iteration limit')


def _count_minutes_between(local_start, local_end, hours_cfg, holidays_cfg):
    """Count business minutes between two local datetimes."""
    total = 0
    current = _snap_to_next_open(local_start, hours_cfg, holidays_cfg)
    max_iterations = 366 * 10
    for _ in range(max_iterations):
        if current >= local_end:
            return total
        window_end = _current_window_end(current, hours_cfg)
        if window_end >= local_end:
            return total + _minutes_between(current, local_end)
        total += _minutes_between(current, window_end)
        current = _next_business_window(
            window_end, hours_cfg, holidays_cfg,
        )
    return total


# ── Snapping to business hours ───────────────────────────────


def _snap_to_next_open(local_dt, hours_cfg, holidays_cfg):
    """If local_dt is outside business hours, advance to next open."""
    day_key = DAY_KEYS[local_dt.weekday()]
    date_str = local_dt.strftime('%Y-%m-%d')
    windows = _day_windows(day_key, hours_cfg)
    if date_str in holidays_cfg or not windows:
        return _next_business_day_start(local_dt, hours_cfg, holidays_cfg)
    return _snap_within_day(local_dt, windows, hours_cfg, holidays_cfg)


def _snap_within_day(local_dt, windows, hours_cfg, holidays_cfg):
    """Find the correct window within the current day."""
    t = local_dt.time()
    for open_str, close_str in windows:
        open_t = _parse_time(open_str)
        close_t = _parse_time(close_str)
        if t < open_t:
            return local_dt.replace(
                hour=open_t.hour, minute=open_t.minute,
                second=0, microsecond=0,
            )
        if open_t <= t < close_t:
            return local_dt
    return _next_business_day_start(local_dt, hours_cfg, holidays_cfg)


# ── Window navigation ────────────────────────────────────────


def _current_window_end(local_dt, hours_cfg):
    """Return the end-of-window datetime for the current position."""
    day_key = DAY_KEYS[local_dt.weekday()]
    windows = _day_windows(day_key, hours_cfg)
    t = local_dt.time()
    for open_str, close_str in windows:
        open_t = _parse_time(open_str)
        close_t = _parse_time(close_str)
        if open_t <= t < close_t:
            return local_dt.replace(
                hour=close_t.hour, minute=close_t.minute,
                second=0, microsecond=0,
            )
    raise ValueError(f'Not in any business window at {local_dt}')


def _next_business_window(window_end, hours_cfg, holidays_cfg):
    """Given a window-end time, find the start of the next window."""
    day_key = DAY_KEYS[window_end.weekday()]
    windows = _day_windows(day_key, hours_cfg)
    next_open = _find_later_window(window_end.time(), windows)
    if next_open:
        return window_end.replace(
            hour=next_open.hour, minute=next_open.minute,
            second=0, microsecond=0,
        )
    return _next_business_day_start(window_end, hours_cfg, holidays_cfg)


def _next_business_day_start(local_dt, hours_cfg, holidays_cfg):
    """Advance to the opening time of the next business day."""
    day = local_dt.date() + dt.timedelta(days=1)
    for _ in range(366):
        date_str = day.strftime('%Y-%m-%d')
        day_key = DAY_KEYS[day.weekday()]
        windows = _day_windows(day_key, hours_cfg)
        if windows and date_str not in holidays_cfg:
            open_t = _parse_time(windows[0][0])
            return local_dt.replace(
                year=day.year, month=day.month, day=day.day,
                hour=open_t.hour, minute=open_t.minute,
                second=0, microsecond=0,
            )
        day += dt.timedelta(days=1)
    raise ValueError('No business day found within 366 days')


def _find_later_window(current_time, windows):
    """Return the open-time of the next window after current_time."""
    for open_str, _close_str in windows:
        open_t = _parse_time(open_str)
        if open_t > current_time:
            return open_t
    return None


# ── Utilities ────────────────────────────────────────────────


def _day_windows(day_key, hours_cfg):
    """Return list of [open, close] pairs for a day key."""
    return hours_cfg.get(day_key, [])


def _parse_time(time_str):
    """Parse 'HH:MM' into a time object."""
    h, m = time_str.split(':')
    return dt.time(int(h), int(m))


def _minutes_between(start_dt, end_dt):
    """Return minutes between two datetimes."""
    delta = end_dt - start_dt
    return int(delta.total_seconds() / 60)


def _add_minutes_utc(local_dt, minutes, tz):
    """Add minutes to local_dt and convert back to UTC."""
    result = local_dt + dt.timedelta(minutes=minutes)
    return result.astimezone(ZoneInfo('UTC'))
