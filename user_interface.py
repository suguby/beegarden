#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pygame
import random
from pygame.constants import RLEACCEL, QUIT, KEYDOWN, K_ESCAPE, K_f, K_d, K_s
from pygame.rect import Rect
from constants import NEAR_RADIUS
from geometry import Point, Vector

SCREENRECT = None
MAX_LAYERS = 3
SPRITES_GROUPS = [pygame.sprite.Group() for i in range(MAX_LAYERS + 1)]


class ObjectToSprite(object):
    """
        Интерфейс получения данных об объекте спрайтом
    """

    def get_coordinates(self):
        """
            Получить координаты
        """
        raise NotImplementedError

    def get_load_value(self):
        """
            Получить величену загрузки медем
        """
        raise NotImplementedError


class BaseSprite(ObjectToSprite, pygame.sprite.DirtySprite):
    """Класс отображения объектов на экране"""
    _img_file_name = 'empty.png'
    _layer = 0
    radius = 1
    speed = 3
    _sprites_count = 0

    coordinate = property(lambda self: self.get_coordinates)

    def __init__(self):
        """Создать объект в указанном месте"""

        if self._layer > MAX_LAYERS:
            self._layer = MAX_LAYERS
        if self._layer < 0:
            self._layer = 0
        self.containers = self.containers, SPRITES_GROUPS[self._layer]
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = load_image(self._img_file_name, -1)
        self.images = [self.image, pygame.transform.flip(self.image, 1, 0)]
        self.rect = self.image.get_rect()

        #if pos is None:
        #    self.coord = Point(100, 100)
        #else:
        #    self.coord = Point(pos)
        #self.target_coord = Point(0, 0)
        #self.rect.center = self.coord.to_screen()
        #
        #self.vector = Vector()
        #self.is_moving = False
        #self.course = self.vector.angle
        #
        #self.load_value = 0
        #self.load_value_px = 0

        BaseSprite._sprites_count += 1
        self._id = BaseSprite._sprites_count

    def __str__(self):
        return 'sprite %s: %s %s %s %s' % (self._id, self.coord, self.vector, self.is_moving, self.is_turning)

    def __repr__(self):
        return str(self)

    x = property(lambda self: self.coordinate.int_x, doc="текущая позиция X объекта")
    y = property(lambda self: self.coordinate.int_y, doc="текущая позиция Y объекта")
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
        if self.vector.dx >= 0:
            self.image = self.images[1].copy()
        else:
            self.image = self.images[0].copy()
        #print self.course, self.vector.angle

        self.rect.center = self.coord.to_screen()

        load_value = self.get_load_value()
        if load_value:
            load_value_px = int((load_value / 100.0) * self.w)
            pygame.draw.line(self.image, (0, 255, 7), (0, 0), (load_value_px, 0), 3)

        # TODO сделать проверку на выход за границы экрана
        #if not SCREENRECT.contains(self.rect):
        #    if self.rect.top < SCREENRECT.top:
        #        self.rect.top = SCREENRECT.top
        #    if self.rect.bottom > SCREENRECT.bottom:
        #        self.rect.bottom = SCREENRECT.bottom
        #    if self.rect.left < SCREENRECT.left:
        #        self.rect.left = SCREENRECT.left
        #    if self.rect.right > SCREENRECT.right:
        #        self.rect.right = SCREENRECT.right
        #    self.stop()


class GameObject(ObjectToSprite):

    speed = property(lambda self: self._speed)

    def __init__(self, pos=None):

        if pos is None:
            self.coord = Point(100, 100)
        else:
            self.coord = Point(pos)
        self.target_coord = Point(0, 0)

        self._vector = Vector()
        self._is_moving = False
        self.course = self._vector.angle

        self._speed = float(self._speed) - random.random()  # чуть-чуть разная скорость
        self.on_born()

    def on_born(self):
        """Обработчик события 'рождение' """
        pass

    def on_stop_at_target(self):
        """Обработчик события 'остановка у цели' """
        pass

    def move_at(self, target):
        """ Задать движение к указанной точке <объект/точка/координаты>, <скорость> """
        if isinstance(target, Point):
            self.target_coord = target
        elif isinstance(target, GameObject):
            self.target_coord = target.coord
        else:
            raise Exception("move_at: target {} must be GameObject or Point!".format(target))
        self._vector = Vector(point1=self.coord, point2=self.target_coord, module=self._speed)
        self._is_moving = True

    def stop(self):
        """ Остановить объект """
        self._is_moving = False

    def distance_to(self, obj):
        """ Расстояние до объекта <объект/точка>"""
        if isinstance(obj, GameObject):
            return self.coord.distance_to(obj.coord)
        if isinstance(obj, Point):
            return self.coord.distance_to(obj)
        raise Exception("sprite.distance_to: obj {} must be GameObject or Point!".format(obj))

    def near(self, obj, radius=NEAR_RADIUS):
        """ Проверка близости к объекту <объект/точка>"""
        return self.distance_to(obj) <= radius

    def _update(self):
        if self._is_moving:
            self.coord.add(self._vector)
            if self.near(self.target_coord):
                self.stop()
                self.on_stop_at_target()

