from enum import IntEnum

class GndColumn(IntEnum):
    """
    Ground Column indexes for WiTE2's _ground.csv files
    """
    ID = 0
    NAME = 1
    ID_2 = 2
    TYPE = 3
    SYM = 4
    NAT = 5
    MAX_LOAD = 6
    LOAD_COST = 7
    YEAR = 8
    LAST = 9
    LAST_MONTH = 10
    RANGE = 11  # max effective range
    SPEED = 12  #: speed in miles per hour
    DUR = 13
    SIZE = 14
    RELIB = 15  #: Reliability and Survivabiliy
    """
    The first digit represents the reliability of the AFV when
    moving (if only 1 digit is shown the 1st digit is assumed to be 0).
    The higher the number, the less likely the AFV will become damaged during
    movement.
    The second digit is survivability, and the higher the survivability the less
    likely the AFV will be destroyed in combat during a special survival check as
    opposed to just being damaged.
    """
    ARMOR = 16  #: front armour thickness in millimetres
    SIDE_ARMOR = 17
    TOP_ARMOR = 18
    MONTH = 19
    BUILD_LIMIT = 20
    MEN = 21
    UPGRADE = 22
    FUEL_USE = 23
    SUPPLY_USE = 24
    BUILD_COST = 25
    POOL = 26
    MAX_IMPORT = 27
    IMPORT_FROM = 28
    PHOTO = 29
    EXP_RATE = 30
    SCRAP_AFTER_YEAR = 31
   # --- Weapons ---
    WPN_0, WPN_1, WPN_2, WPN_3, WPN_4 = 32, 33, 34, 35, 36
    WPN_5, WPN_6, WPN_7, WPN_8, WPN_9 = 37, 38, 39, 40, 41

    WPN_NUM_0, WPN_NUM_1, WPN_NUM_2, WPN_NUM_3, WPN_NUM_4 = 42, 43, 44, 45, 46
    WPN_NUM_5, WPN_NUM_6, WPN_NUM_7, WPN_NUM_8, WPN_NUM_9 = 47, 48, 49, 50, 51

    WPN_AMMO_0, WPN_AMMO_1, WPN_AMMO_2, WPN_AMMO_3 = 52, 53, 54, 55
    WPN_AMMO_4, WPN_AMMO_5, WPN_AMMO_6, WPN_AMMO_7 = 56, 57, 58, 59
    WPN_AMMO_8, WPN_AMMO_9 = 60, 61

    WPN_ROF_0 = 62
    """
    Rate of Fire is a negative modifier that is applied to vehicle mounted
    devices to reflect the restrictions of operating the device inside the
    vehicle.
    """
    WPN_ROF_1, WPN_ROF_2, WPN_ROF_3, WPN_ROF_4 = 63, 64, 65, 66
    WPN_ROF_5, WPN_ROF_6, WPN_ROF_7, WPN_ROF_8 = 67, 68, 69, 70
    WPN_ROF_9 = 71

    WPN_ACC_0, WPN_ACC_1, WPN_ACC_2, WPN_ACC_3, WPN_ACC_4 = 72, 73, 74, 75, 76
    WPN_ACC_5, WPN_ACC_6, WPN_ACC_7, WPN_ACC_8, WPN_ACC_9 = 77, 78, 79, 80, 81

    WPN_FACE_0, WPN_FACE_1, WPN_FACE_2, WPN_FACE_3 = 82, 83, 84, 85
    WPN_FACE_4, WPN_FACE_5, WPN_FACE_6, WPN_FACE_7 = 86, 87, 88, 89
    WPN_FACE_8, WPN_FACE_9 = 90, 91