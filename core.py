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
            raise Exception("honey_max cant be zero!")
        self._honey_max = honey_max

        self._source = None
        self._target = None
        self._state = 'stop'

    def on_honey_loaded(self):
        """Обработчик события 'мёд загружен' """
        pass

    def on_honey_unloaded(self):
        """Обработчик события 'мёд разгружен' """
        pass

    def load_honey_from(self, source):
        """Загрузить мёд от ... """
        self._state = 'loading'
        self._source = source

    def unload_honey_to(self, target):
        """Разгрузить мёд в ... """
        self._target = target
        self._state = 'unloading'

    def is_full(self):
        """полностью заполнен?"""
        return self.honey >= self._honey_max

    def _update(self):
        """Внутренняя функция для обновления переменных отображения"""
        if self._state == 'moving':
            self._source = None
            self._target = None
            return
        if self._source:
            honey = self._source._get_honey()
            if honey:
                self._put_honey(honey)
                if self.honey >= self._honey_max:
                    self.on_honey_loaded()
                    self._source = None
                    self._state = 'stop'
                else:
                    self._state = 'loading'
            else:
                self.on_honey_loaded()
                self._source = None
                self._state = 'stop'
        if self._target:
            honey = self._get_honey()
            self._target._put_honey(honey)
            if self.honey == 0:
                self.on_honey_unloaded()
                self._target = None
                self._state = 'stop'
            else:
                self._state = 'unloading'

    def _get_honey(self):
        """Взять мёд у объекта"""
        if self._honey > self._honey_speed:
            self._honey -= self._honey_speed
            return self._honey_speed
        elif self._honey > 0:
            value = self._honey
            self._honey = 0
            return value
        return 0.0

    def _put_honey(self, value):
        """Отдать мёд объекту"""
        self._honey += value
        if self._honey > self._honey_max:
            self._honey = self._honey_max


class Bee(GameObject, BaseSprite, HoneyHolder):
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
                pos = self.my_beehive.coordinates
        BaseSprite.__init__(self)
        HoneyHolder.__init__(self, honey_loaded=0, honey_max=100)
        GameObject.__init__(self, pos=pos)
        Bee._container.append(self)

    def __str__(self):
        return 'bee(%s,%s) %s %s' % (self.x, self.y, self._state, BaseSprite.__str__(self))

    def __repr__(self):
        return str(self)

    def _get_load_value(self):
        return self.honey / float(self._honey_max)

    def _update(self):
        """Внутренняя функция для обновления переменных отображения"""
        HoneyHolder._update(self)  # TODO множественное переопределение :(
        GameObject._update(self)

    def on_stop_at_target(self, target):
        """Обработчик события 'остановка у цели' """
        self._state = 'stop'
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


class BeeHive(GameObject, BaseSprite, HoneyHolder):
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


class Flower(GameObject, BaseSprite, HoneyHolder):
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


