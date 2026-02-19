"""
WiTE2 Static Data Lookups
=========================

This module provides explicitly declared dictionary mappings and
corresponding retrieval functions for War in the East 2 (WiTE2) internal
data codes. It serves as a static translation layer to convert raw numerical
IDs found in the game's CSV files into human-readable string descriptions.

Core Contents:
--------------
* Entity Translations: Contains hardcoded lookup tables for OB Types,
  Nationalities, Unit Statuses, Device Types, HQ Types, Ground Element
  Types, Device Sizes, and Device Face orientations.
* Safe Retrieval: Each lookup dictionary is paired with a getter function
  that implements safe fallback logic (e.g., returning "Unk Type (X)").
  This ensures that undocumented or custom modded game IDs do not cause
  `KeyError` crashes during runtime analysis, scanning, or logging.
"""

OB_COMBAT_CLASS_LOOKUP: dict[int, str] = {
    0: "None",
    1: "Combat",
    2: "HQ",
    3: "Support",
    4: "Partisan",
    5: "Multirole"
}

def get_ob_combat_class_name(ob_class_val:int) -> str:
    """
    Retrieves the description for a specific Combat Class code.
    Returns 'Unk ' if the code is not found.
    """
    result = OB_COMBAT_CLASS_LOOKUP.get(ob_class_val, f"Unk ({ob_class_val})")
    return result

OB_TYPE_LOOKUP: dict[int,str] = {
        0: "None",
        1: "Armor",
        2: "Mech",
        3: "Mot. Inf",
        4: "Inf",
        5: "Para",
        6: "Cav",
        7: "Arty",
        8: "AT",
        9: "Corps HQ",
       10: "Army HQ",
       11: "AG HQ",
       12: "AA",
       13: "Mtn",
       14: "SP Arty",
       15: "Eng",
       16: "Const",
       17: "Mor",
       18: "Rkt",
       19: "Sec",
       20: "Fort",
       21: "MG",
       22: "AB",
       23: "Partisan",
       24: "Air Land",
       25: "Naval"
    }

def get_ob_type_code_name(ob_type_val:int) -> str:
    """
    Not to be confused with 'get_ob_type_name', this one
    retrieves the name for a specific OB Type code.
    Returns 'Unk ' if the code is not found.
    """
    result = OB_TYPE_LOOKUP.get(ob_type_val,  f"Unk ({ob_type_val})")
    return result

NAT_LOOKUP : dict[int, str] = {
    1: "Ger",
    2: "Fin",
    3: "Ita",
    4: "Rum",
    5: "Hun",
    6: "Slo",
    8: "Cze",
    9: "Bel",
    10: "Net",
    11: "Pol",
    12: "SU",
    13: "USA",
    15: "Bri",
    16: "Gre",
    17: "Nor",
    18: "Yug",
    19: "Can",
    20: "Ind",
    21: "Aus",
    22: "Fre",
    23: "SA",
    24: "WA",
    25: "Bra",
    26: "Com",
    27: "Fra",
    32: "Den",
    41: "Swe"
}

def get_nat_abbr(nat_val:int) -> str:
    """
    Retrieves the abbreviation for a specific nat code.
    Returns 'Unk ' if the code is not found.
    """
    result = NAT_LOOKUP.get(nat_val, f"Unk ({nat_val})")
    return result

# Explicitly declared lookup for WiTE2 Nationalities
# Key: Nation ID (int), Value: Nation Name (str)
NATION_LOOKUP: dict[int, str] = {
    0: "None",
    1: "Germany",
    2: "Finland",
    3: "Italy",
    4: "Rumania",
    5: "Hungary",
    6: "Slovakia",
    7: "Bulgaria",
    8: "Czech",
    9: "Belgium",
    10: "Netherlands",
    11: "Poland",
    12: "Soviet Union",
    13: "USA",
    15: "Britain",
    16: "Greece",
    17: "Norway",
    18: "Yugoslavia",
    19: "Canada",
    20: "India",
    21: "Australia",
    22: "Free French",
    23: "South Africa",
    24: "WA Italy",
    25: "Brazil",
    26: "Commonwealth",
    27: "France",
    28: "New zealand",
    29: "Morocco",
    30: "Portugal",
    31: "Sweden",
    32: "Denmark",
    33: "Turkey",
    34: "Switzerland",
    35: "Spain",
    36: "Iraq",
    37: "vichy France",
    38: "America",
    41: "Sweden",
    42: "Ireland",
    43: "Iceland",
    44: "Luxembourg",
    45: "Switzerland",
    46: "Andorra",
    47: "Albania",
    48: "Turkey",
    49: "Portugal",
    50: "Spain",
    51: "Iraq",
    52: "Algeria",
    53: "Tunisia",
    54: "Libya",
    55: "Egypt",
    56: "Syria",
    57: "Lebanon",
    58: "Transjordan",
    59: "Palestine",
    60: "Saudi Arabia",
    61: "kuwait",
    62: "Iran",
    63: "Cyprus"
}

