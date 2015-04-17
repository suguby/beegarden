# -*- coding: utf-8 -*-
"""Пакет для игры программистов в пасеку - чья команда пчел быстрее соберет мёд?"""

__all__ = ['core', 'geometry', 'engine']
from .core import Bee, Scene, HoneyHolder
from .geometry import Point, Vector
from .engine import GameObject