#class UserInterface:
#    """Отображение игры: отображение спрайтов
#    и взаимодействия с пользователем"""
#
#    def __init__(self, name):
#        """Создать окно игры. """
#        global SCREENRECT
#
#        pygame.init()
#        SCREENRECT = Rect((0, 0),
#                          (constants.field_width, constants.field_height))
#        self.screen = pygame.display.set_mode(SCREENRECT.size)
#        pygame.display.set_caption(name)
#
#        self.background = pygame.Surface(self.screen.get_size())  # и ее размер
#        self.background = self.background.convert()
#        self.background.fill(constants.background_color)  # заполняем цветом
#        self.clear_screen()
#
#        self.all = pygame.sprite.LayeredUpdates()
#        MshpSprite.sprite_containers = self.all
#        Fps.sprite_containers = self.all
#
#        global clock
#        clock = pygame.time.Clock()
#        self.fps_meter = Fps(color=(255, 255, 0))
#        self.max_fps = constants.max_fps
#
#        self._step = 0
#        self.debug = False
#
#    def get_keyboard_and_mouse_state(self):
#        self.one_step = False
#        self.switch_debug = False
#        self.the_end = False
#
#        for event in pygame.event.get():
#            if event.type == KEYDOWN and event.key == K_f:
#                self.fps_meter.show = not self.fps_meter.show
#
#            if (event.type == QUIT) \
#                or (event.type == KEYDOWN and event.key == K_ESCAPE) \
#                or (event.type == KEYDOWN and event.key == K_q):
#                self.the_end = True
#            if event.type == KEYDOWN and event.key == K_d:
#                self.switch_debug = True
#            if event.type == KEYDOWN and event.key == K_s:
#                self.one_step = True
#        key = pygame.key.get_pressed()
#        if key[pygame.K_g]:  # если нажата и удерживается
#            self.one_step = True
#        pygame.event.pump()
#
#        self.mouse_pos = pygame.mouse.get_pos()
#        self.mouse_buttons = pygame.mouse.get_pressed()
#
#    def clear_screen(self):
#        self.screen.blit(self.background, (0, 0))
#        pygame.display.flip()
#
#    def _draw_radar_outline(self, obj):
#        from math import pi, cos, sin
#        angle_r = (obj.course - constants.tank_radar_angle // 2) / 180.0 * pi
#        angle_l = (obj.course + constants.tank_radar_angle // 2) / 180.0 * pi
#        points = [
#            Point(obj.coord.x + cos(angle_r) * constants.tank_radar_range,
#                  obj.coord.y + sin(angle_r) * constants.tank_radar_range),
#            Point(obj.coord.x + cos(angle_l) * constants.tank_radar_range,
#                  obj.coord.y + sin(angle_l) * constants.tank_radar_range),
#            Point(obj.coord.x,
#                  obj.coord.y)
#        ]
#        points = [x.to_screen() for x in points]
#        pygame.draw.aalines(self.screen,
#                            obj._debug_color,
#                            True,
#                            points)
#
#    def draw(self):
#        """Отрисовка спрайтов на экране"""
#
#        #update all the sprites
##        for sprites in _sprites_by_layer:
##            sprites.update()
#        self.all.update()
#
#        #draw the scene
#        if self.debug:
#            self.screen.blit(self.background, (0, 0))
#            dirty = self.all.draw(self.screen)
#            for obj in self.all:
#                if obj.type() == 'Tank' and obj._selected:
#                    self._draw_radar_outline(obj)
##            [self._draw_radar_outline(obj) for obj in self.all \
##                        if obj.type() == 'Tank' and obj._selected]
#            pygame.display.flip()
#        else:
#            # clear/erase the last drawn sprites
#            self.all.clear(self.screen, self.background)
#            dirty = self.all.draw(self.screen)
#            pygame.display.update(dirty)
#
#        #cap the framerate
#        clock.tick(self.max_fps)
#        return True


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


class HoneyMeter(pygame.sprite.DirtySprite):
    """Отображение кол-ва мёда"""
    _layer = MAX_LAYERS

    def __init__(self, pos, color=(255, 255, 0)):
        self.containers = self.containers, SPRITES_GROUPS[self._layer]
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
        BaseSprite.containers = self.all
        Fps.containers = self.all
        HoneyMeter.containers = self.all

        global clock
        clock = pygame.time.Clock()
        self.fps_meter = Fps(color=(255, 255, 0))
        self.max_fps = max_fps

        self.debug = False

    def _draw_scene(self):
        # TODO ускорить через начальную отрисовку всех цветков и ульев в бакграунд
        # clear/erase the last drawn sprites
        self.all.clear(self.screen, self.background)
        #update all the sprites
        self.all.update()
        #draw the scene
        dirty = self.all.draw(self.screen)
        pygame.display.update(dirty)
        #cap the framerate
        clock.tick(self.max_fps)

    def _proceed_keyboard(self):
        one_step = False
        for event in pygame.event.get():
            if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.halt = True
            if event.type == KEYDOWN and event.key == K_f:
                self.fps_meter.show = not self.fps_meter.show
            if event.type == KEYDOWN and event.key == K_d:
                self.debug = not self.debug
            if event.type == KEYDOWN and event.key == K_s:
                one_step = True
        if self.debug and not one_step:
            return False
        return True

    def go(self, debug=False):
        self.debug = debug
        if self.debug:
            self._draw_scene()
        self.halt = False
        while not self.halt:
            if self._proceed_keyboard():
                self._draw_scene()