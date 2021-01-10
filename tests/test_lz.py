import nsmblib


TEST_PLAINTEXT = b'In signal processing, data compression, source coding,[1] or bit-rate reduction is the process of encoding information using fewer bits than the original representation.[2] Any particular compression is either lossy or lossless. Lossless compression reduces bits by identifying and eliminating statistical redundancy. No information is lost in lossless compression. Lossy compression reduces bits by removing unnecessary or less important information.[3] Typically, a device that performs data compression is referred to as an encoder, and one that performs the reversal of the process (decompression) as a decoder.'
TEST_COMPRESSED = b'\x11g\x02\x00\x00In signa\x00l proces\x00sing, da\x00ta compr\x800\x11on, sou\x14rce \x13d0 [1\x00] or bit\x00-rate re\x08duct ( is\x08 thepL of\x10 enP4 inf\norma@&u0g \x0cfewe@E04an\x82@9origi0\x8frDe0}ent@1.[\x002] Any p\x00articuladr\xb0\xa00wei ?r \x06lossy0\x9d0\x08l\x8e \x1e. L`\t\xc01@\xb3eAsP~by id k\x10ify0\x98and \nelim \x88t0\x0fs\xb00\x84s w@\x97dund\x00ancy. No\xef\xc0\xd5 \x84 tt \x13\x80|\xb0rP\x88Ay\x00\xc0\x85remov0r\tunne1BarP\xcc\x800Kimporta`n0a\x80u.[3] \x10Typ0\x9cly, \x03a devi!\xab!R\x05t per0)s\x00\x01\xd2\x820\xacrefer \x81 \x06to as \xf5Q\xacefr E!\x01on\xf0D1\xa0r\x07evers!\x08!\xdb\xb1\xea\x17(de\xa0^)@P \x8a@O\x00.'


def test_for_broken_compression():
    """
    The old broken compression algorithm fails this test
    """
    VECTOR = b'\0\1\0\0\0\0\0\0\0\1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
    assert nsmblib.decompress11LZS(nsmblib.compress11LZS(VECTOR)) == VECTOR


def test_decompress11LZS():
    """
    Basic decompression test
    """
    assert nsmblib.decompress11LZS(TEST_COMPRESSED) == TEST_PLAINTEXT


def test_compress11LZS():
    """
    Basic compression test
    """
    assert nsmblib.compress11LZS(TEST_PLAINTEXT) == TEST_COMPRESSED
