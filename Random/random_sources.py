# -*- coding: utf-8 -*-
''' random.sources.py

This module wraps ways of getting some randomness.

@author: Richard Mathot
'''

# pylint: disable=E0611
from os import urandom


def randint(q):
    '''Returns an integer between 0 and q (q should be < 2^256)'''
    assert q < 2 ** 256
    return get_256_random_bits_os() % q


def get_256_random_bits_os():
    '''Generates a random integer whose length is 256 bits (32 bytes),
       by using system pseudorandom bytes source'''
    return int(urandom(32).encode('hex'), 16)
