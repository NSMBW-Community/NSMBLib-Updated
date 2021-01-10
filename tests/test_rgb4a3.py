import struct
import sys

import nsmblib


IS_PY3 = (sys.version_info.major >= 3)


def premultiply(r, g, b, a):
    """
    Ported from nsmblibmodule.c
    """
    x = (a << 24) | (r << 16) | (g << 8) | b

    t = (x & 0xff00ff) * a
    t = (t + ((t >> 8) & 0xff00ff) + 0x800080) >> 8
    t &= 0xff00ff
    x = ((x >> 8) & 0xff) * a
    x = (x + ((x >> 8) & 0xff) + 0x80)
    x &= 0xff00
    x |= t | (a << 24)

    a, r, g, b = (x >> 24), ((x >> 16) & 0xff), ((x >> 8) & 0xff), (x & 0xff)
    return r, g, b, a


def do_test_tileset_decode_function(func, alphaEnabled):
    """
    Generic function for testing decodeTileset() and decodeTilesetNoAlpha()
    """
    # Create a texture data buffer
    tset_data = bytearray(1024 * 256 * 2)

    # Fill each pixel, row by row, with increasing 16-bit integers (so
    # we can check every color).
    # Need to account for tiling, also
    tx = ty = 0
    idx = 0
    for i in range(16384):
        for y in range(ty, ty+4):
            for x in range(tx, tx+4):
                val = ((y * 1024) + x) & 0xffff
                tset_data[idx * 2 : idx * 2 + 1] = struct.pack('>H', val)
                idx += 1

        tx += 4
        if tx >= 1024: tx = 0; ty += 4

    # Run it through the nsmblib decoder function
    out1 = func(bytes(tset_data))

    # Now check each color
    for d in range(0x10000):
        # Decode the color manually
        if d & 0x8000 == 0:
            red = ((d >> 8) & 0xF) * 17
            green = ((d >> 4) & 0xF) * 17
            blue = (d & 0xF) * 17
            alpha = d >> 12
            alpha = alpha << 5 | alpha << 2 | alpha >> 1
        else:
            red = (d >> 10) & 0x1F
            red = red << 3 | red >> 2
            green = (d >> 5) & 0x1F
            green = green << 3 | green >> 2
            blue = d & 0x1F
            blue = blue << 3 | blue >> 2
            alpha = 0xFF

        # Get nsmblib's decoded color
        b, g, r, a = out1[d * 4 : d * 4 + 4]

        if not IS_PY3:
            b, g, r, a = ord(b), ord(g), ord(r), ord(a)

        # Compare
        error_msg = '%04x decoded incorrectly' % d
        if alphaEnabled:
            red, green, blue, alpha = premultiply(red, green, blue, alpha)
            if alpha == 0:
                assert a == 0, error_msg
            else:
                assert (r, g, b, a) == (red, green, blue, alpha), error_msg
        else:
            assert (r, g, b, a) == (red, green, blue, 0xFF), error_msg


def test_decodeTileset():
    """
    Test decodeTileset()
    """
    do_test_tileset_decode_function(nsmblib.decodeTileset, True)


def test_decodeTilesetNoAlpha():
    """
    Test decodeTilesetNoAlpha()
    """
    do_test_tileset_decode_function(nsmblib.decodeTilesetNoAlpha, False)
