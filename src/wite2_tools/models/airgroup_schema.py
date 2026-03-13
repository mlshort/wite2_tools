from enum import IntEnum
from typing import List, Dict

# pylint: disable=invalid-name
class AirGroupColumn(IntEnum):
    """
    Column indices for WiTE2's _airgroup.csv file.
    """
    ID = 0
    NAME = 1
    PLAYER = 2
    TYPE = 3
    AIR_TYPE = 4
    LEADER = 5
    PRIM = 6
    SUB_NUM = 7
    BASE = 8
    START_BASE = 9
    MISSION = 10
    SEC_MISSION = 11
    TARGET = 12
    PASSENGER = 13
    TRANSFER_TO = 14
    TRAVELED = 15
    SUB_TO = 16
    SUB_ID = 17
    MAX_RG = 18
    TRAINED_AS = 19
    MORALE = 20
    EXP = 21
    TACTIC = 22
    MOVED = 23
    PAT_X = 24
    PAT_Y = 25
    LANDING = 26
    FLYING = 27
    TAKEOFF = 28
    ASSIGNED = 29
    READY = 30
    FUELING = 31
    MAINT = 32
    RESERVE = 33
    MOVING = 34
    DAMAGED = 35
    TOTAL = 36
    ALT_TARGET = 37
    DEPART0 = 38
    DEPART1 = 39
    NAT = 40
    DELAY = 41
    REPLACE_DELAY = 42
    DETACHMENT = 43
    DETACHED_FROM = 44
    NAV_DEV = 45
    RADAR_DEV = 46
    KILLS = 47
    CHANGED = 48
    PILOT_NUM = 49
    NOW_READY = 50
    NOW_DAMAGED = 51
    NOW_RESERVE = 52
    NIGHT_FLY = 53
    GUARDS = 54
    WITHDRAW = 55
    A_KILLS = 56
    UPGRADE_ALLOW = 57
    UPGRADE_DONE = 58
    FATIGUE = 59
    REPLACE_MODE = 60
    NAVAL_TRAIN = 61
    NAVAL_ONLY = 62
    AIR_TASK = 63
    AIR_HQ = 64
    TRAVELED_DAY = 65
    CUR_WS = 66
    HQ_CHANGE = 67
    MISSION_PCT = 68
    TRAIN_PCT = 69
    REST_PCT = 70
    GROUP_ARRIVED = 71
    TO_TRAVEL = 72
    AIR_SYM = 73
    INFO_LINK = 74
    THEATER_BOX = 75
    TH_BOX_LOCK = 76
    WITH_TURN_0 = 77
    WITH_DEST_0 = 78
    WITH_TURN_1 = 79
    WITH_DEST_1 = 80
    WITH_TURN_2 = 81
    WITH_DEST_2 = 82
    WITH_TURN_3 = 83
    WITH_DEST_3 = 84
    WITH_TURN_4 = 85
    WITH_DEST_4 = 86



def gen_airgroup_column_names() -> List[str]:
    """
    Generates the 87 headers for a _airgroup.csv file dynamically.
    """

    # 1. Base Properties (Columns 0 to 76)
    cols: List[str] = [
        'id', 'name', 'player', 'type', 'airType', 'leader', 'prim', 'subNum',
        'base', 'startBase', 'mission', 'secMission', 'target', 'passenger',
        'transferTo', 'traveled', 'subTo', 'subId', 'maxRg', 'trainedAs',
        'morale', 'exp', 'tactic', 'moved', 'patX', 'patY', 'landing', 'flying',
        'takeoff', 'assigned', 'ready', 'fueling', 'maint', 'reserve', 'moving',
        'damaged', 'total', 'altTarget', 'depart0', 'depart1', 'nat', 'delay',
        'replaceDelay', 'detachment', 'detachedFrom', 'navDev', 'radarDev',
        'kills', 'changed', 'pilotNum', 'nowReady', 'nowDamaged', 'nowReserve',
        'nightFly', 'guards', 'withdraw', 'aKills', 'upgradeAllow', 'upgradeDone',
        'fatigue', 'replaceMode', 'navalTrain', 'navalOnly', 'airTask', 'airHQ',
        'traveledDay', 'curWS', 'hqChange', 'missionPct', 'trainPct', 'restPct',
        'groupArrived', 'toTravel', 'airSym', 'infoLink', 'theaterBox', 'thBoxLock'
    ]

    # 2. Withdrawal Slots (Columns 77 to 86)
    # 5 pairs of turn/destination arrays
    for i in range(5):
        cols.extend([f"withTurn {i}", f"withDest {i}"])

    return cols

def gen_default_airgroup_row(airgroup_id: int = 0,
                             name: str = "",
                             nat: int = 0) -> List[str]:
    """
    Generates a default 87-column row for a _airgroup.csv file.

    Args:
        airgroup_id (int): The ID for the Air Group (Column 0). Defaults to 0.
        name (str): The name of the Air Group (Column 1). Defaults to empty.
        nat (int): The nationality ID (Column 40). Defaults to 0.

    Returns:
        List[str]: A list containing the ID, Name, and zeroes mapped to the remaining slots.
    """
    # Create the base row: ID and Name
    row: List[str] = [str(airgroup_id), name]

    # Fill the remaining 85 columns with zeros
    row.extend(["0"] * 85)

    # If a specific nationality is passed, inject it into index 40
    if nat != 0:
        row[40] = str(nat)

    return row


def gen_default_airgroup_dict(airgroup_id: int = 0,
                              name: str = "",
                              nat: int = 0) -> Dict[str, str]:
    """
    Generates a default Air Group dictionary mapped to schema headers.
    """
    headers = gen_airgroup_column_names()
    default_row_list = gen_default_airgroup_row(airgroup_id, name, nat)

    # Zip the 87 headers together with the 87 default values
    return dict(zip(headers, default_row_list))
