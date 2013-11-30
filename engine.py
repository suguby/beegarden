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


class Rect:

    def __init__(self, x=0, y=0, w=10, h=10):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def reduce(self, dw=0, dh=0):
        self.w -= dw
        self.h -= dh

    def shift(self, dx=0, dy=0):
        self.x -= dx
        self.y -= dy

class Scene:
    """Сцена игры. Содержит статичные элементы"""
    beehives = []
    screen_width = 1
    screen_height = 1

    def __init__(self, name, flowers_count=5, beehives_count=1, speed=5, resolution=None):
        from core import Bee, BeeHive, Flower
        from user_interface import UserInterface
        self._flower_jitter = 0.34

        self.bees = Bee._container
        self.beehives = BeeHive._container
        self.flowers = Flower._container
        Bee.flowers = self.flowers
        self.ui = UserInterface(name, resolution=resolution)
        Scene.screen_width, Scene.screen_height = UserInterface.screen_width, UserInterface.screen_height

        self.hold_state = False  # режим пошаговой отладки
        self._step = 0

        self._place_flowers_and_beehives(flowers_count, beehives_count)
        self._set_game_speed(speed)

    def _place_flowers_and_beehives(self, flowers_count, beehives_count):
        from core import Flower, BeeHive

        flower = Rect(w=104, h=100)
        beehive = Rect(w=150, h=117)
        field = Rect(w=Scene.screen_width, h=Scene.screen_height)
        field.reduce(dw=flower.w * 0.5 + beehive.w, dh=flower.h * 0.5 - beehive.h)
        if beehives_count >= 2:
            field.reduce(dw=beehive.w)
        if beehives_count >= 3:
            field.reduce(dh=beehive.h)
        if field.w < flower.w or field.h < flower.h:
            raise Exception("Too little field...")

        cell = Rect()
        cell.h = sqrt(field.w * field.h * flower.h / float(flowers_count * flower.w))
        cell.w = int(cell.h * flower.w / flower.h)
        cell.h = int(cell.h)

        cells_in_width, cells_in_height, cells_count = 5, 5, 25
        while True:
            cells_in_width = int(float(field.w) / cell.w)
            cells_in_height = int(float(field.h) / cell.h)
            cells_count = cells_in_width * cells_in_height
            if cells_count >= flowers_count:
                break
            dw = (float(field.w) - cells_in_width * cell.w) / cells_in_width
            dh = (float(field.h) - cells_in_height * cell.h) / cells_in_height
            if dw > dh:
                cell.w -= 1
            else:
                cell.h -= 1

        cell_numbers = [i for i in range(cells_count)]
        print cells_in_width, cells_in_height

        min_random = int(self._flower_jitter * cell_size / 2.0)
        max_random = cell_size - min_random

        field_width = cells_in_width * cell_size + (cell_size - self.flower_width * self._flower_jitter) / 2.0
        field_height = cells_in_height * cell_size + (cell_size - self.flower_height * self._flower_jitter) / 2.0
        print cell_size, field_width, field_height

        field_x = self.beehive_width + int((Scene.screen_width - self.beehive_width - field_width) / 2)
        field_y = self.beehive_height + int((Scene.screen_height - self.beehive_height - field_height) / 2)


        max_honey = 0
        while len(self.flowers) < flowers_count:
            cell_number = random.choice(cell_numbers)
            cell_numbers.remove(cell_number)
            cell_x = (cell_number % cells_in_width) * cell_size
            cell_y = (cell_number // cells_in_width) * cell_size
            dx = random.randint(min_random, max_random)
            dy = random.randint(min_random, max_random)
            pos = Point(field_x + cell_x + dx, field_y + cell_y + dy)
            flower = Flower(pos)  # автоматически добавит к списку цаетов
            max_honey += flower.honey
        max_honey /= float(beehives_count)
        max_honey = int(round((max_honey / 1000.0) * 1.3)) * 1000
        if max_honey < 1000:
            max_honey = 1000
        for i in range(beehives_count):
            if i == 0:
                pos = Point(90, 75)
            elif i == 1:
                pos = Point(Scene.screen_width - 90, 75)
            elif i == 2:
                pos = Point(90, Scene.screen_height - 75)
            else:
                pos = Point(Scene.screen_width - 90, Scene.screen_height - 75)
            Scene.beehives.append(BeeHive(pos=pos, max_honey=max_honey))

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