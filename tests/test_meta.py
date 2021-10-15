import nsmblib


def test_getVersion():
    """
    Test getVersion()
    """
    assert nsmblib.getVersion() == 5


def test_getUpdatedVersion():
    """
    Test getUpdatedVersion()
    """
    assert 2021000000 < nsmblib.getUpdatedVersion() < 3000000000
