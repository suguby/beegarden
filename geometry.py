#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt, pow, pi, sin, cos, atan
from constants import NEAR_RADIUS, RANDOM_POINT_BORDER
from utils import random_number


class Point():
    """Класс точки на экране"""

    int_x = property(lambda self: round(self.x), doc="Округленная до пиксела координата X")
    int_y = property(lambda self: round(self.y), doc="Округленная до пиксела координата Y")

    def __init__(self, arg1=100, arg2=100):
        """Создать точку. Можно создать из другой точки, из списка/тьюпла или из конкретных координат"""
        try:  # arg1 is Point
            self.x = arg1.x
            self.y = arg1.y
        except AttributeError:
            try:  # arg1 is tuple or list
                self.x, self.y = arg1
            except:  # arg1 & arg2 is numeric
                self.x, self.y = arg1, arg2

    def to_screen(self, height):
        """Преобразовать координаты к экранным"""
        return self.int_x, height - self.int_y

    def add(self, vector):
        """Прибавить вектор - точка смещается на вектор"""
        self.x += vector.dx
        self.y += vector.dy

    def sub(self, vector):
        """Вычесть вектор - точка смещается на "минус" вектор"""
        self.add(-vector)

    def distance_to(self, point2):
        """Расстояние до другой точки"""
        return sqrt(pow(self.x - point2.x, 2) + pow(self.y - point2.y, 2))

    def near(self, point2, radius=NEAR_RADIUS):
        """Признак расположения рядом с другой точкой, рядом - это значит ближе, чем радиус"""
        return self.distance_to(point2) < radius

    def __eq__(self, point2):
        """Сравнение двух точек на равенство целочисленных координат"""
        #~ if point2:
        #~ print self, point2
        if self.int_x == point2.int_x and self.int_y == point2.int_y:
            return True
        return False

    def __str__(self):
        """Преобразование к строке"""
        return 'point(%s,%s)' % (self.x, self.y)

    def __repr__(self):
        """Представление """
        return str(self)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, ind):
        if ind:
            return self.y
        return self.x

    def __nonzero__(self):
        if self.x and self.y:
            return 1
        return 0


class Vector():
    """Класс математического вектора"""

    def __init__(self, point1=None, point2=None, direction=None, module=None, dx=None, dy=None):
        """
        Создать вектор. Можно создать из двух точек (длинной в модуль, если указан),
        а можно указать направление и модуль вектора.
        """
        self.dx = 0
        self.dy = 0

        if dx and dy:
            self.dx, self.dy = dx, dy
        elif point1 or point2:  # если заданы точки
            if not point1:
                point1 = Point(0, 0)
            if not point2:
                point2 = Point(0, 0)
            self.dx = float(point2.x - point1.x)
            self.dy = float(point2.y - point1.y)
        elif direction:  # ... или задано направление
            direction = (direction * pi) / 180
            self.dx = sin(direction)
            self.dy = cos(direction)

        self.module = self._determine_module()
        if module:  # если задана длина вектора, то ограничиваем себя :)
            if self.module:
                self.dx *= module / self.module
                self.dy *= module / self.module
            self.module = module

        self.angle = self._determine_angle()

    def add(self, vector2):
        """Сложение векторов"""
        self.dx += vector2.dx
        self.dy += vector2.dy
        self.module = self._determine_module()
        self.angle = self._determine_angle()

    def _determine_module(self):
        return sqrt(self.dx * self.dx + self.dy * self.dy)

    def _determine_angle(self):
        angle = 0
        if self.dx == 0:
            if self.dy >= 0:
                return 90
            else:
                return 270
        else:
            angle = atan(self.dy / self.dx) * (180 / pi)
            #print self.dx, self.dy, angle
            if self.dx < 0:
                angle += 180
        return angle

    def __str__(self):
        return 'vector([%.2f,%.2f],{%.2f,%.2f})' % (self.dx, self.dy, self.angle, self.module)

    def __repr__(self):
        return str(self)

    def __nonzero__(self):
        """Проверка на пустоту"""
        return int(self.module)

    def __neg__(self):
        return Vector(dx=-self.dx, dy=-self.dy)


def random_point():
    """
        Сгенерировать случнайную точку внутри области рисования
    """
    import user_interface

    x = _get_random_coordinate(user_interface.SCREENRECT.width)
    y = _get_random_coordinate(user_interface.SCREENRECT.height)
    return Point(x, y)


def _get_random_coordinate(high):
    return random_number(RANDOM_POINT_BORDER, high - RANDOM_POINT_BORDER)