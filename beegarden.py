#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from math import *
import random

import time
import os

SCREENRECT = None
_revolvable = 0
_determine_collisions = 0
_max_layers = 5
_sprites_by_layer = [pygame.sprite.Group() for i in range(_max_layers + 1)]
_sprites_count = 0
_course_step = 5
NEAR_RADIUS = 20


def collide_circle(left, right):
    return left.distance_to(right) <= left.radius + right.radius


class MshpSprite(pygame.sprite.DirtySprite):
    """Класс отображения объектов на экране"""
    _img_file_name = 'empty.png'
    _layer = 0
    radius = 1
    speed = 3

    def __init__(self, pos=None, revolvable=None):
        """Создать объект в указанном месте"""

        if self._layer > _max_layers:
            self._layer = _max_layers
        if self._layer < 0:
            self._layer = 0
        self.containers = self.containers, _sprites_by_layer[self._layer]
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = load_image(self._img_file_name, -1)
        self.images = [self.image, pygame.transform.flip(self.image, 1, 0)]
        self.rect = self.image.get_rect()

        if pos is None:
            self.coord = Point(100, 100)
        else:
            self.coord = Point(pos)
        self.target_coord = Point(0, 0)
        self.rect.center = self.coord.to_screen()

        self.vector = Vector()
        self.is_moving = False
        self.course = self.vector.angle
        self.is_turning = False
        self.shot = False

        self.load_value = 0
        self.load_value_px = 0

        if revolvable is None:
            self.revolvable = _revolvable
        else:
            self.revolvable = revolvable

        global _sprites_count
        _sprites_count += 1
        self._id = _sprites_count

    def __str__(self):
        return 'sprite %s: %s %s %s %s' % (self._id, self.coord, self.vector, self.is_moving, self.is_turning)

    def __repr__(self):
        return str(self)

    x = property(lambda self: self.coord.int_x, doc="текущая позиция X объекта")
    y = property(lambda self: self.coord.int_y, doc="текущая позиция Y объекта")
    w = property(lambda self: self.rect.width, doc="ширина спрайта")
    h = property(lambda self: self.rect.height, doc="высота спрайта")

    def _set_load(self, value):
        """Внутренняя, установить бар загрузки"""
        if value > 100:
            value = 100
        if value < 0:
            value = 0
        self.load_value = value
        self.load_value_px = int((value / 100.0) * self.w)

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        if self.revolvable:
            if self.is_turning:
                delta = self.vector.angle - self.course
                if abs(delta) < _course_step:
                    self.course = self.vector.angle
                    self.is_turning = False
                else:
                    if delta < 0:
                        self.course -= _course_step
                    else:
                        self.course += _course_step
                old_center = self.rect.center
                self.image = pygame.transform.rotate(self.images[0], self.course)
                self.rect = self.image.get_rect()
                self.rect.center = old_center

        else:
            self.is_turning = False
            if self.vector.dx >= 0:
                self.image = self.images[1].copy()
            else:
                self.image = self.images[0].copy()
        #print self.course, self.vector.angle
        if self.is_moving and not self.is_turning:
            self.coord.add(self.vector)
            self.rect.center = self.coord.to_screen()
            if self.coord.near(self.target_coord):
                self.stop()
                self.on_stop_at_target()
            if _determine_collisions:
                collisions = pygame.sprite.spritecollide(self, _sprites_by_layer[self._layer], 0, collide_circle)
                if len(collisions) > 1:
                    #print collisions
                    for sprite in collisions:
                        if sprite._id == self._id:  # исключаем себя
                            continue
                        #~ print self._id, self.coord, sprite.coord, self.distance_to(sprite)
                        step_back_distance = (self.radius + sprite.radius) - self.distance_to(sprite)
                            # (self.radius + sprite.radius) - () +1
                        step_back_vector = Vector(sprite, self, module=step_back_distance)
                        #~ print self.vector, step_back_vector

                        #~ step_back_vector = Vector(dx = -self.vector.dx, dy = -self.vector.dy )
                        self.coord.add(step_back_vector)
                        self.stop()

        if self.load_value_px:
            pygame.draw.line(self.image, (0, 255, 7), (0, 0), (self.load_value_px, 0), 3)

        if not SCREENRECT.contains(self.rect):
            if self.rect.top < SCREENRECT.top:
                self.rect.top = SCREENRECT.top
            if self.rect.bottom > SCREENRECT.bottom:
                self.rect.bottom = SCREENRECT.bottom
            if self.rect.left < SCREENRECT.left:
                self.rect.left = SCREENRECT.left
            if self.rect.right > SCREENRECT.right:
                self.rect.right = SCREENRECT.right
            self.is_moving = False

    def turn_to(self, direction):
        self.vector = Vector(direction=direction, module=0)
        self.is_turning = True
        self.is_moving = False

    def move(self, direction):
        """ Задать движение в направлении <угол в градусах>, <скорость> """
        self.vector = Vector(direction=direction, module=self.speed)
        self.is_moving = True
        self.is_turning = True

    def move_at(self, target):
        """ Задать движение к указанной точке <объект/точка/координаты>, <скорость> """
        if type(target) in (type(()), type([])):
            target = Point(target)
        elif isinstance(target, Point):
            pass
        elif isinstance(target, MshpSprite):
            target = target.coord
        else:
            raise Exception("move_at: target %s must be coord or point or sprite!" % target)
        self.target_coord = target
        self.vector = Vector(point1=self.coord, point2=self.target_coord, module=self.speed)
        self.is_moving = True
        self.is_turning = True

    def stop(self):
        """ Остановить объект """
        self.is_moving = False
        self.is_turning = False

    def on_stop_at_target(self):
        """Обработчик события 'остановка у цели' """
        pass

    def distance_to(self, obj):
        """ Расстояние до объекта <объект/точка>"""
        if isinstance(obj, MshpSprite):
            return self.coord.distance_to(obj.coord)
        if isinstance(obj, Point):
            return self.coord.distance_to(obj)
        raise Exception("sprite.distance_to: obj %s must be Sprite or Point!" % obj)

    def near(self, obj, radius=NEAR_RADIUS):
        """ Проверка близости к объекту <объект/точка>"""
        return self.distance_to(obj) <= radius

    def near_edge(self):
        """ Проверка близости к краю экрана """
        if self.coord.x <= self.w // 2:
            return 'left'
        if self.coord.x >= SCREENRECT.width - self.w // 2:
            return 'right'
        if self.coord.y <= self.h // 2:
            return 'bottom'
        if self.coord.y >= SCREENRECT.height - self.h // 2:
            return 'top'
        return False


