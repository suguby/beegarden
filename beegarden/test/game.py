# -*- coding: utf-8 -*-
"""Тестовая игра"""
import random

from robogame_engine.geometry import Point

from beegarden.core import Bee, Beegarden


class WorkerBee(Bee):
    my_team_bees = []

    def is_other_bee_target(self, flower):
        for bee in WorkerBee.my_team_bees:
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
        WorkerBee.my_team_bees.append(self)
        self.go_next_flower()

    def on_stop_at_flower(self, flower):
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


class HunterBee(GreedyBee):
    _hunters = []
    _victim = None

    def on_born(self):
        if len(HunterBee._hunters) < 3:
            HunterBee._hunters.append(self)
        super(HunterBee, self).on_born()

    @classmethod
    def to_hunt(cls):
        if cls._victim:
            can_sting = 0
            for hunter in cls._hunters:
                if hunter.distance_to(cls._victim) < 20:
                    can_sting += 1
            if can_sting == len(cls._hunters):
                for hunter in cls._hunters:
                    hunter.sting(cls._victim)
                cls._victim = None
            else:
                for hunter in cls._hunters:
                    hunter.move_at(cls._victim)
        else:
            commander = cls._hunters[0]
            bees = [bee for bee in commander.bees if not isinstance(bee, cls) and not bee.dead]
            for bee in bees:
                if cls._victim is None or (commander.distance_to(bee) < commander.distance_to(cls._victim)):
                    cls._victim = bee

    def on_stop_at_flower(self, flower):
        HunterBee.to_hunt()
        super(HunterBee, self).on_stop_at_flower(flower)

    def on_stop_at_beehive(self, beehive):
        HunterBee.to_hunt()
        super(HunterBee, self).on_stop_at_beehive(beehive)

    def on_honey_loaded(self):
        HunterBee.to_hunt()
        super(HunterBee, self).on_honey_loaded()

    def on_honey_unloaded(self):
        HunterBee.to_hunt()
        super(HunterBee, self).on_honey_unloaded()


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
    bees_3 = [HunterBee() for i in range(count)]
    bees_4 = [Next2Bee() for i in range(count)]

    bee = WorkerBee()
    bee.move_at(Point(1000, 1000))  # проверка на выход за границы экрана

    beegarden.go()
