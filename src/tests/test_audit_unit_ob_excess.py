from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Callable


from wite2_tools.auditing.audit_unit_ob_excess import audit_unit_ob_excess

@patch(
    "wite2_tools.auditing.audit_unit_ob_excess.get_ob_suffix",
    return_value="41a"
)
def test_audit_unit_ob_excess_flags_violations(
    mock_suffix: MagicMock,
    make_unit_csv: Callable[..., Path],
    make_ob_csv: Callable[..., Path],
    make_ground_csv: Callable[..., Path]
) -> None:
    # OB Authorizes 10 squads
    ob_csv = make_ob_csv(
        filename="excess_ob.csv",
        rows_data=[{"id": "1", "name": "Test OB", "squads": [(0, "100", "10")]}]
    )
    ground_csv = make_ground_csv(
        filename="excess_gnd.csv",
        rows_data=[{"id": "100", "weapons": [(0, "10", "1")]}]
    )

    # Unit has 15 squads (150% of authorization, violating 125% limit)
    unit_csv = make_unit_csv(
        filename="excess_unit.csv",
        rows_data=[{
            "id": "10",
            "name": "Violator",
            "type": "1",
            "nat": "1",
            "squads": [(0, "100", "15")]
        }]
    )

    issues = audit_unit_ob_excess(
        str(unit_csv), str(ob_csv), str(ground_csv), {1}
    )
    assert issues == 1
