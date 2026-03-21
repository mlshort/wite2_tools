"""
_unit.csv Mapping Reference:
| Constant       | CSV Header | Index | Notes                     |
|----------------|------------|-------|---------------------------|
| ID_COL         | id         | 0     | Unique Identifier         |
| NAME_COL       | name       | 1     | Display Name              |
| TYPE_COL       | type       | 2     | FK: _ob.csv -> id         |
| NAT_COL        | nat        | 3     | Nationality index         |
"""
from enum import IntEnum
from typing import Final


class UnitColumn(IntEnum):
    """
    Schema for WiTE2's _unit.csv files (380 columns).

    Attributes:
        ID: Unique unit identifier (Index 0).
        TYPE: Linkage ID to the _ob.csv table (Index 2).
        NAT: Nationality index (Index 3).
    """
    ID = 0
    NAME = 1
    TYPE = 2  # References _ob.id
    # maps to nat types
    NAT = 3
    PLAYER = 4
    X = 5
    Y = 6
    LEADER = 7
    MORALE = 8
    # num of weeks until arrival
    DELAY = 9
    # maps to hq type
    HQ = 10
    # maps to _unit.id of assigned HQ
    HHQ = 11
    # can be negative
    COMBAT_SUPPORT = 12
    MEN = 13
    SUP = 14
    S_NEED = 15
    MOVED = 16
    MOVE = 17
    CUR = 18
    MOTORIZED = 19
    SUB_TO = 20
    HQ_FUEL = 21
    NEXT = 22
    FRONT = 23
    A_NEED = 24
    AMMO = 25
    CUR_STRAT = 26
    LOADED = 27
    ROLE = 28
    FROZEN = 29
    WITHDRAW = 30
    IN_SUPPLY = 31
    WON = 32
    LOST = 33
    GUARDS = 34
    HQ_SUPPORT = 35
    HQ_SUPPLY = 36
    V_NEED = 37
    TRUCK = 38
    TX = 39
    TY = 40
    FAT = 41
    SYM = 42
    DAM = 43
    DETECT = 44
    MAX_DETECT = 45
    HIDDEN = 46
    FUEL = 47
    F_NEED = 48
    SUPPORT = 49
    SPT_NEED = 50
    ROUTED = 51
    FIGHTING = 52
    AX = 53
    AY = 54
    MAX_TOE = 55
    WAS_STATIC = 56
    BUILD_UP = 57
    RESERVE = 58
    CORPS = 59
    CORPS_GDS = 60
    DIVN0 = 61
    DIVN1 = 62
    DIVN2 = 63
    DIV_GDS0 = 64
    DIV_GDS1 = 65
    DIV_GDS2 = 66
    DIV_WON0 = 67
    DIV_WON1 = 68
    DIV_WON2 = 69
    DIV_LOST0 = 70
    DIV_LOST1 = 71
    DIV_LOST2 = 72
    COMBAT_VALUE0 = 73  # Att CV
    COMBAT_VALUE1 = 74  # Def CV
    RECON_VALUE0 = 75
    RECON_VALUE1 = 76
    AIR_HQ = 77
    AIR_SUPPLY_TONS = 78
    AIR_SUPPLY_RG = 79
    WITHDRAW_TURN = 80
    SUPPLY_DUMP_CITY = 81
    AT_CITY = 82
    AMPHIB_PREP = 83
    AMPHIB_ORDERS = 84
    INTERDICT = 85
    TRUCKS_USED = 86
    HQ_CHAIN = 87
    ATX = 88
    ATY = 89
    GARRISON = 90
    HQ_CHANGE = 91
    STACK_TOP = 92
    AWX = 93
    AWY = 94
    AUTO_AV_SUPPORT = 95
    PRIORITY = 96
    AIR_TASK_DETAIL = 97
    PTX = 98
    PTY = 99
    PARA_PREP = 100
    JUMP = 101
    UNIT_ARRIVED = 102
    HQ_COLOR = 103  # Can be very large
    RENAME_UNIT = 104
    RENAME_VALID = 105
    RENAME_CONDITION = 106
    COM_PREP = 107
    INFO_LINK = 108
    THEATER_BOX = 109
    TH_BOX_LOCK = 110
    ATTACHED_TO_FORT = 111
    UNIT_TAG_ID = 112
    NO_UNIT_REBUILD = 113

    # --- Withdraw / Destination ---
    WITH_TURN_0, WITH_DEST_0 = 114, 115
    WITH_TURN_1, WITH_DEST_1 = 116, 117
    WITH_TURN_2, WITH_DEST_2 = 118, 119
    WITH_TURN_3, WITH_DEST_3 = 120, 121
    WITH_TURN_4, WITH_DEST_4 = 122, 123

    # --- Squad Detailed Stats ---
    SQD_U0, SQD_NUM0, SQD_DIS0, SQD_DAM0 = 124, 125, 126, 127
    SQD_FAT0, SQD_FIRED0, SQD_EXP0, SQD_EXP_ACCUM0 = 128, 129, 130, 131

    SQD_U1, SQD_NUM1, SQD_DIS1, SQD_DAM1 = 132, 133, 134, 135
    SQD_FAT1, SQD_FIRED1, SQD_EXP1, SQD_EXP_ACCUM1 = 136, 137, 138, 139

    SQD_U2, SQD_NUM2, SQD_DIS2, SQD_DAM2 = 140, 141, 142, 143
    SQD_FAT2, SQD_FIRED2, SQD_EXP2, SQD_EXP_ACCUM2 = 144, 145, 146, 147

    SQD_U3, SQD_NUM3, SQD_DIS3, SQD_DAM3 = 148, 149, 150, 151
    SQD_FAT3, SQD_FIRED3, SQD_EXP3, SQD_EXP_ACCUM3 = 152, 153, 154, 155

    SQD_U4, SQD_NUM4, SQD_DIS4, SQD_DAM4 = 156, 157, 158, 159
    SQD_FAT4, SQD_FIRED4, SQD_EXP4, SQD_EXP_ACCUM4 = 160, 161, 162, 163

    SQD_U5, SQD_NUM5, SQD_DIS5, SQD_DAM5 = 164, 165, 166, 167
    SQD_FAT5, SQD_FIRED5, SQD_EXP5, SQD_EXP_ACCUM5 = 168, 169, 170, 171

    SQD_U6, SQD_NUM6, SQD_DIS6, SQD_DAM6 = 172, 173, 174, 175
    SQD_FAT6, SQD_FIRED6, SQD_EXP6, SQD_EXP_ACCUM6 = 176, 177, 178, 179

    SQD_U7, SQD_NUM7, SQD_DIS7, SQD_DAM7 = 180, 181, 182, 183
    SQD_FAT7, SQD_FIRED7, SQD_EXP7, SQD_EXP_ACCUM7 = 184, 185, 186, 187

    SQD_U8, SQD_NUM8, SQD_DIS8, SQD_DAM8 = 188, 189, 190, 191
    SQD_FAT8, SQD_FIRED8, SQD_EXP8, SQD_EXP_ACCUM8 = 192, 193, 194, 195

    SQD_U9, SQD_NUM9, SQD_DIS9, SQD_DAM9 = 196, 197, 198, 199
    SQD_FAT9, SQD_FIRED9, SQD_EXP9, SQD_EXP_ACCUM9 = 200, 201, 202, 203

    SQD_U10, SQD_NUM10, SQD_DIS10, SQD_DAM10 = 204, 205, 206, 207
    SQD_FAT10, SQD_FIRED10, SQD_EXP10, SQD_EXP_ACCUM10 = 208, 209, 210, 211

    SQD_U11, SQD_NUM11, SQD_DIS11, SQD_DAM11 = 212, 213, 214, 215
    SQD_FAT11, SQD_FIRED11, SQD_EXP11, SQD_EXP_ACCUM11 = 216, 217, 218, 219

    SQD_U12, SQD_NUM12, SQD_DIS12, SQD_DAM12 = 220, 221, 222, 223
    SQD_FAT12, SQD_FIRED12, SQD_EXP12, SQD_EXP_ACCUM12 = 224, 225, 226, 227

    SQD_U13, SQD_NUM13, SQD_DIS13, SQD_DAM13 = 228, 229, 230, 231
    SQD_FAT13, SQD_FIRED13, SQD_EXP13, SQD_EXP_ACCUM13 = 232, 233, 234, 235

    SQD_U14, SQD_NUM14, SQD_DIS14, SQD_DAM14 = 236, 237, 238, 239
    SQD_FAT14, SQD_FIRED14, SQD_EXP14, SQD_EXP_ACCUM14 = 240, 241, 242, 243

    SQD_U15, SQD_NUM15, SQD_DIS15, SQD_DAM15 = 244, 245, 246, 247
    SQD_FAT15, SQD_FIRED15, SQD_EXP15, SQD_EXP_ACCUM15 = 248, 249, 250, 251

    SQD_U16, SQD_NUM16, SQD_DIS16, SQD_DAM16 = 252, 253, 254, 255
    SQD_FAT16, SQD_FIRED16, SQD_EXP16, SQD_EXP_ACCUM16 = 256, 257, 258, 259

    SQD_U17, SQD_NUM17, SQD_DIS17, SQD_DAM17 = 260, 261, 262, 263
    SQD_FAT17, SQD_FIRED17, SQD_EXP17, SQD_EXP_ACCUM17 = 264, 265, 266, 267

    SQD_U18, SQD_NUM18, SQD_DIS18, SQD_DAM18 = 268, 269, 270, 271
    SQD_FAT18, SQD_FIRED18, SQD_EXP18, SQD_EXP_ACCUM18 = 272, 273, 274, 275

    SQD_U19, SQD_NUM19, SQD_DIS19, SQD_DAM19 = 276, 277, 278, 279
    SQD_FAT19, SQD_FIRED19, SQD_EXP19, SQD_EXP_ACCUM19 = 280, 281, 282, 283

    SQD_U20, SQD_NUM20, SQD_DIS20, SQD_DAM20 = 284, 285, 286, 287
    SQD_FAT20, SQD_FIRED20, SQD_EXP20, SQD_EXP_ACCUM20 = 288, 289, 290, 291

    SQD_U21, SQD_NUM21, SQD_DIS21, SQD_DAM21 = 292, 293, 294, 295
    SQD_FAT21, SQD_FIRED21, SQD_EXP21, SQD_EXP_ACCUM21 = 296, 297, 298, 299

    SQD_U22, SQD_NUM22, SQD_DIS22, SQD_DAM22 = 300, 301, 302, 303
    SQD_FAT22, SQD_FIRED22, SQD_EXP22, SQD_EXP_ACCUM22 = 304, 305, 306, 307

    SQD_U23, SQD_NUM23, SQD_DIS23, SQD_DAM23 = 308, 309, 310, 311
    SQD_FAT23, SQD_FIRED23, SQD_EXP23, SQD_EXP_ACCUM23 = 312, 313, 314, 315

    SQD_U24, SQD_NUM24, SQD_DIS24, SQD_DAM24 = 316, 317, 318, 319
    SQD_FAT24, SQD_FIRED24, SQD_EXP24, SQD_EXP_ACCUM24 = 320, 321, 322, 323

    SQD_U25, SQD_NUM25, SQD_DIS25, SQD_DAM25 = 324, 325, 326, 327
    SQD_FAT25, SQD_FIRED25, SQD_EXP25, SQD_EXP_ACCUM25 = 328, 329, 330, 331

    SQD_U26, SQD_NUM26, SQD_DIS26, SQD_DAM26 = 332, 333, 334, 335
    SQD_FAT26, SQD_FIRED26, SQD_EXP26, SQD_EXP_ACCUM26 = 336, 337, 338, 339

    SQD_U27, SQD_NUM27, SQD_DIS27, SQD_DAM27 = 340, 341, 342, 343
    SQD_FAT27, SQD_FIRED27, SQD_EXP27, SQD_EXP_ACCUM27 = 344, 345, 346, 347

    SQD_U28, SQD_NUM28, SQD_DIS28, SQD_DAM28 = 348, 349, 350, 351
    SQD_FAT28, SQD_FIRED28, SQD_EXP28, SQD_EXP_ACCUM28 = 352, 353, 354, 355

    SQD_U29, SQD_NUM29, SQD_DIS29, SQD_DAM29 = 356, 357, 358, 359
    SQD_FAT29, SQD_FIRED29, SQD_EXP29, SQD_EXP_ACCUM29 = 360, 361, 362, 363

    SQD_U30, SQD_NUM30, SQD_DIS30, SQD_DAM30 = 364, 365, 366, 367
    SQD_FAT30, SQD_FIRED30, SQD_EXP30, SQD_EXP_ACCUM30 = 368, 369, 370, 371

    SQD_U31, SQD_NUM31, SQD_DIS31, SQD_DAM31 = 372, 373, 374, 375
    SQD_FAT31, SQD_FIRED31, SQD_EXP31, SQD_EXP_ACCUM31 = 376, 377, 378, 379