class HoneyHolder():
    """Класс объекта, который может нести мёд"""
    honey_speed = 1

    def __init__(self, honey_loaded, honey_max):
        """Задать начальние значения: honey_loaded - сколько изначально мёда, honey_max - максимум"""
        self._honey = honey_loaded
        self._honey_max = honey_max

        self._source = None
        self._target = None
        self._state = 'stop'

        self._set_load_hh()

    honey = property(lambda self: self._honey, doc="""Количество мёда у объекта""")

    def on_honey_loaded(self):
        """Обработчик события 'мёд загружен' """
        pass

    def on_honey_unloaded(self):
        """Обработчик события 'мёд разгружен' """
        pass

    def load_honey_from(self, source):
        """Загрузить мёд от ... """
        self._state = 'loading'
        self._source = source

    def unload_honey_to(self, target):
        """Разгрузить мёд в ... """
        self._target = target
        self._state = 'unloading'

    def is_full(self):
        """полностью заполнен?"""
        return self.honey >= self._honey_max

    def _update(self):
        """Внутренняя функция для обновления переменных отображения"""
        if self._state == 'moving':
            self._source = None
            self._target = None
            return
        if self._source:
            honey = self._source.get_honey()
            if honey:
                self.put_honey(honey)
                if self.honey >= self._honey_max:
                    self.on_honey_loaded()
                    self._source = None
                    self._state = 'stop'
            elif self.honey:
                self.on_honey_loaded()
                self._source = None
                self._state = 'stop'
            else:
                self._state = 'loading'
        if self._target:
            honey = self.get_honey()
            self._target.put_honey(honey)
            if self.honey == 0:
                self.on_honey_unloaded()
                self._target = None
                self._state = 'stop'
            else:
                self._state = 'unloading'

    def get_honey(self):
        """Взять мёд у объекта"""
        if self._honey > self.honey_speed:
            self._honey -= self.honey_speed
            self._set_load_hh()
            return self.honey_speed
        elif self._honey > 0:
            value = self._honey
            self._honey = 0
            self._set_load_hh()
            return value
        return 0.0

    def put_honey(self, value):
        """Отдать мёд объекту"""
        self._honey += value
        if self._honey > self._honey_max:
            self._honey = self._honey_max
        self._set_load_hh()

    def _set_load_hh(self):
        """Внутренняя функция отрисовки бара"""
        load_value = int((self._honey / self._honey_max) * 100.0)
        MshpSprite._set_load(self, load_value)


