#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pygame
from pygame.constants import RLEACCEL, QUIT, KEYDOWN, K_ESCAPE, K_f, K_d, K_s, K_q
from pygame.rect import Rect
from common import ObjectToSprite

SCREENRECT = None
MAX_LAYERS = 3
SPRITES_GROUPS = [pygame.sprite.Group() for i in range(MAX_LAYERS + 1)]


class BaseSprite(ObjectToSprite, pygame.sprite.DirtySprite):
    """Класс отображения объектов на экране"""
    _img_file_name = 'empty.png'
    _layer = 0
    _sprites_count = 0

    def __init__(self):
        if self._layer > MAX_LAYERS:
            self._layer = MAX_LAYERS
        if self._layer < 0:
            self._layer = 0
        self.containers = BaseSprite.containers, SPRITES_GROUPS[self._layer]
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = load_image(self._img_file_name, -1)
        self._images = [self.image, pygame.transform.flip(self.image, 1, 0)]
        self.rect = self.image.get_rect()

        BaseSprite._sprites_count += 1
        self._id = BaseSprite._sprites_count

    def __str__(self):
        return 'sprite %s: %s %s %s %s' % (self._id, self.coord, self.vector, self.is_moving, self.is_turning)

    def __repr__(self):
        return str(self)

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        if 90 < self._get_direction() < 180:
            self.image = self._images[1].copy()
        else:
            self.image = self._images[0].copy()

        self.rect.center = self._get_coordinates().to_screen(height=SCREENRECT.height)

        load_value = self._get_load_value()
        if load_value:
            load_value_px = int(load_value * self.w)
            pygame.draw.line(self.image, (0, 255, 7), (0, 0), (load_value_px, 0), 3)


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
        self.value = 0.0

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


class UserInterface:
    """Отображение игры: отображение спрайтов
    и взаимодействия с пользователем"""

    def __init__(self, name, background_color=None, max_fps=60, resolution=None):
        """Создать окно игры. """
        global SCREENRECT

        pygame.init()
        if background_color is None:
            background_color = (87, 144, 40)
        if resolution is None:
            resolution = (1024, 768)
        SCREENRECT = Rect((0, 0), resolution)
        self.screen = pygame.display.set_mode(SCREENRECT.size)
        pygame.display.set_caption(name)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(background_color)
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
        self.the_end = False
        self.switch_debug = False
        self.one_step = False

    def get_keyboard_and_mouse_state(self):
        self.one_step = False
        self.switch_debug = False
        self.the_end = False

        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_f:
                self.fps_meter.show = not self.fps_meter.show

            if (event.type == QUIT) \
                or (event.type == KEYDOWN and event.key == K_ESCAPE) \
                or (event.type == KEYDOWN and event.key == K_q):
                self.the_end = True
            if event.type == KEYDOWN and event.key == K_d:
                self.switch_debug = True
            if event.type == KEYDOWN and event.key == K_s:
                self.one_step = True
        key = pygame.key.get_pressed()
        if key[pygame.K_g]:  # если нажата и удерживается
            self.one_step = True
        pygame.event.pump()

        #self.mouse_pos = pygame.mouse.get_pos()
        #self.mouse_buttons = pygame.mouse.get_pressed()

    def clear_screen(self):
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def draw(self):
        """Отрисовка спрайтов на экране"""

        self.all.update()
        if self.debug:
            self.screen.blit(self.background, (0, 0))
            dirty = self.all.draw(self.screen)
            pygame.display.flip()
        else:
            # clear/erase the last drawn sprites
            self.all.clear(self.screen, self.background)
            dirty = self.all.draw(self.screen)
            pygame.display.update(dirty)

        #cap the framerate
        clock.tick(self.max_fps)
        return True


class GameEngine:
    """Deprecated! Игровой движок. Выполняет все функции по отображению спрайтов и взаимодействия с пользователем"""

    def __init__(self, name, background_color=None, max_fps=60, resolution=None):
        pass

    def go(self, debug=False):
        pass
