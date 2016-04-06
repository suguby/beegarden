# -*- coding: utf-8 -*-
"""пример алгоритма пчелы"""

from beegarden.core import Bee  # импортируем нужное из библиотек


class MyBee(Bee):

    def __init__(self):
        """ рождение пчелы """
        Bee.__init__(self)
        self.flower = self.flowers[-1]   # выбираем нашим первый попавшийся цветок
        self.move_at(self.flower)  # летим к нему

    def on_stop_at_flower(self, flower):
        """ пчела прилетела к цветку """
        if flower.honey > 0:  # если в цветке еще есть мёд
            self.load_honey_from(flower)  # забираем его
        else:  # цветок пуст
            self.go_next_flower()  # летим к другому цветку, если он есть

    def on_honey_loaded(self):
        """ мёд в пчелу загружен """
        if self.honey == 100:  # полностью ли я заполнен?
            self.move_at(self.my_beehive)   # да, летим к улью
        else:  # еще осталось место
            self.go_next_flower()  # летим к другому цветку, если он есть

    def on_stop_at_beehive(self, beehive):
        """ пчела прилетела к улью """
        self.unload_honey_to(beehive)  # просто разгружаем мёд в улей

    def on_honey_unloaded(self):
        """ мёд из пчелы разгружен """
        self.go_next_flower()  # летим к другому цветку, если он есть

    def go_next_flower(self):
        """ поиск следующего цветка """
        if not self.flower.honey:   # в моём цветке больше нет мёда
            if not self.flowers:  # и цветов не осталось
                if self.honey:  # а во мне есть мёд
                    self.move_at(self.my_beehive)  # летим к улью
                return   # цветов с мёдом больше нет, стоп
            else:  # остались цветы с мёдом
                self.flower = self.flowers[-1]   # берем следующий из списка
        self.move_at(self.flower)  # и летим к своему цветку