#!/usr/bin/env python
# -*- coding: utf-8 -*-
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