# -*- coding: utf-8 -*-
"""Основной модуль пасеки"""

import random
from common import ObjectToSprite
from constants import BEE_HONEY_MAX, FLOWER_HONEY_MIN, FLOWER_HONEY_MAX
from engine import GameObject, Scene

from geometry import Point
from user_interface import BaseSprite, HoneyMeter, UserInterface


class HoneyHolder():
    """Класс объекта, который может нести мёд"""
    _honey_speed = 1

    honey = property(lambda self: self._honey, doc="""Количество мёда у объекта""")

    def __init__(self, honey_loaded, honey_max):
        """Задать начальние значения: honey_loaded - сколько изначально мёда, honey_max - максимум"""
        self._honey = honey_loaded
        if honey_max == 0:
            raise Exception("honey_max can't be zero!")
        self._honey_max = honey_max

        self._honey_source = None
        self._honey_state = 'hold'

    def _end_exchange(self, event):
        self._honey_source = None
        self._honey_state = 'hold'
        event()

    def _update(self, is_moving=False):
        """Внутренняя функция для обновления переменных отображения"""
        if is_moving:
            self._honey_source = None
            self._honey_state = 'hold'
            return
        elif self._honey_state == 'loading':
            honey = self._honey_source._get_honey()
            if not honey or not self._put_honey(honey):
                self._end_exchange(event=self.on_honey_loaded)
        elif self._honey_state == 'unloading':
            honey = self._get_honey()
            if not honey or not self._honey_source._put_honey(honey):
                self._end_exchange(event=self.on_honey_unloaded)

    def _get_honey(self):
        if self._honey > self._honey_speed:
            self._honey -= self._honey_speed
            return self._honey_speed
        elif self._honey > 0:
            value = self._honey
            self._honey = 0
            return value
        return 0.0

    def _put_honey(self, value):
        self._honey += value
        if self._honey > self._honey_max:
            self._honey = self._honey_max
            return False
        return True

    def on_honey_loaded(self):
        """Обработчик события 'мёд загружен' """
        pass

    def on_honey_unloaded(self):
        """Обработчик события 'мёд разгружен' """
        pass

    def load_honey_from(self, source):
        """Загрузить мёд от ... """
        self._honey_state = 'loading'
        self._honey_source = source

    def unload_honey_to(self, target):
        """Разгрузить мёд в ... """
        self._honey_state = 'unloading'
        self._honey_source = target

    def is_full(self):
        """полностью заполнен?"""
        return self.honey >= self._honey_max


class Bee(HoneyHolder, GameObject):
    """Пчела. Может летать по экрану и носить мёд."""
    _container = []
    team = 1  # к какой команде пчел принадлежит
    my_beehive = None
    flowers = []

    def __init__(self, pos=None):
        """создать пчелу в указанной точке экрана"""
        img_file_name = 'bee.png' if self.team == 1 else 'bee-2.png'
        self.my_beehive = Scene.get_beehive(self.team)
        if pos is None:
            if self.my_beehive is None:
                pos = Point()
            else:
                pos = self.my_beehive.coordinates.copy()
        self._sprite = BaseSprite(
            obj_to_sprite=ObjectToSprite(self),
            img_file_name=img_file_name,
            layer=2
        )
        HoneyHolder.__init__(self, honey_loaded=0, honey_max=BEE_HONEY_MAX)
        GameObject.__init__(self, pos=pos)
        Bee._container.append(self)

    def __str__(self):
        return 'bee({},{}) {}'.format(self.x, self.y, self._vector)

    def __repr__(self):
        return str(self)

    def _update(self):
        """Внутренняя функция для обновления переменных отображения"""
        HoneyHolder._update(self, is_moving=self.is_moving)
        GameObject._update(self)

    def on_stop_at_target(self, target):
        """Обработчик события 'остановка у цели' """
        if isinstance(target, Flower):
            self.on_stop_at_flower(target)
        elif isinstance(target, BeeHive):
            self.on_stop_at_beehive(target)
        else:
            pass

    def on_stop_at_flower(self, flower):
        """Обработчик события 'остановка у цветка' """
        pass

    def on_stop_at_beehive(self, beehive):
        """Обработчик события 'остановка у улья' """
        pass


class BeeHive(HoneyHolder, GameObject):
    """Улей. Стоит там где поставили и содержит мёд."""
    _container = []

    def __init__(self, pos=None, max_honey=4000):
        """создать улей в указанной точке экрана"""
        self._sprite = BaseSprite(
            obj_to_sprite=ObjectToSprite(self),
            img_file_name='beehive.png'
        )
        GameObject.__init__(self, pos)
        HoneyHolder.__init__(self, 0, max_honey)
        self.honey_meter = HoneyMeter(pos=Point(pos.int_x - 24, pos.int_y - 37))
        BeeHive._container.append(self)

    def move_at(self, target_pos):
        """Заглушка - улей не может двигаться"""
        pass

    def _update(self):
        """Внутренняя функция для обновления переменных отображения"""
        self.honey_meter.set_value(self.honey)
        HoneyHolder._update(self, is_moving=False)
        GameObject._update(self)


class Flower(HoneyHolder, GameObject):
    """Цветок. Источник мёда."""
    _container = []

    def __init__(self, pos=None):
        """Создать цветок в указанном месте.
        Если не указано - то в произвольном месте в квадрате ((200,200),(край экрана - 50,край экрана - 50))"""
        if not pos:
            pos = (
                random.randint(200, UserInterface.screen_width - 50),
                random.randint(200, UserInterface.screen_height - 50)
            )
        honey = random.randint(FLOWER_HONEY_MIN, FLOWER_HONEY_MAX)
        self._sprite = BaseSprite(
            obj_to_sprite=ObjectToSprite(self),
            img_file_name='romashka.png'
        )
        GameObject.__init__(self, pos)
        HoneyHolder.__init__(self, honey, honey)
        Flower._container.append(self)

    def move_at(self, target_pos):
        """Заглушка - цветок не может двигаться"""
        pass

