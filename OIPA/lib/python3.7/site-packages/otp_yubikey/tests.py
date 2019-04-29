from __future__ import absolute_import, division, print_function, unicode_literals

from binascii import unhexlify

from django.db import IntegrityError

from django_otp.tests import TestCase
from yubiotp.otp import encode_otp, YubiKey


class YubikeyTest(TestCase):
    # YubiKey device simulators.
    alice_key = YubiKey(unhexlify(b'5dc30490956b'), 6, 0)
    bob_key = YubiKey(unhexlify(b'326f70826d31'), 11, 0)

    def setUp(self):
        try:
            alice = self.create_user('alice', 'password')
            bob = self.create_user('bob', 'password')
        except IntegrityError:
            self.skipTest("Unable to create the test user")
        else:
            self.alice_device = alice.yubikeydevice_set.create(
                private_id='5dc30490956b',
                key='fb362a0853be5e5306d5cc2483f279cb', session=5, counter=0)
            self.alice_public = self.alice_device.public_id()

            self.bob_device = bob.yubikeydevice_set.create(
                private_id='326f70826d31',
                key='11080a0e7a56d0a1546f327f20626308', session=10, counter=3)
            self.bob_public = self.bob_device.public_id()

    def test_verify_alice(self):
        _, token = self.alice_token()
        ok = self.alice_device.verify_token(token)

        self.assertTrue(ok)

    def test_verify_unicode(self):
        _, token = self.alice_token()
        ok = self.alice_device.verify_token(token.decode('ascii'))

        self.assertTrue(ok)

    def test_counter_increment(self):
        otp, token = self.alice_token(5, 7)
        ok = self.alice_device.verify_token(token)

        self.assertTrue(ok)
        self.assertEqual(self.alice_device.session, 5)
        self.assertEqual(self.alice_device.counter, 7)

    def test_no_verify_mismatch(self):
        _, token = self.alice_token()
        ok = self.bob_device.verify_token(token)

        self.assertTrue(not ok)

    def test_replay(self):
        otp, token = self.alice_token()
        ok1 = self.alice_device.verify_token(token)
        ok2 = self.alice_device.verify_token(token)

        self.assertTrue(ok1)
        self.assertTrue(not ok2)
        self.assertEqual(self.alice_device.session, otp.session)
        self.assertEqual(self.alice_device.counter, otp.counter)

    def test_bad_public_id(self):
        self.alice_public = self.bob_public
        otp, token = self.alice_token()
        ok = self.alice_device.verify_token(token)

        self.assertTrue(not ok)

    def test_bad_private_id(self):
        alice_key = YubiKey(unhexlify(b'2627dc624cbd'), 6, 0)
        otp = alice_key.generate()
        token = encode_otp(otp, self.alice_aes, self.alice_public)
        ok = self.alice_device.verify_token(token)

        self.assertTrue(not ok)

    def test_session_replay(self):
        otp, token = self.alice_token(4, 0)
        ok = self.alice_device.verify_token(token)

        self.assertTrue(not ok)

    def test_counter_replay(self):
        otp, token = self.alice_token(5, 0)
        ok = self.alice_device.verify_token(token)

        self.assertTrue(not ok)

    def test_bad_decrypt(self):
        otp = self.alice_key.generate()
        token = encode_otp(otp, self.bob_aes, self.alice_public)
        ok = self.alice_device.verify_token(token)

        self.assertTrue(not ok)

    def test_bogus_token(self):
        ok = self.alice_device.verify_token('completelybogus')

        self.assertTrue(not ok)

    def alice_token(self, session=None, counter=None):
        otp = self.alice_key.generate()

        if session is not None:
            otp.session = session

        if counter is not None:
            otp.counter = counter

        return otp, encode_otp(otp, self.alice_aes, self.alice_public)

    @property
    def alice_aes(self):
        return self.alice_device.bin_key

    @property
    def bob_aes(self):
        return self.bob_device.bin_key