class Bee(MshpSprite, HoneyHolder):
    """Пчела. Может летать по экрану и носить мёд."""
    _img_file_name = 'bee.png'
    _layer = 2

    def __init__(self, pos=None):
        """создать пчелу в указанной точке экрана"""
        MshpSprite.__init__(self, pos)
        self.speed = float(self.speed) - random.random()
        HoneyHolder.__init__(self, 0, 100)
        self.on_born()

    def __str__(self):
        return 'bee(%s,%s) %s %s' % (self.x, self.y, self._state, MshpSprite.__str__(self))

    def __repr__(self):
        return str(self)

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        HoneyHolder._update(self)
        MshpSprite.update(self)

    def move_at(self, target):
        """ Задать движение к указанной точке <объект/точка/координаты>, <скорость> """
        self.target = target
        self._state = 'moving'
        MshpSprite.move_at(self, target)

    def on_stop_at_target(self):
        """Обработчик события 'остановка у цели' """
        self._state = 'stop'
        if isinstance(self.target, Flower):
            self.on_stop_at_flower(self.target)
        elif isinstance(self.target, BeeHive):
            self.on_stop_at_beehive(self.target)
        else:
            pass

    def on_born(self):
        """Обработчик события 'рождение' """
        pass

    def on_stop_at_flower(self, flower):
        """Обработчик события 'остановка у цветка' """
        pass

    def on_stop_at_beehive(self, beehive):
        """Обработчик события 'остановка у улья' """
        pass


class BeeHive(MshpSprite, HoneyHolder):
    """Улей. Стоит там где поставили и содержит мёд."""
    _img_file_name = 'beehive.png'

    def __init__(self, pos=None):
        """создать улей в указанной точке экрана"""
        MshpSprite.__init__(self, pos)
        HoneyHolder.__init__(self, 0, 4000)
        self.hm = HoneyMeter(pos=(pos[0] - 24, pos[1] - 37))

    def move(self, direction):
        """Заглушка - улей не может двигаться"""
        pass

    def move_at(self, target_pos):
        """Заглушка - улей не может двигаться"""
        pass

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        self.hm.set_value(self.honey)
        HoneyHolder._update(self)
        MshpSprite.update(self)


class Flower(MshpSprite, HoneyHolder):
    """Цветок. Источник мёда."""
    _img_file_name = 'romashka.png'

    def __init__(self, pos=None):
        """Создать цветок в указанном месте.
        Если не указано - то в произвольном месте в квадрате ((200,200),(край экрана - 50,край экрана - 50))"""
        if not pos:
            pos = (random.randint(200, SCREENRECT.width - 50), random.randint(200, SCREENRECT.height - 50))
        MshpSprite.__init__(self, pos)
        honey = random.randint(100, 200)
        HoneyHolder.__init__(self, honey, honey)

    def move(self, direction):
        """Заглушка - цветок не может двигаться"""
        pass

    def move_at(self, target_pos):
        """Заглушка - цветок не может двигаться"""
        pass

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        HoneyHolder._update(self)
        MshpSprite.update(self)


