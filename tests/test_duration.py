from datetime import timedelta

import pytest

from personio_py.mapping import DurationFieldMapping


def test_parse_valid():
    assert parse('06:30') == delta(6, 30)
    assert parse('0:30') == delta(0, 30)
    assert parse('25:00') == delta(25, 0)
    assert parse('0:00') == delta(0, 0)


def test_parse_fail():
    with pytest.raises(ValueError):
        parse('06:3')
    with pytest.raises(ValueError):
        parse('0630')
    with pytest.raises(ValueError):
        parse('6:30:00')


def test_to_str():
    assert serialize(6, 5) == '06:05'
    assert serialize(12, 30) == '12:30'
    assert serialize(25, 0) == '25:00'


def parse(s: str) -> timedelta:
    return DurationFieldMapping.str_to_timedelta(s)


def delta(hours: int, minutes: int):
    return timedelta(hours=hours, minutes=minutes)


def serialize(hours: int, minutes: int):
    return DurationFieldMapping('', '').serialize(delta(hours, minutes))
