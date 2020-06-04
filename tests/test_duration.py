import pytest

from personio_py.models import Duration


def test_parse_valid():
    assert Duration.from_str('06:30') == Duration(6, 30)
    assert Duration.from_str('6:30') == Duration(6, 30)
    assert Duration.from_str('0:30') == Duration(0, 30)
    assert Duration.from_str('25:00') == Duration(25, 0)
    assert Duration.from_str('0:00') == Duration(0, 0)


def test_parse_fail():
    with pytest.raises(ValueError):
        Duration.from_str('06:3')
    with pytest.raises(ValueError):
        Duration.from_str('0630')
    with pytest.raises(ValueError):
        Duration.from_str('6:30:00')


def test_to_str():
    assert str(Duration(6, 5)) == '06:05'
    assert str(Duration(12, 30)) == '12:30'


def test_compare():
    assert Duration(5, 0) < Duration(6, 0)
    assert Duration(5, 30) < Duration(6, 15)
    assert Duration(2, 30) < Duration(27, 00)
