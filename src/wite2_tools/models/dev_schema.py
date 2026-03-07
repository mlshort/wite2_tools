from enum import IntEnum

# pylint: disable=invalid-name
class DevColumn(IntEnum):
    """
    Device Column indices for WiTE2's _device.csv file.
    """
    ID = 0
    NAME = 1
    TYPE = 2
    SYM = 3
    LOAD_COST = 4  # number of pounds the device weighs
    RANGE = 5  # no idea how this is used
    EFFECT = 6
    PEN = 7  # Penetration
    """
    number of millimetres of armour plate the weapon can penetrate
    appears to be 0-degree (vertical) penetration at 100 meters
    """
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
