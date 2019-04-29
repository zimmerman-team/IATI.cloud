"""
Implementation of `modhex encoding <http://www.yubico.com/modhex-calculator>`_,
which uses keyboard-independent characters.

::

    hex digit:    0123456789abcdef
    modhex digit: cbdefghijklnrtuv
"""

from binascii import hexlify, unhexlify
from functools import partial

from six import int2byte, iterbytes


__all__ = ['modhex', 'unmodhex', 'is_modhex', 'hex_to_modhex', 'modhex_to_hex']


def modhex(data):
    """
    Encode a string of bytes as modhex.

    >>> modhex(b'abcdefghijklmnop') == b'hbhdhehfhghhhihjhkhlhnhrhthuhvic'
    True
    """
    return hex_to_modhex(hexlify(data))


def unmodhex(encoded):
    """
    Decode a modhex string to its binary form.

    >>> unmodhex(b'hbhdhehfhghhhihjhkhlhnhrhthuhvic') == b'abcdefghijklmnop'
    True
    """
    return unhexlify(modhex_to_hex(encoded))


def is_modhex(encoded):
    """
    Returns ``True`` iff the given string is valid modhex.

    >>> is_modhex(b'cbdefghijklnrtuv')
    True
    >>> is_modhex(b'cbdefghijklnrtuvv')
    False
    >>> is_modhex(b'cbdefghijklnrtuvyy')
    False
    """
    if any(c not in modhex_chars for c in encoded):
        return False
    elif len(encoded) % 2 != 0:
        return False
    else:
        return True


def hex_to_modhex(hex_str):
    """
    Convert a string of hex digits to a string of modhex digits.

    >>> hex_to_modhex(b'69b6481c8baba2b60e8f22179b58cd56') == b'hknhfjbrjnlnldnhcujvddbikngjrtgh'
    True
    >>> hex_to_modhex(b'6j')
    Traceback (most recent call last):
        ...
    ValueError: Illegal hex character in input
    """
    try:
        return b''.join(int2byte(hex_to_modhex_char(b))
                        for b in iterbytes(hex_str.lower()))
    except ValueError:
        raise ValueError('Illegal hex character in input')


def modhex_to_hex(modhex_str):
    """
    Convert a string of modhex digits to a string of hex digits.

    >>> modhex_to_hex(b'hknhfjbrjnlnldnhcujvddbikngjrtgh') == b'69b6481c8baba2b60e8f22179b58cd56'
    True
    >>> modhex_to_hex(b'hbhdxx')
    Traceback (most recent call last):
        ...
    ValueError: Illegal modhex character in input
    """
    try:
        return b''.join(int2byte(modhex_to_hex_char(b))
                        for b in iterbytes(modhex_str.lower()))
    except ValueError:
        raise ValueError('Illegal modhex character in input')


#
# Internals
#

def lookup(alist, key):
    try:
        return next(v for k, v in alist if k == key)
    except StopIteration:
        raise ValueError()

hex_chars = b'0123456789abcdef'
modhex_chars = b'cbdefghijklnrtuv'

hex_to_modhex_map = list(zip(iterbytes(hex_chars), iterbytes(modhex_chars)))
modhex_to_hex_map = list(zip(iterbytes(modhex_chars), iterbytes(hex_chars)))

hex_to_modhex_char = partial(lookup, hex_to_modhex_map)
modhex_to_hex_char = partial(lookup, modhex_to_hex_map)
