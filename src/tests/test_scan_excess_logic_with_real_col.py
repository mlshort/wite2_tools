# Internal package imports
from wite2_tools.config import ENCODING_TYPE

def test_scan_excess_logic_with_real_columns(tmp_path):
    """Verifies the resource > 5 * need logic using real WiTE2 headers."""
    # Note: 'sup' is the current supply, 'sNeed' is the requirement
    headers = "id,name,type,sup,sNeed\n"
    content = (
        "1,Normal Unit,1,100,100\n"   # 1x need: Fine
        "2,Excess Unit,1,600,100\n"   # 6x need: Should be flagged (>5)
    )
    file_path = tmp_path / "test_excess.csv"
    file_path.write_text(headers + content, encoding=ENCODING_TYPE)

    from wite2_tools.scanning.scan_unit_for_excess import scan_units_for_excess_supplies

    # This should find exactly 1 unit (ID 2)
    matches = scan_units_for_excess_supplies(str(file_path))
    assert matches == 1