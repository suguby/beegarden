# -*- coding: utf-8 -*-


class HoneyHolder(object):
    """Класс объекта, который может нести мёд"""
    _honey_speed = 1
    _honey = 0
    _max_honey = 0
    _honey_source = None
    _honey_state = 'hold'

    def set_inital_honey(self, loaded, maximum):
        """Задать начальние значения: honey_loaded - сколько изначально мёда, honey_max - максимум"""
        self._honey = loaded
        if maximum == 0:
            raise Exception("honey_max can't be zero!")
        self._max_honey = maximum

    @property
    def honey(self):
        return self._honey

    @property
    def meter_1(self):
        return self._honey / float(self._max_honey)

    def _end_exchange(self, event):
        self._honey_source = None
        self._honey_state = 'hold'
        event()

    def _stop_loading_honey(self):
        self._honey_source = None
        self._honey_state = 'hold'

    def _update(self, is_moving=False):
        """Внутренняя функция для обновления переменных отображения"""
        if is_moving or (self._honey_source and not self.near(self._honey_source)):
            self._stop_loading_honey()
        elif self._honey_state == 'loading':
            honey = self._honey_source._get_honey()
            if not honey or not self._put_honey(honey):
                self._end_exchange(event=self.on_honey_loaded)
        elif self._honey_state == 'unloading':
            honey = self._get_honey()
            if not honey or not self._honey_source._put_honey(honey):
                self._end_exchange(event=self.on_honey_unloaded)

    def _get_honey(self):
        if self._honey > self._honey_speed:
            self._honey -= self._honey_speed
            return self._honey_speed
        elif self._honey > 0:
            value = self._honey
            self._honey = 0
            return value
        return 0.0

    def _put_honey(self, value):
        self._honey += value
        if self._honey > self._max_honey:
            self._honey = self._max_honey
            return False
        return True

    def on_honey_loaded(self):
        """Обработчик события 'мёд загружен' """
        pass

    def on_honey_unloaded(self):
        """Обработчик события 'мёд разгружен' """
        pass

    def load_honey_from(self, source):
        """Загрузить мёд от ... """
        self._honey_state = 'loading'
        self._honey_source = source

    def unload_honey_to(self, target):
        """Разгрузить мёд в ... """
        self._honey_state = 'unloading'
        self._honey_source = target

    def is_full(self):
        """полностью заполнен?"""
        return self.honey >= self._max_honey