def get_country_name(nat_id: int) -> str:
    """
    Returns the nation name for a given ID.
    Defaults to 'Unk ' if ID is not in the list.
    """
    return NATION_LOOKUP.get(nat_id, f"Unk ({nat_id})")

# Explicitly declared lookup for Unit Status/Type
# Key: Status Integer, Value: Status Description
UNIT_SPECIAL_LOOKUP: dict[int, str] = {
    0: "None",
    1: "Guards",
    2: "Axis-Elite",
    3: "SS-Elite",
    4: "SS-Non-Elite",
    5: "LW (Luftwaffe)",
    6: "LW-Elite",
    7: "AL-Elite"
}

def get_unit_special_name(status_code: int) -> str:
    """
    Returns the string description for a given WiTE2 status code.
    Defaults to 'Unk' if the code is not in the lookup table.
    """
    return UNIT_SPECIAL_LOOKUP.get(status_code, f"Unk ({status_code})")

# Explicitly declared lookup for WiTE2 Device Types
# Key: Device Type Integer, Value: Description String
DEVICE_TYPE_LOOKUP: dict[int, str] = {
    0: "aircraft cannon",
    1: "man weapon",
    2: "squad weapon",
    3: "Hvy squad weapon",
    4: "AA weapon",
    5: "Lt gun",
    6: "Md gun",
    7: "Hvy gun",
    8: "Flame",
    9: "AA Rocket",
    10: "naval gun",
    11: "air-to-air rocket",
    12: "incendiary bomb",
    13: "GP bomb/rocket",
    14: "factory",
    15: "drop tank",
    16: "RADAR detector",
    17: "RADAR jammer",
    18: "Air navigation",
    19: "Air RADAR",
    20: "Ground RADAR",
    21: "ELINT",
    22: "Balloon",
    23: "Flak",
    24: "Torpedo",
    25: "DP Gun",
    26: "ASW",
    27: "Mine",
    28: "Camera",
    29: "Naval RADAR"
}

def get_device_type_name(device_code: int) -> str:
    """
    Retrieves the description for a specific Device Type code.
    Returns 'Unk ' if the code is not found.
    """
    return DEVICE_TYPE_LOOKUP.get(device_code, f"Unk ({device_code})")

# Explicitly declared lookup for WiTE2 HQ Types
# Key: HQ Type Integer, Value: Description String
HQ_TYPE_LOOKUP: dict[int, str] = {
    0: "None",
    1: "HighCom (High Command)",
    2: "AG/Front (Army Group/Front)",
    3: "Army",
    4: "Corps",
    5: "AB (Air Base)",
    6: "Const (Construction)",
    7: "Amphib (Amphibious)"
}

def get_hq_type_description(type_code: int) -> str:
    """
    Retrieves the description for a specific HQ Type code.
    Returns 'Unk Type' if the code is not found in the dictionary.
    """
    return HQ_TYPE_LOOKUP.get(type_code, f"Unk ({type_code})")

