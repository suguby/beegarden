#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import *
import random
from constants import NEAR_RADIUS

from geometry import Point
from user_interface import BaseSprite, HoneyMeter
import user_interface


class HoneyHolder():
    """Класс объекта, который может нести мёд"""
    honey_speed = 1

    def __init__(self, honey_loaded, honey_max):
        """Задать начальние значения: honey_loaded - сколько изначально мёда, honey_max - максимум"""
        self._honey = honey_loaded
        if honey_max == 0:
            raise Exception("honey_max cant be zero!")
        self._honey_max = honey_max

        self._source = None
        self._target = None
        self._state = 'stop'

        self._set_load_hh()

    honey = property(lambda self: self._honey, doc="""Количество мёда у объекта""")

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
        if self._honey > self.honey_speed:
            self._honey -= self.honey_speed
            self._set_load_hh()
            return self.honey_speed
        elif self._honey > 0:
            value = self._honey
            self._honey = 0
            self._set_load_hh()
            return value
        return 0.0

    def _put_honey(self, value):
        """Отдать мёд объекту"""
        self._honey += value
        if self._honey > self._honey_max:
            self._honey = self._honey_max
        self._set_load_hh()

    def _set_load_hh(self):
        """Внутренняя функция отрисовки бара"""
        load_value = int((float(self._honey) / self._honey_max) * 100.0)
        BaseSprite._set_load(self, load_value)


class Bee(BaseSprite, HoneyHolder):
    """Пчела. Может летать по экрану и носить мёд."""
    _img_file_name = 'bee.png'
    _layer = 2
    team = 1
    my_beehive = None
    flowers = []

    def __init__(self, pos=None):
        """создать пчелу в указанной точке экрана"""
        if self.team > 1:
            self._img_file_name = 'bee-2.png'
        self.my_beehive = Scene.get_beehive(self.team)
        pos = self.my_beehive.coord
        BaseSprite.__init__(self, pos)
        self.speed = float(self.speed) - random.random()
        HoneyHolder.__init__(self, 0, 100)
        self.on_born()

    def __str__(self):
        return 'bee(%s,%s) %s %s' % (self.x, self.y, self._state, BaseSprite.__str__(self))

    def __repr__(self):
        return str(self)

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        HoneyHolder._update(self)
        BaseSprite.update(self)

    def move_at(self, target):
        """ Задать движение к указанной точке <объект/точка/координаты>, <скорость> """
        self.target = target
        self._state = 'moving'
        BaseSprite.move_at(self, target)

    def on_stop_at_target(self):
        """Обработчик события 'остановка у цели' """
        self._state = 'stop'
        if isinstance(self.target, Flower):
            self.on_stop_at_flower(self.target)
        elif isinstance(self.target, BeeHive):
            self.on_stop_at_beehive(self.target)
        else:
            pass

    def on_born(self):
        """Обработчик события 'рождение' """
        pass

    def on_stop_at_flower(self, flower):
        """Обработчик события 'остановка у цветка' """
        pass

    def on_stop_at_beehive(self, beehive):
        """Обработчик события 'остановка у улья' """
        pass


class BeeHive(BaseSprite, HoneyHolder):
    """Улей. Стоит там где поставили и содержит мёд."""
    _img_file_name = 'beehive.png'

    def __init__(self, pos=None, max_honey=4000):
        """создать улей в указанной точке экрана"""
        BaseSprite.__init__(self, pos)
        HoneyHolder.__init__(self, 0, max_honey)
        self.honey_meter = HoneyMeter(pos=(pos[0] - 24, pos[1] - 37))

    def move(self, direction):
        """Заглушка - улей не может двигаться"""
        pass

    def move_at(self, target_pos):
        """Заглушка - улей не может двигаться"""
        pass

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        self.honey_meter.set_value(self.honey)
        HoneyHolder._update(self)
        BaseSprite.update(self)


class Flower(BaseSprite, HoneyHolder):
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
        BaseSprite.__init__(self, pos)
        honey = random.randint(100, 200)
        HoneyHolder.__init__(self, honey, honey)

    def move(self, direction):
        """Заглушка - цветок не может двигаться"""
        pass

    def move_at(self, target_pos):
        """Заглушка - цветок не может двигаться"""
        pass

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        HoneyHolder._update(self)
        BaseSprite.update(self)


class Scene:
    """Сцена игры. Содержит статичные элементы"""
    _flower_size = 100
    _behive_size = 50
    _flower_jitter = 0.72
    beehives = []

    def __init__(self, flowers_count=5, beehives_count=1, speed=5):
        self._place_flowers(flowers_count)
        self._place_beehives(beehives_count)
        self._set_game_speed(speed)

    def _place_flowers(self, flowers_count):
        field_width = user_interface.SCREENRECT.width - self._flower_size * 2
        field_height = user_interface.SCREENRECT.height - self._flower_size * 2 - self._behive_size
        if field_width < 100 or field_height < 100:
            raise Exception("Too little field...")
#        print "field", field_width, field_height

        cell_size = int(round(sqrt(float(field_width * field_height) / flowers_count)))
        while True:
            cells_in_width = int(round(field_width / cell_size))
            cells_in_height = int(round(field_height / cell_size))
            cells_count = cells_in_width * cells_in_height
            if cells_count >= flowers_count:
                break
            cell_size -= 1
        cell_numbers = [i for i in range(cells_count)]
#        print "cells: size", cell_size, "count", cells_count, "in w/h", cells_in_width, cells_in_height

        field_width = cells_in_width * cell_size
        field_height = cells_in_height * cell_size
        x0 = int((user_interface.SCREENRECT.width - field_width) / 2)
        y0 = int((user_interface.SCREENRECT.height - field_height) / 2) + self._behive_size
#        print "field", field_width, field_height, x0, y0

        min_random = int((1.0 - self._flower_jitter) * (cell_size / 2.0))
        max_random = cell_size - min_random

        self.flowers = []
        while len(self.flowers) < flowers_count:
            cell_number = random.choice(cell_numbers)
            cell_numbers.remove(cell_number)
            cell_x = (cell_number % cells_in_width) * cell_size
            cell_y = (cell_number // cells_in_width) * cell_size
            dx = random.randint(min_random, max_random)
            dy = random.randint(min_random, max_random)
            pos = Point(x0 + cell_x + dx, y0 + cell_y + dy)
            self.flowers.append(Flower(pos))
        Bee.flowers = self.flowers

    def _place_beehives(self, beehives_count):
        max_honey = 0
        for flower in self.flowers:
            max_honey += flower.honey
        if beehives_count in (1, 2):
            if beehives_count == 2:
                max_honey /= 2.0
            max_honey = int(round((max_honey / 1000.0) * 1.3)) * 1000
            if max_honey < 1000:
                max_honey = 1000
            Scene.beehives.append(BeeHive(pos=(90, 75), max_honey=max_honey))
            if beehives_count == 2:
                self.beehives.append(BeeHive(pos=(user_interface.SCREENRECT.width - 90, 75), max_honey=max_honey))
        else:
            raise Exception("Only 2 beehives!")

    @classmethod
    def get_beehive(cls, team):
        # TODO сделать автоматическое распределение ульев - внизу, по кол-ву команд
        try:
            return cls.beehives[team - 1]
        except IndexError:
            return cls.beehives[0]

    def _set_game_speed(self, speed):
        if speed > NEAR_RADIUS:
            speed = NEAR_RADIUS
        BaseSprite.speed = speed
        honey_speed = int(speed / 2.0)
        if honey_speed < 1:
            honey_speed = 1
        HoneyHolder.honey_speed = honey_speed