NUM_COLS : Final[int] = len(UnitColumn)
SQD_SLOTS : Final[int] = 32
ATTRS_PER_SQD: Final[int] = 8

"""
Unit Column Aliases
-------------------
These constants provide a clean interface for accessing specific indices
within the _unit.csv structure.
"""
ID_COL: Final[int]          = UnitColumn.ID
NAME_COL: Final[int]        = UnitColumn.NAME
#: The TYPE_COL maps directly to the 'id' field in the _ob.csv file.
TYPE_COL: Final[int]        = UnitColumn.TYPE
NAT_COL : Final[int]        = UnitColumn.NAT
TRUCK_COL : Final[int]      = UnitColumn.TRUCK
SUPPORT_COL : Final[int]    = UnitColumn.SUPPORT
SPT_NEED_COL : Final[int]   = UnitColumn.SPT_NEED
HQ_SUPPORT_COL : Final[int] = UnitColumn.HQ_SUPPORT

# Interleaved stride (8 attributes per squad slot)
# pylint: disable=invalid-name
SQD_U0_COL: Final[int]         = UnitColumn.SQD_U0
SQD_NUM0_COL : Final[int]      = UnitColumn.SQD_NUM0
SQD_DIS0_COL: Final[int]       = UnitColumn.SQD_DIS0
SQD_DAM0_COL: Final[int]       = UnitColumn.SQD_DAM0
SQD_FAT0_COL: Final[int]       = UnitColumn.SQD_FAT0
SQD_FIRED0_COL: Final[int]     = UnitColumn.SQD_FIRED0
SQD_EXP0_COL: Final[int]       = UnitColumn.SQD_EXP0
SQD_EXP_ACCUM0_COL: Final[int] = UnitColumn.SQD_EXP_ACCUM0