# Explicitly declared lookup for WiTE2 Ground Element Types
# Key: Type ID (int), Value: Description (str)
GROUND_ELEMENT_TYPE_LOOKUP: dict[int, str] = {
    1: "Rifle Squad",
    2: "Infantry-AT",
    3: "Cavalry Squad",
    4: "Machinegun",
    5: "Mortar",
    6: "AT Gun",
    7: "Mech-Inf Squad",
    8: "Md Flak",
    9: "Artillery",
    10: "Naval Gun",
    11: "Armoured Car",
    12: "Lt Tank",
    13: "Md Tank",
    14: "Hvy Tank",
    15: "CS Tank",
    16: "Motor-Inf Squad",
    17: "Flame Tank",
    18: "Assault Gun",
    19: "Mech-Engr Squad",
    20: "Engineer Squad",
    21: "SP Artillery",
    22: "SP Flak",
    23: "HT AT-Gun",
    24: "HT MG/Mor",
    25: "HT CS-Mortar",
    26: "Special Forces",
    27: "Marine Commando",
    28: "Airborne Eng",
    29: "SP AAMG",
    30: "AAMG",
    31: "Rocket",
    32: "Hvy Artillery",
    33: "Lt Flak",
    34: "Hvy Flak",
    35: "DD Tank",
    36: "MSW Tank", # Minesweeper Tank
    37: "Engineer Tank",
    38: "Airborne Squad",
    39: "SP Inf-Gun",
    40: "SMG Squad",
    41: "Barge",
    42: "Air Landing Section",
    43: "Hvy AT Gun",
    44: "Lt AT Gun",
    45: "Hvy Infantry Gun",
    46: "Lt Artillery",
    47: "Airborne Tank",
    48: "Recon Jeep",
    49: "Motorcycle Squad",
    50: "Ski Squad",
    51: "Security Squad",
    52: "Partisan Squad",
    53: "Naval Rifle Squad",
    54: "Labour Squad",
    55: "HQ Troops",
    56: "Ammo Truck",
    57: "Lt Armour",
    58: "Hvy Mortar",
    59: "SP AT Gun",
    60: "Tank Destroyer",
    61: "Hvy Tank Destroyer",
    62: "Infantry Gun",
    63: "Infantry Tank",
    64: "Cavalry Tank",
    65: "Hvy Cavalry Tank",
    66: "Hvy Assault Tank",
    67: "Lt Tank Destroyer",
    68: "CS Cavalry Tank",
    69: "CS Infantry Tank",
    70: "Lt Armoured Car",
    71: "Naval Artillery",
    72: "CDL Tank",
    73: "Recon Halftrack",
    74: "Flamethrower",
    75: "Assault Tank",
    76: "Foreign Md Tank",
    77: "Foreign Lt Tank",
    78: "Foreign Flame Tank",
    79: "Foreign Lt TD",
    80: "Foreign Tank Destroyer",
    81: "Foreign Assault Gun",
    82: "Foreign SP Artillery",
    83: "Foreign Armoured Car",
    84: "Foreign SP Rocket", # Unarmored?
    85: "HT Mortar", # New to WiTE2
    86: "Super Hvy Artillery", # New to WiTE2
    87: "Chassis", # New to WiTE2
    88: "Mech Recon", # New to WiTE2
    89: "Lt Infantry", # New to WiTE2
    90: "Hvy SP Artillery", # New to WiTE2
    91: "CS Armored Car", # New to WiTE2
    92: "Hvy Armored Car", # New to WiTE2
    93: "Flame APC", # New to WiTE2
    94: "Troop Ship",
    95: "Cargo Ship",
    96: "Vehicle Repair",
    97: "Supply Dump",
    98: "Fuel Dump",
    99: "Support",
    100: "Air Support", # New to WiTE2
    101: "Manpower",
    102: "Hvy Industry",
    103: "Oil",
    104: "Fuel",
    105: "Synthetic Fuel",
    106: "Resource",
    107: "Artillery",
    108: "Vehicle",
    109: "Rail yard",
    110: "Port",
    111: "V-weapons Factory",
    112: "V-weapons launcher",
    113: "U-boat Factory",
    114: "U-boat Pen",
    115: "Assault Squad", # New to WiTE2
    116: "Static AT Gun", # New to WiTE2
    117: "Mech Cav", # New to WiTE2
    118: "MG Section" # Local Modification
}

def get_ground_elem_class_name(type_id: int) -> str:
    """
    Returns the string description for a Ground Element Type ID.
    Handles undefined ranges gracefully.
    """
    return GROUND_ELEMENT_TYPE_LOOKUP.get(type_id, f"Unk ({type_id})")

# Explicitly declared lookup for WiTE2 Device Sizes
# Key: Size Integer, Value: Category Description
DEVICE_SIZE_LOOKUP: dict[int, str] = {
    1: "Infantry, MGs, Mortars, Lt/Md Artillery, AT/AA Guns",
    2: "Hvy Artillery, AT/AA Guns",
    3: "Lt Tanks, Armoured Cars, Assault Guns, Hvy Artillery",
    4: "Md Tanks, Hvy Artillery",
    5: "Hvy/Super Hvy Tanks, Hvy Artillery, Siege Guns/Mortars"
}

def get_device_size_description(size_code: int) -> str:
    """
    Returns the descriptive category for a WiTE2 device size code.
    Handles the 5-10 range as a single category.
    """
    # Group sizes 5 through 10 maps into the 'Hvy/Super Hvy' category
    if 5 <= size_code <= 10:
        return DEVICE_SIZE_LOOKUP[5]

    return DEVICE_SIZE_LOOKUP.get(size_code, f"Unk ({size_code})")

# Explicitly declared lookup for WiTE2 Device Face Types
# Key: Face Type Integer, Value: Orientation Description
DEVICE_FACE_TYPE_LOOKUP: dict[int, str] = {
    0: "Fwd", # (forward)",
    1: "Side",
    2: "Rear",
    3: "Turret", # (turret/top turret)",
    4: "BT", # (ball/bottom turret)",
    5: "TR", # (top rear)",
    6: "BR", # (bottom rear)",
    7: "SM", # (swivel mount)",
    11: "Int", # (Internal bomb load)",
    12: "Ext", # (external bomb load)"
}

def get_device_face_type_name(face_code: int) -> str:
    """
    Retrieves the orientation description for a Device Face code.
    Defaults to 'Unk' if the code is outside the 0-12 range.
    """
    return DEVICE_FACE_TYPE_LOOKUP.get(face_code, f"Unk ({face_code})")
