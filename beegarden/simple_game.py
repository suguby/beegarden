# -*- coding: utf-8 -*-
"""simple game example"""

from beegarden.core import Beegarden
from beegarden.my_bee import MyBee

scene = Beegarden(
    name="My little garden",
    flowers_count=10,
    theme_mod_path='beegarden.themes.default',
)

bee = MyBee()  # bee born

scene.go()  # let the world revolves around you

