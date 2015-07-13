# -*- coding: utf-8 -*-
"""Тестовая игра"""
import random

from robogame_engine.geometry import Point

from beegarden.core import Bee, Beegarden


class WorkerBee(Bee):
    all_bees = []

    def is_other_bee_target(self, flower):
        for bee in WorkerBee.all_bees:
            if hasattr(bee, 'flower') and bee.flower and bee.flower.id == flower.id:
                return True
        return False

    def get_nearest_flower(self):
        flowers_with_honey = [flower for flower in self.flowers if flower.honey > 0]
        if not flowers_with_honey:
            return None
        nearest_flower = None
        for flower in flowers_with_honey:
            if self.is_other_bee_target(flower):
                continue
            if nearest_flower is None or self.distance_to(flower) < self.distance_to(nearest_flower):
                nearest_flower = flower
        return nearest_flower

    def go_next_flower(self):
        if self.is_full():
            self.move_at(self.my_beehive)
        else:
            self.flower = self.get_nearest_flower()
            if self.flower is not None:
                self.move_at(self.flower)
            elif self.honey > 0:
                self.move_at(self.my_beehive)
            else:
                i = random.randint(0, len(self.flowers) - 1)
                self.move_at(self.flowers[i])

    def on_born(self):
        WorkerBee.all_bees.append(self)
        self.go_next_flower()

    def on_stop_at_flower(self, flower):
        for bee in self.bees:
            if not isinstance(bee, self.__class__) and self.near(bee):
                self.sting(bee)
        else:
            if flower.honey > 0:
                self.load_honey_from(flower)
            else:
                self.go_next_flower()

    def on_honey_loaded(self):
        self.go_next_flower()

    def on_stop_at_beehive(self, beehive):
        self.unload_honey_to(beehive)

    def on_honey_unloaded(self):
        self.go_next_flower()

    def sting(self, bee):
        pass


class GreedyBee(WorkerBee):

    def get_nearest_flower(self):
        flowers_with_honey = [flower for flower in self.flowers if flower.honey > 0]
        if not flowers_with_honey:
            return None
        nearest_flower = None
        max_honey = 0
        for flower in flowers_with_honey:
            if self.is_other_bee_target(flower):
                continue
            if flower.honey > max_honey:
                nearest_flower = flower
                max_honey = flower.honey
        if nearest_flower:
            return nearest_flower
        return random.choice(flowers_with_honey)


class NextBee(GreedyBee):
    pass


class Next2Bee(GreedyBee):
    pass


if __name__ == '__main__':
    beegarden = Beegarden(
        name="My little garden",
        beehives_count=4,
        flowers_count=50,
        speed=3,
        # field=(800, 600),
        theme_mod_path='beegarden.themes.default',
    )

    count = 10
    bees = [WorkerBee(pos=Point(400,400)) for i in range(count)]
    bees_2 = [GreedyBee() for i in range(count)]
    bees_3 = [NextBee() for i in range(count)]
    bees_4 = [Next2Bee() for i in range(count)]

    bee = WorkerBee()
    bee.move_at(Point(1000, 1000))  # проверка на выход за границы экрана

    beegarden.go()
