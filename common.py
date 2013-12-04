# -*- coding: utf-8 -*-
"""Общие обьекты для всех модулей"""
import random


class ObjectToSprite(object):
    """
        Инкапсуляция получения данных об объекте спрайтом
    """

    def __init__(self, game_object):
        self.game_object = game_object

    def _get_coordinates(self):
        """
            Получить координаты
        """
        return self.game_object._coord

    def _get_direction(self):
        """
            Получить направление
        """
        return self.game_object._vector.angle

    def _get_load_value(self):
        """
            Получить величену загрузки в долях единицы
        """
        return self.game_object._honey / float(self.game_object._honey_max)

    def _is_dead(self):
        """
            Мертв?
        """
        return self.game_object.state == 'dead'


def random_number(a=0, b=300):
    """
        Выдать случайное целое из диапазона [a,b]
    """
    return random.randint(a, b)