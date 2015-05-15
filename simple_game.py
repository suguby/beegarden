# -*- coding: utf-8 -*-
"""запуск простейшей игры"""

from engine import Scene
from my_bee import MyBee  # импортируем код класса пчелы

scene = Scene(  # создаем нужную сцену
    name="My little garden",
    flowers_count=10,
    resolution=(1000, 500),
)

bee = MyBee()  # вот оно - рождение пчелы!

scene.go()  # и запускаем наш виртуальный мир крутиться...

# для запуска соревнования
#
# scene = Scene(
#     name="My little garden",
#     beehives_count=2,
#     flowers_count=80,
#     speed=40,
#     resolution=(1000, 500)
# )
# #
# from my_bee import MyBee
# from my_bee import MyBee as OtherBee
#
# bees = [MyBee() for i in range(10)] # В классе MyBee должна быть указана команда team = 1
# bees_2 = [OtherBee() for i in range(10)] # В классе OtherBee должна быть указана команда team = 2
# #
# scene.go()