class Scene:
    """Сцена игры. Содержит статичные элементы"""

    def __init__(self, flowers_count=5, beehives_count=1, speed=5):

        if beehives_count > 2:
            beehives_count = 2
        self.beehives = []
        for i in range(beehives_count):
            if i:
                x = SCREENRECT.width - 90
            else:
                x = 90
            self.beehives.append(BeeHive(pos=(x, 75)))
        self.beehive = self.beehives[0]

        left_bottom = Point(100, 200)
        top_right = Point(SCREENRECT.width - 100, SCREENRECT.height - 60)
        self.flowers = []
        while len(self.flowers) < flowers_count:
            x = random.randint(left_bottom.x, top_right.x)
            y = random.randint(left_bottom.y, top_right.y)
            pos = Point(x, y)
            min_disance = 1000
            for flower in self.flowers:
                distance = flower.distance_to(pos)
                if min_disance > distance:
                    min_disance = distance
            if min_disance > 50:
                self.flowers.append(Flower(pos))

        if speed > NEAR_RADIUS / 2.0:
            speed = int(NEAR_RADIUS / 2.0)
        MshpSprite.speed = speed

        honey_speed = speed / 2.0
        if honey_speed < 1:
            honey_speed = 1
        HoneyHolder.honey_speed = honey_speed


