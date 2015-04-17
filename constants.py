# -*- coding: utf-8 -*-
"""Констаны, влияющие на игру"""

import os

NEAR_RADIUS = 20
RANDOM_POINT_BORDER = 42

FLOWER_HONEY_MIN = 100
FLOWER_HONEY_MAX = 200

BEE_HONEY_MAX = 100

BEE_HEALTH = 100
BEE_STING_VALUE = 100

BACKGROUND_COLOR = (87, 144, 40)
HONEY_METER_COLOR = (0, 255, 7)

PICTURES_PATH = os.path.join(os.path.dirname(__file__), 'data')

DEBUG = False

try:
    from constants_local import *
except ImportError:
    pass
