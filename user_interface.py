# -*- coding: utf-8 -*-
"""Взаимодействие с пользователем - показываем и слушаем ответ"""

import os
import pygame
from pygame.constants import RLEACCEL, QUIT, KEYDOWN, K_ESCAPE, K_f, K_d, K_s, K_q

_MAX_LAYERS = 3
_SPRITES_GROUPS = [pygame.sprite.Group() for i in range(_MAX_LAYERS + 1)]


class BaseSprite(pygame.sprite.DirtySprite):
    """Класс отображения объектов на экране"""
    _sprites_count = 0

    def __init__(self, obj_to_sprite, img_file_name, layer=0):
        self.obj_to_sprite = obj_to_sprite
        self._img_file_name = img_file_name
        self._layer = layer
        if self._layer > _MAX_LAYERS:
            self._layer = _MAX_LAYERS
        if self._layer < 0:
            self._layer = 0
        self.containers = BaseSprite.containers, _SPRITES_GROUPS[self._layer]
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.image = load_image(self._img_file_name, -1)
        self._images = [
            self.image,
            pygame.transform.flip(self.image, 1, 0),
            pygame.transform.flip(self.image, 0, 1)
        ]
        self.rect = self.image.get_rect()

        BaseSprite._sprites_count += 1
        self._id = BaseSprite._sprites_count

    def __str__(self):
        return 'sprite %s: %s %s %s %s' % (self._id, self.coord, self.vector, self.is_moving, self.is_turning)

    def __repr__(self):
        return str(self)

    def update(self):
        """Внутренняя функция для обновления переменных отображения"""
        direction = self.obj_to_sprite._get_direction()
        if self.obj_to_sprite._is_dead():
            self.image = self._images[2].copy()
        elif abs(direction) > 90:
            self.image = self._images[0].copy()
        else:
            self.image = self._images[1].copy()

        self.rect.center = self.obj_to_sprite._get_coordinates().to_screen(height=UserInterface.screen_height)

        load_value = self.obj_to_sprite._get_load_value()
        if load_value:
            load_value_px = int(load_value * self.rect.width)
            HONEY_METER_COLOR = UserInterface.scene.get_theme_constant('HONEY_METER_COLOR')
            pygame.draw.line(self.image, HONEY_METER_COLOR, (0, 0), (load_value_px, 0), 3)


class HoneyMeter(pygame.sprite.DirtySprite):
    """Отображение кол-ва мёда"""
    _layer = _MAX_LAYERS

    def __init__(self, pos, color=(255, 255, 0)):
        self.containers = self.containers, _SPRITES_GROUPS[self._layer]
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(None, 27)
        self.color = color
        self.image = self.font.render('-', 0, self.color)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos.int_x, UserInterface.screen_height - pos.int_y)
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
        self.rect = self.rect.move(UserInterface.screen_width - 100, 10)
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

    screen_width = 1024
    screen_height = 768
    scene = None  # устанавливается при генерации сцены

    def __init__(self, name, max_fps=60, resolution=None):
        """Создать окно игры. """

        pygame.init()
        if resolution is None:
            resolution = [UserInterface.screen_width, UserInterface.screen_height]
            # resolution = list(pygame.display.list_modes()[0])
            resolution[1] -= 100  # хак, что бы были видны ульи внизу экрана
        self.screen = pygame.display.set_mode(resolution)
        UserInterface.screen_width, UserInterface.screen_height = self.screen.get_size()
        pygame.display.set_caption(name)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        try:
            image = load_image('background.jpg', -1)
            self.background.blit(image, (0, 0))
        except ImageLoadError:
            background_color = UserInterface.scene.get_theme_constant('BACKGROUND_COLOR')
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

class ImageLoadError(Exception):
    pass

def load_image(name, colorkey=None):
    """Загрузить изображение из файла"""
    PICTURES_PATH = UserInterface.scene.get_theme_constant('PICTURES_PATH')
    fullname = os.path.join(PICTURES_PATH, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        raise ImageLoadError("Cannot load image:".format(name))
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image


