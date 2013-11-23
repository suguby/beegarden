# -*- coding: utf-8 -*-
"""Общие обьекты для всех модулей"""
import random


class ObjectToSprite(object):
    """
        Интерфейс получения данных об объекте спрайтом
    """

    def _get_coordinates(self):
        """
            Получить координаты
        """
        raise NotImplementedError

    def _get_load_value(self):
        """
            Получить величену загрузки в долях единицы
        """
        raise NotImplementedError

    def _get_direction(self):
        """
            Получить направление
        """
        raise NotImplementedError


def random_number(a=0, b=300):
    """
        Выдать случайное целое из диапазона [a,b]
    """
    return random.randint(a, b)