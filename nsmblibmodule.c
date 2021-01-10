#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "bytesobject.h"
#define s32 signed int
#define s16 signed short
#define s8 signed char
#define u32 unsigned int
#define u16 unsigned short
#define u8 unsigned char

/************************************************************
 * New Super Mario Bros Wii Module for Python               *
 * Written by Treeki; 19th December 2009                    *
 * Ported to Python 3 by RoadrunnerWMC                      *
 ************************************************************
 * This module is used by the Reggie! level editor          *
 * in order to speed up some algorithms like decoding       *
 * textures and decompressing data. Slower Python versions  *
 * of the functions are available in reggie.py, and will be *
 * used if this module isn't available for whatever reason. *
 ************************************************************/

/* Update Log:
 * -----------
 * 0.1: First version
 * 0.2: Added nsmblib_decompress11LZS
 * 0.3: Fixed hosed memory addressing in nsmblib_decompress11LZS
 * 0.4: Added nsmblib_getVersion
 * 0.4.1: Added Python 3 compatibility
 * 0.5: Added nsmblib_compress11LZS (thanks to puyo_tools
 *      for the original C# code) [rewritten by RoadrunnerWMC],
        and added nsmblib_decodeTilesetNoAlpha
 */

#define CURRENT_VERSION 5

static PyObject *nsmblib_getVersion(PyObject *self, PyObject *args) {
    /* Gets the current version of the NSMB module.
     * Returns: int (version number * 10)
     * Parameters: none
     */

     return Py_BuildValue("i", CURRENT_VERSION);
}

