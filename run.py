# -*- coding: utf-8 -*-

from engine import Scene
from my_bee import MyBee  # импортируем код класса пчелы
from user_interface import GameEngine

game = GameEngine("My little garden")  # создаем движок нашей игры
scene = Scene(flowers_count=3)  # создаем нужную сцену

bee = MyBee()  # вот оно - рождение пчелы!

game.go()  # и запускаем наш виртуальный мир крутиться...


# для запуска соревнования
#
#game = GameEngine("My little garden", resolution=(1000, 500))
#scene = Scene(beehives_count=2, flowers_count=80, speed=40)
#
#from my_bee import MyBee
#from other_bee import OtherBee
# или
#from beegarden import WorkerBee, GreedyBee
#
#bees = [MyBee() for i in range(10)] # В классе MyBee должна быть указана команда team = 1
#bees_2 = [OtherBee() for i in range(10)] # В классе OtherBee должна быть указана команда team = 2
#
#game.go()