def gen_unit_column_names() -> list[str]:
    """
    Generates the mapping for the UnitColumn IntEnum.
    """
    cols: list[str] = [
        "id", "name", "type", "nat", "player", "x", "y", "leader", "morale",
        "delay", "hq", "hhq", "combatSupport", "men", "sup", "sNeed", "moved",
        "move", "cur", "motorized", "subTo", "hqFuel", "next", "front", "aNeed",
        "ammo", "curStrat", "loaded", "role", "frozen", "withdraw", "inSupply",
        "won", "lost", "guards", "hqSupport", "hqSupply", "vNeed", "truck", "tx",
        "ty", "fat", "sym", "dam", "detect", "maxDetect", "hidden", "fuel",
        "fNeed", "support", "sptNeed", "routed", "fighting", "ax", "ay", "maxTOE",
        "wasStatic", "buildUp", "reserve", "corps", "corpsGds", "divn0", "divn1",
        "divn2", "divGds0", "divGds1", "divGds2", "divWon0", "divWon1", "divWon2",
        "divLost0", "divLost1", "divLost2", "combatValue0", "combatValue1",
        "reconValue0", "reconValue1", "airHq", "airSupplyTons", "airSupplyRg",
        "withdrawTurn", "supplyDumpCity", "atCity", "amphibPrep", "amphibOrders",
        "interdict", "trucksUsed", "hqChain", "atx", "aty", "garrison", "hqChange",
        "stackTop", "awx", "awy", "autoAvSupport", "priority", "airTaskDetail",
        "ptx", "pty", "paraPrep", "jump", "unitArrived", "hqColor", "renameUnit",
        "renameValid", "renameCondition", "comPrep", "infoLink", "theaterBox",
        "thBoxLock", "attachedToFort", "unitTagID", "noUnitRebuild"
    ]
    # Withdrawal turns (114 to 123)
    for i in range(5):
        cols.extend([f"withTurn {i}", f"withDest {i}"])
    # Squad blocks (124 to 379)
    sqd_attrs: list[str] = ["u", "num", "dis", "dam",
                            "fat", "fired", "exp", "expAccum"]
    for i in range(SQD_SLOTS):
        for attr in sqd_attrs:
            cols.append(f"sqd.{attr}{i}")
    return cols



