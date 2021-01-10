import nsmblib


def test_getVersion():
    """
    Test getVersion()
    """
    assert nsmblib.getVersion() == 5
