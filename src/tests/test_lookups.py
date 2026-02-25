from wite2_tools.utils.lookups import get_nat_abbr
from wite2_tools.utils.lookups import get_device_type_name

def test_get_nat_abbr_known_codes():
    """
    Verifies that standard WiTE2 nationality codes return the expected
    three-letter abbreviations.
    """
    # Test major factions
    assert get_nat_abbr(1) == "Ger"
    assert get_nat_abbr(12) == "SU"
    assert get_nat_abbr(13) == "USA"

    # Test minor factions
    assert get_nat_abbr(2) == "Fin"
    assert get_nat_abbr(3) == "Ita"
    assert get_nat_abbr(41) == "Swe"

def test_get_nat_abbr_unknown_codes():
    """
    Verifies the fallback logic when a code is not present in the lookup.
    """
    # Test out-of-bounds codes
    assert get_nat_abbr(999) == "Unk (999)"
    assert get_nat_abbr(-1) == "Unk (-1)"

def test_get_nat_abbr_boundary_codes():
    """
    Verifies edge cases like 0 or non-standard entries.
    """
    # Code 0 is typically 'None' or 'Neutral' in game data but not in this lookup
    assert get_nat_abbr(0) == "Unk (0)"

def test_get_device_type_name_known_codes():
    """
    Verifies that standard WiTE2 device type IDs return the expected
    descriptive names.
    """
    # Test common weapon types
    assert get_device_type_name(1) == "Man Weapon"
    assert get_device_type_name(6) == "Md Gun"
    assert get_device_type_name(25) == "DP Gun"

    # Test specialized equipment
    assert get_device_type_name(14) == "Factory"
    assert get_device_type_name(19) == "Air RADAR"
    assert get_device_type_name(30) == "Armor"

def test_get_device_type_name_unknown_codes():
    """
    Verifies the fallback logic when a device type code is not
    present in the lookup dictionary. [cite: 932-933]
    """
    # Test out-of-bounds IDs
    assert get_device_type_name(999) == "Unk (999)"
    assert get_device_type_name(-5) == "Unk (-5)"
