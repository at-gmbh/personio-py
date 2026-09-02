from personio_py import Employee


def test_attribute_name_conversion():
    assert Employee._get_attribute_name_for("foo") == "foo"
    assert Employee._get_attribute_name_for("Bar") == "bar"
    assert Employee._get_attribute_name_for("Wörter") == "woerter"
    assert Employee._get_attribute_name_for("Straße & Hausnummer") == "strasse_hausnummer"
    assert Employee._get_attribute_name_for("Handy (geschäftlich) ") == "handy_geschaeftlich"
    assert Employee._get_attribute_name_for("18 Loch Golf Handicap") == "loch_golf_handicap"
