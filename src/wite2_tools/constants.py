"""
WiTE2 Global Constants and Enumerations
=======================================

This module defines global constants, game engine limits, and column
enumerations used throughout the `wite2_tools` package. Centralizing
these values ensures structural consistency and simplifies maintenance
across the various modifier, auditing, and analysis scripts.

Core Contents:
--------------
* Engine Limits: Defines hardcoded game engine limitations (e.g.,
  `MAX_SQUAD_SLOTS = 32`) to replace magic numbers in iterative loops
  and validation checks.
* Column Enumerations: Provides strongly typed `IntEnum` classes
  (`UnitColumn`, `OBColumn`, `GroundColumn`) that map game CSV column headers
  to their exact zero-based integer indices, enabling safe, readable,
  and highly performant row parsing.
"""
from enum import IntEnum

MIN_SQUAD_SLOTS: int = 0
MAX_SQUAD_SLOTS: int = 32
MAX_GROUND_MEN: int = 30
MAX_WPN_SLOTS: int = 10
# GC41 is configured to run from 22 Jun 1941 till 2 Aug 1945
# which is 216 turns
MAX_GAME_TURNS: int = 225
EXCESS_RESOURCE_MULTIPLIER: int = 5

# Map Coordinate Limits
MIN_X: int = 0
MIN_Y: int = 0
MAX_X: int = 378
MAX_Y: int = 354

GROUND_WPN_PREFIXES: list[str] = ["wpn ", "wpnNum ", "wpnAmmo ",
                                  "wpnRof ", "wpnAcc ", "wpnFace "]

UNIT_SQUAD_PREFIXES: list[str] = ["sqd.u", "sqd.num", "sqd.dis",
                                  "sqd.dam", "sqd.fat", "sqd.fired",
                                  "sqd.exp", "sqd.expAccum"]


