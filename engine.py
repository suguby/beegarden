# -*- coding: utf-8 -*-
"""Сердце игры - тут все крутится и происходит"""
from math import sqrt
import random
from common import ObjectToSprite
from constants import NEAR_RADIUS
from geometry import Point, Vector


class GameObject(ObjectToSprite):
    _default_speed = 5.0
    _total_objects = 0

    coordinates = property(lambda self: self._coord)
    speed = property(lambda self: self._speed)
    course = property(lambda self: self._vector.angle)
    is_moving = property(lambda self: self._is_moving)

    def __init__(self, pos=None):
        if pos is None:
            self._coord = Point()
        else:
            self._coord = pos
        self._target_coord = Point(0, 0)
        self._vector = Vector()
        self._is_moving = False
        self._speed = float(GameObject._default_speed) - random.random()  # что бы не сливались при полете к одной цели
        self.on_born()
        GameObject._total_objects += 1
        self._id = GameObject._total_objects

    #def _get_coordinates(self):
    #    return self._coord
    #
    #def _get_direction(self):
    #    return self._vector.angle
    #
    def on_born(self):
        """Обработчик события 'рождение' """
        pass

    def on_stop_at_target(self, target):
        """Обработчик события 'остановка у цели' """
        pass

    def move_at(self, target):
        """ Задать движение к указанной точке <объект/точка/координаты>, <скорость> """
        if isinstance(target, Point):
            self._target_coord = target
        elif isinstance(target, GameObject):
            self._target_coord = target._coord
            self._target = target
        else:
            raise Exception("move_at: target {} must be GameObject or Point!".format(target))
        self._vector = Vector(point1=self._coord, point2=self._target_coord, module=self._speed)
        self._is_moving = True

    def stop(self):
        """ Остановить объект """
        self._is_moving = False

    def distance_to(self, obj):
        """ Расстояние до объекта <объект/точка>"""
        if isinstance(obj, GameObject):
            return self._coord.distance_to(obj._coord)
        if isinstance(obj, Point):
            return self._coord.distance_to(obj)
        raise Exception("sprite.distance_to: obj {} must be GameObject or Point!".format(obj))

    def near(self, obj, radius=NEAR_RADIUS):
        """ Проверка близости к объекту <объект/точка>"""
        return self.distance_to(obj) <= radius

    def _update(self):
        if self._is_moving:
            self._coord.add(self._vector)
            if self._coord.int_x < 0 or self._coord.int_x > Scene.screen_width or \
                            self._coord.int_y < 0 or self._coord.int_y > Scene.screen_height:
                self._coord.add(-self._vector)
                self.stop()
            elif self.near(self._target_coord):
                self.stop()
                self.on_stop_at_target(self._target)


class Scene:
    """Сцена игры. Содержит статичные элементы"""
    _flower_size = 100
    _behive_size = 50
    _flower_jitter = 0.72
    beehives = []
    screen_width = 1024
    screen_height = 768

    def __init__(self, name, flowers_count=5, beehives_count=1, speed=5, resolution=None):
        from core import Bee, BeeHive, Flower
        from user_interface import UserInterface

        self.bees = Bee._container
        self.beehives = BeeHive._container
        self.flowers = Flower._container
        Bee.flowers = self.flowers
        self.ui = UserInterface(name, resolution=resolution)
        Scene.screen_width, Scene.screen_height = UserInterface.screen_width, UserInterface.screen_height

        self.hold_state = False  # режим пошаговой отладки
        self._step = 0

        self._place_flowers(flowers_count)
        self._place_beehives(beehives_count)
        self._set_game_speed(speed)

    def _place_flowers(self, flowers_count):
        from core import Flower

        field_width = Scene.screen_width - self._flower_size * 2
        field_height = Scene.screen_height - self._flower_size * 2 - self._behive_size
        if field_width < 100 or field_height < 100:
            raise Exception("Too little field...")
            #        print "field", field_width, field_height

        cell_size = int(round(sqrt(float(field_width * field_height) / flowers_count)))
        cells_in_width, cells_in_height, cells_count = 5, 5, 25
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

        x0 = int((Scene.screen_width - field_width) / 2)
        y0 = int((Scene.screen_height - field_height) / 2) + self._behive_size
        #        print "field", field_width, field_height, x0, y0

        min_random = int((1.0 - self._flower_jitter) * (cell_size / 2.0))
        max_random = cell_size - min_random

        while len(self.flowers) < flowers_count:
            cell_number = random.choice(cell_numbers)
            cell_numbers.remove(cell_number)
            cell_x = (cell_number % cells_in_width) * cell_size
            cell_y = (cell_number // cells_in_width) * cell_size
            dx = random.randint(min_random, max_random)
            dy = random.randint(min_random, max_random)
            pos = Point(x0 + cell_x + dx, y0 + cell_y + dy)
            Flower(pos)  # автоматически добавит к списку цаетов

    def _place_beehives(self, beehives_count):
        from core import BeeHive

        max_honey = 0
        for flower in self.flowers:
            max_honey += flower.honey
        if beehives_count in (1, 2):
            if beehives_count == 2:
                max_honey /= 2.0
            max_honey = int(round((max_honey / 1000.0) * 1.3)) * 1000
            if max_honey < 1000:
                max_honey = 1000
            Scene.beehives.append(BeeHive(pos=Point(90, 75), max_honey=max_honey))
            if beehives_count == 2:
                Scene.beehives.append(BeeHive(pos=Point(Scene.screen_width - 90, 75), max_honey=max_honey))
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
        from core import HoneyHolder
        if speed > NEAR_RADIUS:
            speed = NEAR_RADIUS
        GameObject._default_speed = speed
        honey_speed = int(speed / 5.0)
        if honey_speed < 1:
            honey_speed = 1
        HoneyHolder._honey_speed = honey_speed

    def game_step(self):
        for obj in self.bees + self.beehives:
            obj._update()

    def go(self):
        """ Главный цикл игры """
        while True:
            # получение состояния клавы и мыши
            self.ui.get_keyboard_and_mouse_state()
            if self.ui.the_end:
                break
                # переключение режима отладки
            if self.ui.switch_debug:
                if self.ui.debug:  # были в режиме отладки
                    self.hold_state = False
                    self.ui.clear_screen()
                else:
                    self.hold_state = True
                self.ui.debug = not self.ui.debug
                # шаг игры, если надо
            if not self.hold_state or self.ui.one_step:
                self._step += 1
                self.game_step()
                #if self.ui.debug:
                #    common.log.debug('=' * 20, self._step, '=' * 10)
            # отрисовка
            self.ui.draw()

        print 'Thank for playing beegarden! See you in the future :)'