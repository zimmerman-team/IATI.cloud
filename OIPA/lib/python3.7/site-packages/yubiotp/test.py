from doctest import DocTestSuite
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

from . import crc, modhex, otp


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()

    suite.addTests(tests)
    suite.addTest(DocTestSuite(crc))
    suite.addTest(DocTestSuite(modhex))
    suite.addTest(DocTestSuite(otp))

    return suite