static PyObject *nsmblib_decompress11LZS(PyObject *self, PyObject *args) {
    /* Decompresses a file using LZSS 0x11 variant.
     * Returns: bytes (containing the decompressed data)
     * Parameters:
     *  - bytes data (containing the compressed data)
     */

    const u8 *data;
    Py_ssize_t datalength;

    u8 *decoded;
    PyObject *retvalue;
    int decompsize;

    /* used while decompressing */
    int curr_size;
    const u8 *source;
    u8 *dest;
    int len, i, j, cdest, disp, flag;
    u8 b1, b2, b3, bt, flags;

    /* get the arguments */
    if (!PyArg_ParseTuple(args, "s#", &data, &datalength))
        return NULL;

    /* parse the file itself */
    source = data;
    if (*(source++) != 0x11) {
        /* it's invalid */
        Py_INCREF(Py_None);
        return Py_None;
    }

    decompsize = 0;
    for (i = 0; i < 3; i++) {
        decompsize += (*(source++)) << (i * 8);
    }

    if (decompsize == 0) {
        for (i = 0; i < 4; i++) {
            decompsize += (*(source++)) << (i * 8);
        }
    }

    /* if it's obviously invalid, kill it */
    if (decompsize > 0x800000) {
        /* fixed 8mb limit */
        PySys_WriteStdout("Too big! %d\n", decompsize);
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* allocate a buffer */
    decoded = (u8*)PyMem_Malloc(decompsize);
    if (decoded == NULL)
        return PyErr_NoMemory();

    /* now we can start going through everything */
    dest = decoded;
    curr_size = 0;

    while (curr_size < decompsize) {
        flags = *(source++);

        for (i = 0; i < 8 && curr_size < decompsize; i++) {
            flag = (flags & (0x80 >> i));
            if (flag > 0) {
                b1 = *(source++);

                switch (b1 >> 4) {
                    case 0:
                        len = b1 << 4;
                        bt = *(source++);
                        len |= bt >> 4;
                        len += 0x11;

                        disp = (bt & 0x0F) << 8;
                        b2 = *(source++);
                        disp |= b2;
                        break;

                    case 1:
                        bt = *(source++);
                        b2 = *(source++);
                        b3 = *(source++);

                        len = (b1 & 0xF) << 12;
                        len |= (bt << 4);
                        len |= (b2 >> 4);
                        len += 0x111;
                        disp = (b2 & 0xF) << 8;
                        disp |= b3;
                        break;

                    default:
                        len = (b1 >> 4) + 1;
                        disp = (b1 & 0x0F) << 8;
                        b2 = *(source++);
                        disp |= b2;
                        break;
                }

                if (disp > curr_size) {
                    /* how's that for failure? */
                    PyMem_Free(decoded);
                    Py_INCREF(Py_None);
                    return Py_None;
                }

                cdest = curr_size;

                for (j = 0; j < len && curr_size < decompsize; j++) {
                    *(dest++) = decoded[cdest - disp - 1 + j];
                    curr_size++;
                }

                if (curr_size > decompsize) {
                    break;
                }
            } else {
                *(dest++) = *(source++);
                curr_size++;

                if (curr_size > decompsize) {
                    break;
                }
            }
        }

    }

    /* return it */
    retvalue = PyBytes_FromStringAndSize((const char*)decoded, decompsize);
    PyMem_Free(decoded);

    return retvalue;
}


void LZSearch(u8 *data, int offset, int length, int *ret1, int *ret2) {
    int windowsize, maxmatchamount;
    int start;
    int recordoffset, recordlen;
    int matchstart, thismaxmatchamount, matchlen;

    windowsize = 0x1000;
    maxmatchamount = 0xFFFF + 273;

    if (windowsize > offset)
        windowsize = offset;

    start = offset - windowsize;

    if (windowsize < maxmatchamount)
        maxmatchamount = windowsize;
    if ((length - offset) < maxmatchamount)
        maxmatchamount = length - offset;

    recordoffset = -1;
    recordlen = 3;
    for (matchstart = start; matchstart < offset; matchstart++) {

        thismaxmatchamount = maxmatchamount;
        if (thismaxmatchamount > offset - matchstart)
            thismaxmatchamount = offset - matchstart;

        /* find length of match at this location */
        matchlen = 0;
        while ((matchlen < thismaxmatchamount) && (data[matchstart + matchlen] == data[offset + matchlen]))
            matchlen++;

        if (matchlen >= recordlen) {
            /* new best match! */
            recordoffset = matchstart;
            recordlen = matchlen;
        }

        if (recordlen > offset - matchstart) {
            /* no hope of finding a longer match anymore */
            break;
        }
    }

    /* return record offset and length */
    if (recordoffset == -1) {
        *ret1 = -1;
        *ret2 = -1;
    } else {
        *ret1 = offset - recordoffset;
        *ret2 = recordlen;
    }
}


static PyObject *nsmblib_compress11LZS(PyObject *self, PyObject *args) {
    /* Compresses a file using LZSS 0x11 variant.
     * Returns: bytes (containing the compressed data)
     * Parameters:
     *  - bytes data (containing the decompressed data)
     */

    const u8 *data;
    int datalength;

    u8 *src_ptr, *end_src_ptr;
    u8 *dest_ptr, *end_dest_ptr;

    u8 *buffer;
    int bufSize;

    int i;
    int ret1, ret2;

    PyObject *retvalue;

    /* get the arguments */
    if (!PyArg_ParseTuple(args, "s#", &data, &datalength))
        return NULL;

    /* if it's too big, kill it */
    if (datalength > 0xffffffff) {
        PySys_WriteStdout("Too big! %d\n", datalength);
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* allocate a buffer to start with */
    bufSize = datalength + 0x100;  // a bit extra to accomodate small inputs that don't compress well
    buffer = (char*)PyMem_Malloc(bufSize);
    if (buffer == NULL)
        return PyErr_NoMemory();

    src_ptr = (u8*)data;
    dest_ptr = buffer;
    end_src_ptr = src_ptr + datalength;
    end_dest_ptr = dest_ptr + bufSize;

    /* write the decomp size */
    if (datalength <= 0xFFFFFF) {
        *dest_ptr++ = 0x11;
        *dest_ptr++ = (datalength & 0xFF);
        *dest_ptr++ = ((datalength >> 8) & 0xFF);
        *dest_ptr++ = ((datalength >> 16) & 0xFF);
    } else {
        *dest_ptr++ = 0x11;
        *dest_ptr++ = 0x00;
        *dest_ptr++ = 0x00;
        *dest_ptr++ = 0x00;
        *dest_ptr++ = (datalength & 0xFF);
        *dest_ptr++ = ((datalength >> 8) & 0xFF);
        *dest_ptr++ = ((datalength >> 16) & 0xFF);
        *dest_ptr++ = ((datalength >> 24) & 0xFF);
    }

    /* start compression */
    while (src_ptr < end_src_ptr) {
        u8 flag = 0;
        u8 *flagpos = dest_ptr;
        *dest_ptr++ = flag;

        for (i = 7; i >= 0; i--) {

            LZSearch(data, src_ptr - data, datalength, &ret1, &ret2);

            if (ret2 > 0) { /* there is a compression match */
                flag |= (u8)(1 << i);

                /* write the distance/length pair */
                if (ret2 <= 0xF + 1) { /* 2 bytes */
                    *dest_ptr++ = (((ret2 - 1) & 0xF) << 4) | (((ret1 - 1) >> 8) & 0xF);
                    *dest_ptr++ = ((ret1 - 1) & 0xFF);
                } else if (ret2 <= 0xFF + 17) { /* 3 bytes */
                    *dest_ptr++ = (((ret2 - 17) & 0xFF) >> 4);
                    *dest_ptr++ = ((((ret2 - 17) & 0xF) << 4) | (((ret1 - 1) & 0xFFF) >> 8));
                    *dest_ptr++ = ((ret1 - 1) & 0xFF);
                } else { /* 4 bytes */
                    *dest_ptr++ = (0x10 | (((ret2 - 273) >> 12) & 0xF));
                    *dest_ptr++ = (((ret2 - 273) >> 4) & 0xFF);
                    *dest_ptr++ = ((((ret2 - 273) & 0xF) << 4) | (((ret1 - 1) >> 8) & 0xF));
                    *dest_ptr++ = ((ret1 - 1) & 0xFF);
                }

                src_ptr += ret2;

            } else { /* there wasn't a match */
                *dest_ptr++ = *src_ptr++;
            }

            /* check for out of bounds */
            if (src_ptr >= end_src_ptr || dest_ptr >= end_dest_ptr)
                break;
        }

        /* write the flag */
        *flagpos = flag;
    }

    /* return it! */
    retvalue = PyBytes_FromStringAndSize((const char*)buffer, dest_ptr - buffer);
    PyMem_Free(buffer);

    return retvalue;
}

static PyObject *nsmblib_decodeTilesetOptionalAlpha(PyObject *self, PyObject *args, int usealpha) {
    /* Decodes an uncompressed RGB5A4 tileset into ARGB32 Premultiplied.
     * Assumes that the size of the decoded tileset is 1024x512.
     * Returns: bytes (containing the decoded data)
     * Parameters:
     *  - bytes texture (containing the raw texture data)
     */

    const u8 *texture;
    Py_ssize_t texlength;
    u8 *decoded;
    PyObject *retvalue;

    /* used later in the pixel loop */
    const u8 *pointer;
    u32 *output;
    int tx, ty, i;
    int alpha_ormask = usealpha ? 0 : 7;

    /* get the arguments */
    if (!PyArg_ParseTuple(args, "s#", &texture, &texlength))
        return NULL;

    if (texlength < 524288) {
        /* if the input string is too small, return None */
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* allocate memory */
    decoded = (u8*)PyMem_Malloc(1048576);
    if (decoded == NULL)
        return PyErr_NoMemory();

    /* loop through every tile */
    tx = 0;
    ty = 0;
    pointer = texture;
    output = (u32*)decoded;

    for (i = 0; i < 16384; i++) {
        /* loop through every row in this tile */
        int y = ty;
        int endy = ty + 4;

        for (; y < endy; y++) {
            /* now loop through each pixel */
            int sourcey = y << 10;
            int x = tx;
            int endx = tx + 4;

            for (; x < endx; x++) {
                /* calculate this pixel */
                int pos = sourcey | x;
                u8 a = *(pointer++);
                u8 b = *(pointer++);
                u16 ab = a << 8 | b;

                if ((ab & 0x8000) == 0) {
                    /* RGB4A3 */
                    u8 alpha = (ab >> 12) | alpha_ormask;
                    u8 alpha255 = alpha << 5 | alpha << 2 | alpha >> 1;
                    u8 red = (ab >> 8) & 0xF;
                    u8 green = (ab >> 4) & 0xF;
                    u8 blue = ab & 0xF;
                    u32 x = alpha255 << 24 | red << 20 | red << 16 | green << 12 | green << 8 | blue << 4 | blue;

                    /* this code from Qt's PREMUL() inline function in
                     * src/gui/painting/qdrawhelper_p.h */
                    u32 al = x >> 24;
                    u32 t = (x & 0xff00ff) * al;
                    t = (t + ((t >> 8) & 0xff00ff) + 0x800080) >> 8;
                    t &= 0xff00ff;
                    x = ((x >> 8) & 0xff) * al;
                    x = (x + ((x >> 8) & 0xff) + 0x80);
                    x &= 0xff00;
                    x |= t | (al << 24);

                    output[pos] = x;

                } else {
                    /* RGB555 */
                    u8 red, green, blue;
                    red = (ab >> 10) & 0x1F;
                    red = red << 3 | red >> 2;
                    green = (ab >> 5) & 0x1F;
                    green = green << 3 | green >> 2;
                    blue = ab & 0x1F;
                    blue = blue << 3 | blue >> 2;
                    output[pos] = 0xFF000000 | red << 16 | green << 8 | blue;
                }
            }
        }

        /* move the positions onwards */
        tx += 4;
        if (tx >= 1024) {
            tx = 0;
            ty += 4;
        }
    }

    /* return it */
    retvalue = PyBytes_FromStringAndSize((const char*)decoded, 1048576);
    PyMem_Free(decoded);

    return retvalue;
}

static PyObject *nsmblib_decodeTileset(PyObject *self, PyObject *args) {
    return nsmblib_decodeTilesetOptionalAlpha(self, args, 1);
}

static PyObject *nsmblib_decodeTilesetNoAlpha(PyObject *self, PyObject *args) {
    return nsmblib_decodeTilesetOptionalAlpha(self, args, 0);
}

static PyMethodDef NSMBLibMethods[] = {
    {"getVersion", nsmblib_getVersion, METH_VARARGS,
     "Gets the current version of the NSMB module."},
    {"decompress11LZS", nsmblib_decompress11LZS, METH_VARARGS,
     "Decompresses a file using LZSS 0x11 variant."},
    {"compress11LZS", nsmblib_compress11LZS, METH_VARARGS,
     "Compresses a file using LZSS 0x11 variant."},
    {"decodeTileset", nsmblib_decodeTileset, METH_VARARGS,
     "Decodes an uncompressed RGB4A3 tileset into ARGB32 Premultiplied."},
    {"decodeTilesetNoAlpha", nsmblib_decodeTilesetNoAlpha, METH_VARARGS,
     "Decodes an uncompressed RGB4A3 tileset into ARGB32 Premultiplied with A fixed at maximum."},
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3

struct module_state {
    PyObject *error;
};
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
static int nsmblib_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}
static int nsmblib_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "nsmblib",
        NULL,
        sizeof(struct module_state),
        NSMBLibMethods,
        NULL,
        nsmblib_traverse,
        nsmblib_clear,
        NULL
};
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC
PyInit_nsmblib(void)
#else
void
initnsmblib(void)
#endif
{

#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    Py_InitModule("nsmblib", NSMBLibMethods);
#endif

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}