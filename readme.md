NSMBLib-Updated
===============

**NSMBLib** is a small accelerator module used by the Reggie! NSMBW Level
Editor and the Puzzle NSMBW Tileset Editor to improve performance when loading
and/or saving files. It is an optional dependency in both applications.

As the original NSMBLib has been abandoned for years, **NSMBLib-Updated** is a
currently maintained fork, which adds support for Python 3.


Installation
------------

NSMBLib-Updated can be installed from PyPI with pip: `pip install nsmblib`. It
is also often included with builds of Reggie! and Puzzle.


Versions
--------

There are two main versions of the original NSMBLib in circulation, 0.4
(bundled with Reggie!) and 0.5 (bundled with Puzzle). Version 0.5 adds an LZ11
compression function (used by Puzzle), but it does not actually work correctly
and produces mangled output data.

NSMBLib-Updated includes a working LZ11 compression function, and is thus
API-compatible with NSMBLib 0.5 (and backwards-compatible with 0.4).

Since every release of NSMBLib-Updated has the exact same API as NSMBLib 0.5,
NSMBLib-Updated uses calendar versioning to distinguish releases (which only
ever fix bugs or broaden compatibility).


API
---

- `nsmblib.getVersion() -> int`:
  Returns the minor version number. For example, for NSMBLib 0.5, returns 5.
- `nsmblib.decompress11LZS(data: bytes) -> bytes`:
  Decompresses LZ11-compressed data.
- `nsmblib.compress11LZS(data: bytes) -> bytes`:
  Compresses data into LZ11 format.
- `nsmblib.decodeTileset(data: bytes) -> bytes`:
  Decodes uncompressed NSMBW tileset image data to a 1024x256 pixel array in
  ARGB32 Premultiplied color format. You can convert this to a PyQt QImage like
  so:
  `image = QtGui.QImage(decodedData, 1024, 256, 4096, QtGui.QImage.Format_ARGB32_Premultiplied)`
- `nsmblib.decodeTilesetNoAlpha(data: bytes) -> bytes`:
  Same as `decodeTileset()`, but locks the alpha channel for all pixels to 255.


Original Readme
---------------

Extracted from nsmblibmodule.c:

    New Super Mario Bros Wii Module for Python
    Written by Treeki; 19th December 2009

    This module is used by the Reggie! level editor
    in order to speed up some algorithms like decoding
    textures and decompressing data. Slower Python versions
    of the functions are available in reggie.py, and will be
    used if this module isn't available for whatever reason.

    Update Log:
    0.1: First version
    0.2: Added nsmblib_decompress11LZS
    0.3: Fixed hosed memory addressing in nsmblib_decompress11LZS
    0.4: Added nsmblib_getVersion
    0.5: Added nsmblib_compress11LZS (thanks to puyo_tools
         for the original C# code)


Licensing
---------

NSMBLib and NSMBLib-Updated are released under the GNU General Public License
v2. See the license file for more information.
