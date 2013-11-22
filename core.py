#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from engine import GameObject, Scene

from geometry import Point
from user_interface import BaseSprite, HoneyMeter
import user_interface


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

    def _update(self):
        """Внутренняя функция для обновления переменных отображения"""
        if self.is_moving:  # TODO плохо - берется метод из соседнего класса, позднее связывание
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

    def _get_load_value(self):
        return self._honey / float(self._honey_max)

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


class Bee(HoneyHolder, GameObject, BaseSprite):
    """Пчела. Может летать по экрану и носить мёд."""
    _img_file_name = 'bee.png'
    _layer = 2
    _container = []
    team = 1
    my_beehive = None
    flowers = []

    def __init__(self, pos=None):
        """создать пчелу в указанной точке экрана"""
        if self.team > 1:
            self._img_file_name = 'bee-2.png'
        self.my_beehive = Scene.get_beehive(self.team)
        if pos is None:
            if self.my_beehive is None:
                pos = Point()
            else:
                pos = self.my_beehive.coordinates.copy()
        BaseSprite.__init__(self)
        HoneyHolder.__init__(self, honey_loaded=0, honey_max=100)
        GameObject.__init__(self, pos=pos)
        Bee._container.append(self)

    def __str__(self):
        return 'bee({},{}) {}'.format(self.x, self.y, BaseSprite.__str__(self))

    def __repr__(self):
        return str(self)

    def _update(self):
        """Внутренняя функция для обновления переменных отображения"""
        HoneyHolder._update(self)
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


class BeeHive(HoneyHolder, GameObject, BaseSprite):
    """Улей. Стоит там где поставили и содержит мёд."""
    _img_file_name = 'beehive.png'

    def __init__(self, pos=None, max_honey=4000):
        """создать улей в указанной точке экрана"""
        BaseSprite.__init__(self)
        GameObject.__init__(self, pos)
        HoneyHolder.__init__(self, 0, max_honey)
        self.honey_meter = HoneyMeter(pos=(pos[0] - 24, pos[1] - 37))

    def move_at(self, target_pos):
        """Заглушка - улей не может двигаться"""
        pass

    def _update(self):
        """Внутренняя функция для обновления переменных отображения"""
        self.honey_meter.set_value(self.honey)
        HoneyHolder._update(self)
        GameObject._update(self)


class Flower(HoneyHolder, GameObject, BaseSprite):
    """Цветок. Источник мёда."""
    _img_file_name = 'romashka.png'

    def __init__(self, pos=None):
        """Создать цветок в указанном месте.
        Если не указано - то в произвольном месте в квадрате ((200,200),(край экрана - 50,край экрана - 50))"""
        if not pos:
            pos = (
                random.randint(200, user_interface.SCREENRECT.width - 50),
                random.randint(200, user_interface.SCREENRECT.height - 50)
            )
        honey = random.randint(100, 200)
        BaseSprite.__init__(self)
        GameObject.__init__(self, pos)
        HoneyHolder.__init__(self, honey, honey)

    def move_at(self, target_pos):
        """Заглушка - цветок не может двигаться"""
        pass