def load_image(name, colorkey=None):
    """Загрузить изображение из файла"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print "Cannot load image:", name
        raise SystemExit(message)
        #image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image


class Point():
    """Класс точки на экране"""

    int_x = property(lambda self: round(self.x), doc="Округленная до пиксела координата X")
    int_y = property(lambda self: round(self.y), doc="Округленная до пиксела координата Y")

    def __init__(self, arg1=0, arg2=0):
        """Создать точку. Можно создать из другой точки, из списка/тьюпла или из конкретных координат"""
        try:  # arg1 is Point
            self.x = arg1.x
            self.y = arg1.y
        except AttributeError:
            try:  # arg1 is tuple or list
                self.x, self.y = arg1
            except:  # arg1 & arg2 is numeric
                self.x, self.y = arg1, arg2

    def to_screen(self):
        """Преобразовать координаты к экранным"""
        return self.int_x, SCREENRECT.height - self.int_y

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

    def near(self, point2, radius=5):
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
                return  270
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


class GameEngine:
    """Игровой движок. Выполняет все функции по отображению спрайтов и взаимодействия с пользователем"""

    def __init__(self, name, background_color=None, max_fps=60, resolution=None):
        """Создать игру. """
        global SCREENRECT

        pygame.init()
        if background_color is None:
            background_color = (87, 144, 40)
        if resolution is None:
            resolution = (1024, 768)
        SCREENRECT = Rect((0, 0), resolution)
        self.screen = pygame.display.set_mode(SCREENRECT.size)
        pygame.display.set_caption(name)

        self.background = pygame.Surface(self.screen.get_size())  # и ее размер
        self.background = self.background.convert()
        self.background.fill(background_color)  # заполняем цветом
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        self.all = pygame.sprite.LayeredUpdates()
        MshpSprite.containers = self.all
        Fps.containers = self.all
        HoneyMeter.containers = self.all

        global clock
        clock = pygame.time.Clock()
        self.fps_meter = Fps(color=(255, 255, 0))
        self.max_fps = max_fps

        self.debug = False

    def go(self):
        """Выполнение игрового цикла: рассчет позиций спрайтов и отрисовка их не экране"""

        one_step = False
        for event in pygame.event.get():
            if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return False
            if event.type == KEYDOWN and event.key == K_f:
                self.fps_meter.show = not self.fps_meter.show

            if event.type == KEYDOWN and event.key == K_d:
                self.debug = not self.debug
            if event.type == KEYDOWN and event.key == K_s:
                one_step = True

        if self.debug and not one_step:
            return True

        # clear/erase the last drawn sprites
        self.all.clear(self.screen, self.background)
        #self.flower.clear(self.screen, self.background)
        #self.others.clear(self.screen, self.background)

        #update all the sprites
        self.all.update()

        #draw the scene
        dirty = self.all.draw(self.screen)
        #pygame.draw.circle(self.screen, (0,0,0), flower_point.to_screen(), 20, 3) # отладка вывода положения цветка
        pygame.display.update(dirty)
        #dirty = self.flower.draw(self.screen)
        #pygame.display.update(dirty)
        #dirty = self.others.draw(self.screen)
        #pygame.display.update(dirty)

        #cap the framerate
        clock.tick(self.max_fps)
        return True


class Fps(pygame.sprite.DirtySprite):
    """Отображение FPS игры"""
    _layer = 5

    def __init__(self, color=(255, 255, 255)):
        """Создать индикатор FPS"""
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.show = False
        self.font = pygame.font.Font(None, 27)
        self.color = color
        self.image = self.font.render('-', 0, self.color)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(SCREENRECT.width - 100, 10)
        self.fps = []

    def update(self):
        """Обновить значение FPS"""
        global clock
        current_fps = clock.get_fps()
        del self.fps[100:]
        self.fps.append(current_fps)
        if self.show:
            fps = sum(self.fps) / len(self.fps)
            msg = '%5.0f FPS' % fps
        else:
            msg = ''
        self.image = self.font.render(msg, 1, self.color)


class HoneyMeter(pygame.sprite.DirtySprite):
    """Отображение кол-ва мёда"""
    _layer = 5

    def __init__(self, pos, color=(255, 255, 0)):
        """Создать индикатор FPS"""
        self.containers = self.containers, _sprites_by_layer[self._layer]
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(None, 27)
        self.color = color
        self.image = self.font.render('-', 0, self.color)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos[0], SCREENRECT.height - pos[1])

    def set_value(self, value):
        self.value = value

    def update(self):
        msg = '%5.0f' % self.value
        self.image = self.font.render(msg, 1, self.color)


def random_number(a=0, b=300):
    """
        Выдать случайное целое из диапазона [a,b]
    """
    return random.randint(a, b)

_random_point_border = 42


def _get_random_coordinate(high):
    return random_number(_random_point_border, high - _random_point_border)


def random_point():
    """
        Сгенерировать случнайную точку внутри области рисования
    """
    x = _get_random_coordinate(SCREENRECT.width)
    y = _get_random_coordinate(SCREENRECT.height)
    return Point(x, y)


if __name__ == '__main__':

    game = GameEngine("test", resolution=(700, 700))
    scene = Scene(beehives_count=2, flowers_count=40, speed=10)

    class MyBee(Bee):
        my_beehave = scene.beehives[0]

        def get_nearest_flower(self):
            nearest_flower = None
            for flower in scene.flowers:
                if flower.honey > 0:
                    if nearest_flower is None or self.distance_to(flower) < self.distance_to(nearest_flower):
                        nearest_flower = flower
            return nearest_flower

        def go_next_flower(self):
            if self.is_full():
                self.move_at(self.my_beehave)
            else:
                nearest_flower = self.get_nearest_flower()
                if nearest_flower is not None:
                    self.move_at(nearest_flower)
                elif self.honey > 0:
                    self.move_at(self.my_beehave)
                else:
                    i = random_number(0, len(scene.flowers) - 1)
                    self.move_at(scene.flowers[i])

        def on_born(self):
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

    class SecondBee(MyBee):
        my_beehave = scene.beehives[1]

        def get_nearest_flower(self):
            nearest_flower = None
            max_honey = 0
            for flower in scene.flowers:
                if flower.honey == 0:
                    continue
                distance = self.distance_to(flower)
                if distance > 200:
                    continue
                if flower.honey > max_honey:
                    nearest_flower = flower
                    max_honey = flower.honey
                elif flower.honey == max_honey:
                    if nearest_flower is None:
                        nearest_flower = flower
                    elif distance < self.distance_to(nearest_flower):
                        nearest_flower = flower
            return nearest_flower

    bees = [MyBee(pos=Point(100, 100)) for i in range(10)]
    bees_2 = [SecondBee(pos=scene.beehives[1].coord) for i in range(10)]

    while game.go():
        pass
