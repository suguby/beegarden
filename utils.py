#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random


def random_number(a=0, b=300):
    """
        Выдать случайное целое из диапазона [a,b]
    """
    return random.randint(a, b)