class GroundColumn(IntEnum):
    """
    Column indexes for WiTE2's _ground.csv files
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
    SPEED = 12  # the speed of the device in miles per hour
    DUR = 13
    SIZE = 14
    RELIB = 15  # Reliability and Survivabiliy
# The first digit represents the reliability of the AFV when
# moving (if only 1 digit is shown the 1st digit is assumed to be 0).
# The higher the number, the less likely the AFV will become damaged during
# movement.
# The second digit is survivability, and the higher the survivability the less
# likely the AFV will be destroyed in combat during a special survival check as
# opposed to just being damaged.
    ARMOR = 16  # front armour thickness in millimetres
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
    WPN_0 = 32
    WPN_1 = 33
    WPN_2 = 34
    WPN_3 = 35
    WPN_4 = 36
    WPN_5 = 37
    WPN_6 = 38
    WPN_7 = 39
    WPN_8 = 40
    WPN_9 = 41
    WPN_NUM_0 = 42
    WPN_NUM_1 = 43
    WPN_NUM_2 = 44
    WPN_NUM_3 = 45
    WPN_NUM_4 = 46
    WPN_NUM_5 = 47
    WPN_NUM_6 = 48
    WPN_NUM_7 = 49
    WPN_NUM_8 = 50
    WPN_NUM_9 = 51
    WPN_AMMO_0 = 52
    WPN_AMMO_1 = 53
    WPN_AMMO_2 = 54
    WPN_AMMO_3 = 55
    WPN_AMMO_4 = 56
    WPN_AMMO_5 = 57
    WPN_AMMO_6 = 58
    WPN_AMMO_7 = 59
    WPN_AMMO_8 = 60
    WPN_AMMO_9 = 61
    WPN_ROF_0 = 62  # ROF is a negative modifier that is applied to vehicle
    # mounted devices to reflect the restrictions of operating the device
    # inside the vehicle
    WPN_ROF_1 = 63
    WPN_ROF_2 = 64
    WPN_ROF_3 = 65
    WPN_ROF_4 = 66
    WPN_ROF_5 = 67
    WPN_ROF_6 = 68
    WPN_ROF_7 = 69
    WPN_ROF_8 = 70
    WPN_ROF_9 = 71
    WPN_ACC_0 = 72
    WPN_ACC_1 = 73
    WPN_ACC_2 = 74
    WPN_ACC_3 = 75
    WPN_ACC_4 = 76
    WPN_ACC_5 = 77
    WPN_ACC_6 = 78
    WPN_ACC_7 = 79
    WPN_ACC_8 = 80
    WPN_ACC_9 = 81
    WPN_FACE_0 = 82
    WPN_FACE_1 = 83
    WPN_FACE_2 = 84
    WPN_FACE_3 = 85
    WPN_FACE_4 = 86
    WPN_FACE_5 = 87
    WPN_FACE_6 = 88
    WPN_FACE_7 = 89
    WPN_FACE_8 = 90
    WPN_FACE_9 = 91


class ObColumn(IntEnum):
    """
    Column indexes for WiTE2's _ob.csv files
    """
    ID = 0
    NAME = 1
    SUFFIX = 2
    NAT = 3
    FIRST_YEAR = 4
    FIRST_MONTH = 5
    LAST_YEAR = 6
    LAST_MONTH = 7
    TYPE = 8
    UPGRADE = 9
    OB_CLASS = 10
    ICON = 11
    DIVIDE_MULTI_ROLE = 12
    MTZ_TYPE = 13
    FORM_SIZE = 14
    SQD_0 = 15
    SQD_1 = 16
    SQD_2 = 17
    SQD_3 = 18
    SQD_4 = 19
    SQD_5 = 20
    SQD_6 = 21
    SQD_7 = 22
    SQD_8 = 23
    SQD_9 = 24
    SQD_10 = 25
    SQD_11 = 26
    SQD_12 = 27
    SQD_13 = 28
    SQD_14 = 29
    SQD_15 = 30
    SQD_16 = 31
    SQD_17 = 32
    SQD_18 = 33
    SQD_19 = 34
    SQD_20 = 35
    SQD_21 = 36
    SQD_22 = 37
    SQD_23 = 38
    SQD_24 = 39
    SQD_25 = 40
    SQD_26 = 41
    SQD_27 = 42
    SQD_28 = 43
    SQD_29 = 44
    SQD_30 = 45
    SQD_31 = 46
    SQD_NUM_0 = 47
    SQD_NUM_1 = 48
    SQD_NUM_2 = 49
    SQD_NUM_3 = 50
    SQD_NUM_4 = 51
    SQD_NUM_5 = 52
    SQD_NUM_6 = 53
    SQD_NUM_7 = 54
    SQD_NUM_8 = 55
    SQD_NUM_9 = 56
    SQD_NUM_10 = 57
    SQD_NUM_11 = 58
    SQD_NUM_12 = 59
    SQD_NUM_13 = 60
    SQD_NUM_14 = 61
    SQD_NUM_15 = 62
    SQD_NUM_16 = 63
    SQD_NUM_17 = 64
    SQD_NUM_18 = 65
    SQD_NUM_19 = 66
    SQD_NUM_20 = 67
    SQD_NUM_21 = 68
    SQD_NUM_22 = 69
    SQD_NUM_23 = 70
    SQD_NUM_24 = 71
    SQD_NUM_25 = 72
    SQD_NUM_26 = 73
    SQD_NUM_27 = 74
    SQD_NUM_28 = 75
    SQD_NUM_29 = 76
    SQD_NUM_30 = 77
    SQD_NUM_31 = 78


class UnitColumn(IntEnum):
    """
    Column indexes for WiTE2's _unit.csv files
    """
    ID = 0
    NAME = 1
    TYPE = 2
    NAT = 3
    PLAYER = 4
    X = 5
    Y = 6
    LEADER = 7
    MORALE = 8
    DELAY = 9
    HQ = 10
    HHQ = 11
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
    WITH_TURN_0 = 114
    WITH_DEST_0 = 115
    WITH_TURN_1 = 116
    WITH_DEST_1 = 117
    WITH_TURN_2 = 118
    WITH_DEST_2 = 119
    WITH_TURN_3 = 120
    WITH_DEST_3 = 121
    WITH_TURN_4 = 122
    WITH_DEST_4 = 123
    SQD_U0 = 124
    SQD_NUM0 = 125
    SQD_DIS0 = 126
    SQD_DAM0 = 127
    SQD_FAT0 = 128
    SQD_FIRED0 = 129
    SQD_EXP0 = 130
    SQD_EXP_ACCUM0 = 131
    SQD_U1 = 132
    SQD_NUM1 = 133
    SQD_DIS1 = 134
    SQD_DAM1 = 135
    SQD_FAT1 = 136
    SQD_FIRED1 = 137
    SQD_EXP1 = 138
    SQD_EXP_ACCUM1 = 139
    SQD_U2 = 140
    SQD_NUM2 = 141
    SQD_DIS2 = 142
    SQD_DAM2 = 143
    SQD_FAT2 = 144
    SQD_FIRED2 = 145
    SQD_EXP2 = 146
    SQD_EXP_ACCUM2 = 147
    SQD_U3 = 148
    SQD_NUM3 = 149
    SQD_DIS3 = 150
    SQD_DAM3 = 151
    SQD_FAT3 = 152
    SQD_FIRED3 = 153
    SQD_EXP3 = 154
    SQD_EXP_ACCUM3 = 155
    SQD_U4 = 156
    SQD_NUM4 = 157
    SQD_DIS4 = 158
    SQD_DAM4 = 159
    SQD_FAT4 = 160
    SQD_FIRED4 = 161
    SQD_EXP4 = 162
    SQD_EXP_ACCUM4 = 163
    SQD_U5 = 164
    SQD_NUM5 = 165
    SQD_DIS5 = 166
    SQD_DAM5 = 167
    SQD_FAT5 = 168
    SQD_FIRED5 = 169
    SQD_EXP5 = 170
    SQD_EXP_ACCUM5 = 171
    SQD_U6 = 172
    SQD_NUM6 = 173
    SQD_DIS6 = 174
    SQD_DAM6 = 175
    SQD_FAT6 = 176
    SQD_FIRED6 = 177
    SQD_EXP6 = 178
    SQD_EXP_ACCUM6 = 179
    SQD_U7 = 180
    SQD_NUM7 = 181
    SQD_DIS7 = 182
    SQD_DAM7 = 183
    SQD_FAT7 = 184
    SQD_FIRED7 = 185
    SQD_EXP7 = 186
    SQD_EXP_ACCUM7 = 187
    SQD_U8 = 188
    SQD_NUM8 = 189
    SQD_DIS8 = 190
    SQD_DAM8 = 191
    SQD_FAT8 = 192
    SQD_FIRED8 = 193
    SQD_EXP8 = 194
    SQD_EXP_ACCUM8 = 195
    SQD_U9 = 196
    SQD_NUM9 = 197
    SQD_DIS9 = 198
    SQD_DAM9 = 199
    SQD_FAT9 = 200
    SQD_FIRED9 = 201
    SQD_EXP9 = 202
    SQD_EXP_ACCUM9 = 203
    SQD_U10 = 204
    SQD_NUM10 = 205
    SQD_DIS10 = 206
    SQD_DAM10 = 207
    SQD_FAT10 = 208
    SQD_FIRED10 = 209
    SQD_EXP10 = 210
    SQD_EXP_ACCUM10 = 211
    SQD_U11 = 212
    SQD_NUM11 = 213
    SQD_DIS11 = 214
    SQD_DAM11 = 215
    SQD_FAT11 = 216
    SQD_FIRED11 = 217
    SQD_EXP11 = 218
    SQD_EXP_ACCUM11 = 219
    SQD_U12 = 220
    SQD_NUM12 = 221
    SQD_DIS12 = 222
    SQD_DAM12 = 223
    SQD_FAT12 = 224
    SQD_FIRED12 = 225
    SQD_EXP12 = 226
    SQD_EXP_ACCUM12 = 227
    SQD_U13 = 228
    SQD_NUM13 = 229
    SQD_DIS13 = 230
    SQD_DAM13 = 231
    SQD_FAT13 = 232
    SQD_FIRED13 = 233
    SQD_EXP13 = 234
    SQD_EXP_ACCUM13 = 235
    SQD_U14 = 236
    SQD_NUM14 = 237
    SQD_DIS14 = 238
    SQD_DAM14 = 239
    SQD_FAT14 = 240
    SQD_FIRED14 = 241
    SQD_EXP14 = 242
    SQD_EXP_ACCUM14 = 243
    SQD_U15 = 244
    SQD_NUM15 = 245
    SQD_DIS15 = 246
    SQD_DAM15 = 247
    SQD_FAT15 = 248
    SQD_FIRED15 = 249
    SQD_EXP15 = 250
    SQD_EXP_ACCUM15 = 251
    SQD_U16 = 252
    SQD_NUM16 = 253
    SQD_DIS16 = 254
    SQD_DAM16 = 255
    SQD_FAT16 = 256
    SQD_FIRED16 = 257
    SQD_EXP16 = 258
    SQD_EXP_ACCUM16 = 259
    SQD_U17 = 260
    SQD_NUM17 = 261
    SQD_DIS17 = 262
    SQD_DAM17 = 263
    SQD_FAT17 = 264
    SQD_FIRED17 = 265
    SQD_EXP17 = 266
    SQD_EXP_ACCUM17 = 267
    SQD_U18 = 268
    SQD_NUM18 = 269
    SQD_DIS18 = 270
    SQD_DAM18 = 271
    SQD_FAT18 = 272
    SQD_FIRED18 = 273
    SQD_EXP18 = 274
    SQD_EXP_ACCUM18 = 275
    SQD_U19 = 276
    SQD_NUM19 = 277
    SQD_DIS19 = 278
    SQD_DAM19 = 279
    SQD_FAT19 = 280
    SQD_FIRED19 = 281
    SQD_EXP19 = 282
    SQD_EXP_ACCUM19 = 283
    SQD_U20 = 284
    SQD_NUM20 = 285
    SQD_DIS20 = 286
    SQD_DAM20 = 287
    SQD_FAT20 = 288
    SQD_FIRED20 = 289
    SQD_EXP20 = 290
    SQD_EXP_ACCUM20 = 291
    SQD_U21 = 292
    SQD_NUM21 = 293
    SQD_DIS21 = 294
    SQD_DAM21 = 295
    SQD_FAT21 = 296
    SQD_FIRED21 = 297
    SQD_EXP21 = 298
    SQD_EXP_ACCUM21 = 299
    SQD_U22 = 300
    SQD_NUM22 = 301
    SQD_DIS22 = 302
    SQD_DAM22 = 303
    SQD_FAT22 = 304
    SQD_FIRED22 = 305
    SQD_EXP22 = 306
    SQD_EXP_ACCUM22 = 307
    SQD_U23 = 308
    SQD_NUM23 = 309
    SQD_DIS23 = 310
    SQD_DAM23 = 311
    SQD_FAT23 = 312
    SQD_FIRED23 = 313
    SQD_EXP23 = 314
    SQD_EXP_ACCUM23 = 315
    SQD_U24 = 316
    SQD_NUM24 = 317
    SQD_DIS24 = 318
    SQD_DAM24 = 319
    SQD_FAT24 = 320
    SQD_FIRED24 = 321
    SQD_EXP24 = 322
    SQD_EXP_ACCUM24 = 323
    SQD_U25 = 324
    SQD_NUM25 = 325
    SQD_DIS25 = 326
    SQD_DAM25 = 327
    SQD_FAT25 = 328
    SQD_FIRED25 = 329
    SQD_EXP25 = 330
    SQD_EXP_ACCUM25 = 331
    SQD_U26 = 332
    SQD_NUM26 = 333
    SQD_DIS26 = 334
    SQD_DAM26 = 335
    SQD_FAT26 = 336
    SQD_FIRED26 = 337
    SQD_EXP26 = 338
    SQD_EXP_ACCUM26 = 339
    SQD_U27 = 340
    SQD_NUM27 = 341
    SQD_DIS27 = 342
    SQD_DAM27 = 343
    SQD_FAT27 = 344
    SQD_FIRED27 = 345
    SQD_EXP27 = 346
    SQD_EXP_ACCUM27 = 347
    SQD_U28 = 348
    SQD_NUM28 = 349
    SQD_DIS28 = 350
    SQD_DAM28 = 351
    SQD_FAT28 = 352
    SQD_FIRED28 = 353
    SQD_EXP28 = 354
    SQD_EXP_ACCUM28 = 355
    SQD_U29 = 356
    SQD_NUM29 = 357
    SQD_DIS29 = 358
    SQD_DAM29 = 359
    SQD_FAT29 = 360
    SQD_FIRED29 = 361
    SQD_EXP29 = 362
    SQD_EXP_ACCUM29 = 363
    SQD_U30 = 364
    SQD_NUM30 = 365
    SQD_DIS30 = 366
    SQD_DAM30 = 367
    SQD_FAT30 = 368
    SQD_FIRED30 = 369
    SQD_EXP30 = 370
    SQD_EXP_ACCUM30 = 371
    SQD_U31 = 372
    SQD_NUM31 = 373
    SQD_DIS31 = 374
    SQD_DAM31 = 375
    SQD_FAT31 = 376
    SQD_FIRED31 = 377
    SQD_EXP31 = 378
    SQD_EXP_ACCUM31 = 379


class GroundElementType(IntEnum):
    RIFLE_SQUAD = 1
    INFANTRY_AT = 2
    CAVALRY_SQUAD = 3
    MACHINEGUN = 4
    MORTAR = 5
    AT_GUN = 6
    MECH_INF_SQUAD = 7
    MD_FLAK = 8
    ARTILLERY = 9
    NAVAL_GUN = 10
    ARMOURED_CAR = 11
    LT_TANK = 12
    MD_TANK = 13
    HVY_TANK = 14
    CS_TANK = 15
    MOTOR_INF_SQUAD = 16
    FLAME_TANK = 17
    ASSAULT_GUN = 18
    MECH_ENGR_SQUAD = 19
    ENGINEER_SQUAD = 20
    SP_ARTILLERY = 21
    SP_FLAK = 22
    HT_AT_GUN = 23
    HT_MG_MOR = 24
    HT_CS_MORTAR = 25
    SPECIAL_FORCES = 26
    MARINE_COMMANDO = 27
    AIRBORNE_ENG = 28
    SP_AAMG = 29
    AAMG = 30
    ROCKET = 31
    HVY_ARTILLERY = 32
    LT_FLAK = 33
    HVY_FLAK = 34
    DD_TANK = 35
    MSW_TANK = 36  # Minesweeper Tank
    ENGINEER_TANK = 37
    AIRBORNE_SQUAD = 38
    SP_INF_GUN = 39
    SMG_SQUAD = 40
    BARGE = 41
    AIR_LANDING_SECTION = 42
    HVY_AT_GUN = 43
    LT_AT_GUN = 44
    HVY_INFANTRY_GUN = 45
    LT_ARTILLERY = 46
    AIRBORNE_TANK = 47
    RECON_JEEP = 48
    MOTORCYCLE_SQUAD = 49
    SKI_SQUAD = 50
    SECURITY_SQUAD = 51
    PARTISAN_SQUAD = 52
    NAVAL_RIFLE_SQUAD = 53
    LABOUR_SQUAD = 54
    HQ_TROOPS = 55
    AMMO_TRUCK = 56
    LT_ARMOUR = 57
    HVY_MORTAR = 58
    SP_AT_GUN = 59
    TANK_DESTROYER = 60
    HVY_TANK_DESTROYER = 61
    INFANTRY_GUN = 62
    INFANTRY_TANK = 63
    CAVALRY_TANK = 64
    HVY_CAVALRY_TANK = 65
    HVY_ASSAULT_TANK = 66
    LT_TANK_DESTROYER = 67
    CS_CAVALRY_TANK = 68
    CS_INFANTRY_TANK = 69
    LT_ARMOURED_CAR = 70
    NAVAL_ARTILLERY = 71
    CDL_TANK = 72
    RECON_HALFTRACK = 73
    FLAMETHROWER = 74
    ASSAULT_TANK = 75
    FOREIGN_MD_TANK = 76
    FOREIGN_LT_TANK = 77
    FOREIGN_FLAME_TANK = 78
    FOREIGN_LT_TD = 79
    FOREIGN_TANK_DESTROYER = 80
    FOREIGN_ASSAULT_GUN = 81
    FOREIGN_SP_ARTILLERY = 82
    FOREIGN_ARMOURED_CAR = 83
    FOREIGN_SP_ROCKET = 84  # Unarmored?
    HT_MORTAR = 85  # New to WiTE2
    SUPER_HVY_ARTILLERY = 86  # New to WiTE2
    CHASSIS = 87  # New to WiTE2
    MECH_RECON = 88  # New to WiTE2
    LT_INFANTRY = 89  # New to WiTE2
    HVY_SP_ARTILLERY = 90  # New to WiTE2
    CS_ARMORED_CAR = 91  # New to WiTE2
    HVY_ARMORED_CAR = 92  # New to WiTE2
    FLAME_APC = 93  # New to WiTE2
    TROOP_SHIP = 94
    CARGO_SHIP = 95
    VEHICLE_REPAIR = 96
    SUPPLY_DUMP = 97
    FUEL_DUMP = 98
    SUPPORT = 99
    AIR_SUPPORT = 100  # New to WiTE2
    MANPOWER = 101
    HVY_INDUSTRY = 102
    OIL = 103
    FUEL = 104
    SYNTHETIC_FUEL = 105
    RESOURCE = 106
    ARTILLERY_PRODUCTION = 107
    VEHICLE = 108
    RAIL_YARD = 109
    PORT = 110
    V_WEAPONS_FACTORY = 111
    V_WEAPONS_LAUNCHER = 112
    U_BOAT_FACTORY = 113
    U_BOAT_PEN = 114
    ASSAULT_SQUAD = 115  # New to WiTE2
    STATIC_AT_GUN = 116  # New to WiTE2
    MECH_CAV = 117  # New to WiTE2
    MG_SECTION = 118  # Local Modification

    @property
    def is_combat_element(self) -> bool:
        """
        Determines if this GroundElementType is a combat unit element.
        Returns False for static infrastructure, factories, and resource pools.
        """
        non_combat_types = {
            GroundElementType.NAVAL_GUN,
            GroundElementType.NAVAL_ARTILLERY,
            GroundElementType.CHASSIS,
            GroundElementType.TROOP_SHIP,      # 94
            GroundElementType.CARGO_SHIP,      # 95
            GroundElementType.VEHICLE_REPAIR,  # 96
            GroundElementType.SUPPLY_DUMP,     # 97
            GroundElementType.FUEL_DUMP,       # 98
            GroundElementType.SUPPORT,         # 99
            GroundElementType.AIR_SUPPORT,     # 100
            GroundElementType.MANPOWER,              # 101
            GroundElementType.HVY_INDUSTRY,          # 102
            GroundElementType.OIL,                   # 103
            GroundElementType.FUEL,                  # 104
            GroundElementType.SYNTHETIC_FUEL,        # 105
            GroundElementType.RESOURCE,              # 106
            GroundElementType.ARTILLERY_PRODUCTION,  # 107
            GroundElementType.VEHICLE,               # 108
            GroundElementType.RAIL_YARD,             # 109
            GroundElementType.PORT,                  # 110
            GroundElementType.V_WEAPONS_FACTORY,     # 111
            GroundElementType.V_WEAPONS_LAUNCHER,    # 112
            GroundElementType.U_BOAT_FACTORY,        # 113
            GroundElementType.U_BOAT_PEN             # 114
        }

        return self not in non_combat_types


# pylint: disable=invalid-name
class DeviceCol(IntEnum):
    """
    Column indices for WiTE2's _device.csv file.
    """
    ID = 0
    NAME = 1
    TYPE = 2
    SYM = 3
    LOAD_COST = 4  # number of pounds the device weighs
    RANGE = 5  # no idea how this is used
    EFFECT = 6
    PEN = 7  # Penetration
    # number of millimetres of armour plate the weapon can penetrate
    # appears to be 0-degree (vertical) penetration at 100 meters
    ACC = 8  # Accuracy
    CEILING = 9  # Max Ceiling (in feet)
    ANTI_ARMOR = 10
    ANTI_SOFT = 11
    WARHEAD = 12  # Not displayed in the Editor (see below)
    ANTI_AIR = 13
    RG = 14  # Maximum Effective Range (meters for ground units)
    # the range is "feet" for aircraft
    ROF = 15  # Rate of Fire (can be negative)
    # a negative value would be scaled as RoF of 1 / x minutes, instead of
    # x / 1 minute.
    # Rate of Fire (ROF) is not used in the conventional military sense.
    # It indicates how many times a device will be allowed to fire during
    # the combat phase. The higher the number entered the better the ROF.
    HEAT = 16  # HEAT Pen
    # number of millimetres of armour plate the HEAT weapon can penetrate
    # at x range
    HVAP = 17  # HVAP Pen
    BLAST = 18
    DUD_RATE = 19  # Not displayed in the Editor
    COUNTER_DEV = 20
    COUNTER_DT = 21
    COUNTER_VAL = 22
    COUNTER_T_VAL = 23
    EFF_CEILING = 24

# 1. Warhead: The Caliber Scale
#
# The warhead value is the primary driver of explosive power and is calculated
# based on the internal volume/caliber of the projectile.
#
#    Linear Scaling for Anti-Tank (AT) Guns: For most standard tank and AT
# guns, the warhead value is almost always roughly Caliber ÷ 15.
# (e.g., 75mm = 4; 88mm = 5; 50mm = 3).
#
#    Artillery & Large Bore: As caliber increases, the scale jumps to reflect
# the non-linear increase in explosive filler. A 150mm howitzer (ID 416) is a
# ssigned an 8, and the massive 600mm Karl-Gerät (ID 441) jumps to 30.
#
#    Small Arms: Machine guns and rifles generally have a warhead of 0,
# indicating they do not rely on chemical energy (explosives) to deal damage.

# 2. Blast: Explosive Radius and Suppression
#
# The blast value correlates strongly with warhead (correlation coefficient of
# 0.30, but nearly 1:1 in behavior for high-caliber weapons) and represents
# the "footprint" of the explosion.
#
#    Formulaic Consistency: For field guns and howitzers, blast is typically
# warhead + 2. (e.g., the 88mm has a warhead of 5 and a blast of 5; the 150mm
# has a warhead of 8 and a blast of 10).
#
#    Rockets vs. Shells: Rockets like the 150mm NbW 41 (ID 430) have a higher
# blast (13) than shells of the same caliber (10), likely to simulate the
# thinner walls of rocket casings which allowed for more explosive filler and
# a larger burst radius at the expense of penetration.

# pylint: disable=invalid-name
class DeviceType(IntEnum):
    """
    Mapping for the 'type' column in WiTE2's _device.csv.
    """
    AIRCRAFT_CANNON = 0
    MAN_WEAPON = 1
    SQUAD_WEAPON = 2
    HVY_SQUAD_WEAPON = 3
    AA_WEAPON = 4
    LT_GUN = 5
    MD_GUN = 6
    HVY_GUN = 7
    FLAME = 8
    AA_ROCKET = 9
    NAVAL_GUN = 10
    AIR_TO_AIR_ROCKET = 11
    INCENDIARY_BOMB = 12
    GP_BOMB_ROCKET = 13
    FACTORY = 14
    DROP_TANK = 15
    RADAR_DETECTOR = 16
    RADAR_JAMMER = 17
    AIR_NAVIGATION = 18
    AIR_RADAR = 19
    GROUND_RADAR = 20
    ELINT = 21
    BALLOON = 22
    FLAK = 23
    TORPEDO = 24
    DP_GUN = 25
    ASW = 26
    MINE = 27
    CAMERA = 28
    NAVAL_RADAR = 29

    @classmethod
    def get_description(cls, value: int) -> str:
        """Returns the original descriptive string for the type ID."""
        descriptions = {
            0: "Aircraft cannon", 1: "Man weapon", 2: "Squad weapon",
            3: "Hvy squad weapon", 4: "AA weapon", 5: "Lt gun",
            6: "Md gun", 7: "Hvy gun", 8: "Flame", 9: "AA Rocket",
            10: "Naval gun", 11: "Air-to-air rocket", 12: "Incendiary bomb",
            13: "GP bomb/rocket", 14: "Factory", 15: "Drop tank",
            16: "RADAR detector", 17: "RADAR jammer", 18: "Air navigation",
            19: "Air RADAR", 20: "Ground RADAR", 21: "ELINT",
            22: "Balloon", 23: "Flak", 24: "Torpedo", 25: "DP Gun",
            26: "ASW", 27: "Mine", 28: "Camera", 29: "Naval RADAR"
        }
        return descriptions.get(value, "Unknown")


# pylint: disable=invalid-name
class AircraftCol(IntEnum):
    """
    Column indices for WiTE2's _aircraft.csv file.
    """
    ID = 0
    NAME = 1
    MAX_ALT = 2
    NAT = 3
    SYM = 4
    MAX_SPEED = 5
    MAX_SPEED_ALT = 6   # the optimum altitude to achieve Max Speed
    ZERO_ALT_SPEED = 7  # max speed at sea level
    MAX_ALT_SPEED = 8   # max speed at highest altitude
    CRU_SPEED = 9  # Cruise Speed
    CLIMB = 10  # climb rate in terms of feet per minute
    MAX_LOAD = 11  # pounds
    ENDURANCE = 12  # minutes
    RANGE = 13
    YEAR = 14
    MVR = 15
    ARMOR = 16
    DURAB = 17  # Aircraft damage points are measured against the aircraft
# durability rating to determine if the aircraft is destroyed or just damaged
    MONTH = 18
    TYPE = 19  # mapped to AirCraftType (below)
    BLANK = 20
    UPGRADE = 21
    CREW = 22
    SORTIE_AMMO = 23
    SORTIE_FUEL = 24
    BUILD_COST = 25
    POOL = 26
    BUILD_LIMIT = 27  # How many frames are converted each turn
    MAX_IMPORT = 28
    IMPORT_FROM = 29
    LAST_YEAR = 30
    LAST_MONTH = 31
    RELIB = 32  # All aircraft have a reliability rating which ranges from
# “really good” (lower numbers) to “really bad” (higher numbers). These
# reliability ratings are checked when aircraft conduct a mission with those
# that fail the reliability check becoming damaged.
    PHOTO = 33
    EXP_RATE = 34
    ENGINE_NUM = 35
    AIR_PROFILE = 36
    WPN_0 = 37
    WPN_1 = 38
    WPN_2 = 39
    WPN_3 = 40
    WPN_4 = 41
    WPN_5 = 42
    WPN_6 = 43
    WPN_7 = 44
    WPN_8 = 45
    WPN_9 = 46
    WPN_NUM_0 = 47
    WPN_NUM_1 = 48
    WPN_NUM_2 = 49
    WPN_NUM_3 = 50
    WPN_NUM_4 = 51
    WPN_NUM_5 = 52
    WPN_NUM_6 = 53
    WPN_NUM_7 = 54
    WPN_NUM_8 = 55
    WPN_NUM_9 = 56
    WPN_FACE_0 = 57
    WPN_FACE_1 = 58
    WPN_FACE_2 = 59
    WPN_FACE_3 = 60
    WPN_FACE_4 = 61
    WPN_FACE_5 = 62
    WPN_FACE_6 = 63
    WPN_FACE_7 = 64
    WPN_FACE_8 = 65
    WPN_FACE_9 = 66
    # ... Weapon Sets (WS0 through WS4) follow ...
    WS0_WPN_0 = 67
    WS0_WPN_NUM_0 = 68
    # [322 total columns]
    WS4_SPD_MOD = 321


# pylint: disable=invalid-name
class AircraftType(IntEnum):
    """
    Mapping for the 'type' column in _aircraft.csv and
    'airType' in _airgroup.csv.
    """
    FIGHTER = 0
    FIGHTER_BOMBER = 1
    NIGHT_FIGHTER = 2
    TACTICAL_BOMBER = 3
    LEVEL_BOMBER = 4
    RECON = 5
    JET_FIGHTER = 6
    EW = 7
    TRANSPORT = 8
    PATROL = 9
    FLOAT_PLANE = 10
    FLOAT_FIGHTER = 11
    TORPEDO_BOMBER = 12
    AIR_FRAME = 13  # New for WiTE2


# pylint: disable=invalid-name
class AirGroupCol(IntEnum):
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


class Elem(IntEnum):
    """
    Work in progress for convenience
    """
    PZ_IB = 1
    PZ_IIC = 2
    PZ_IIF = 3
    STUG_IIIB = 28
    ARMORED_HMG_SECTION_40 = 62
    ARMORED_HMG_SECTION_43 = 65
    MMG34 = 79
    MMG42 = 80
    RIFLE_40 = 81
    PIONEER_39 = 84
    CAV_39 = 88
    MOTORCYCLE = 89
    MOT_RIFLE_40 = 94
    MOT_RIFLE_40_P = 95
    PZGR_40 = 98
    ARMORED_PIONEER_40 = 101
    KFZ4_TWIN_MG34 = 574
    KFZ4_TWIN_MG42 = 575
    HMG_SECTION_40 = 600
    HMG_SECTION_42 = 601
    SUPPORT_GER = 1490


# pylint: disable=invalid-name
class OB(IntEnum):
    """
    Work in progress for convenience
    """
    TIER_1A_PZ_DIV_41 = 33
    TIER_1B_PZ_DIV_41 = 35
    TIER_1C_PZ_DIV_41 = 37
    TIER_1_PZ_DIV_42a = 39
    TIER_2_PZ_DIV_41 = 47
    TIER_3_PZ_DIV_41 = 56
    TIER_4a_PZ_DIV_41 = 65
    TIER_1_MOT_DIV_41 = 250
    TIER_2_MOT_DIV_41 = 258
    WAVE_1_INF_DIV_41 = 389
    WAVE_1_INF_DIV_42 = 390
    WAVE_1_INF_DIV_43 = 391
    WAVE_3_INF_DIV_41 = 393
    WAVE_4_INF_DIV_41 = 398
    WAVE_5_INF_DIV_41 = 402
    WAVE_6_INF_DIV_41 = 407
    WAVE_7_INF_DIV_41 = 412
    WAVE_8_INF_DIV_41 = 416
    WAVE_11_INF_DIV_41 = 420
    WAVE_12_INF_DIV_41 = 424
    WAVE_17_INF_DIV_41 = 438
    AIR_LANDING_DIV_41 = 483
    MOT_MG_BN_41 = 577
    WAVE_12_LIGHT_DIV_41 = 599
    MTN_DIV_41 = 606
    CAV_DIV_41 = 727


class NatCode(IntEnum):
    """
    WiTE2's Nat Codes
    """
    GER = 1
    FIN = 2
    ITA = 3
    RUM = 4
    HUN = 5
    SLO = 6
    CZE = 8
    BEL = 9
    NET = 10
    POL = 11
    SU = 12
    USA = 13
    BRI = 15
    GRE = 16
    NOR = 17
    YUG = 18
    CAN = 19
    IND = 20
    AUS = 21
    FRE = 22
    SA = 23
    WA = 24
    BRA = 25
    COM = 26
    FRA = 27
    DEN = 32
    SWE = 41
