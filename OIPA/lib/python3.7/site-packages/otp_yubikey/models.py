from __future__ import absolute_import, division, print_function, unicode_literals

from base64 import b64decode
from binascii import hexlify, unhexlify
from struct import pack

from django.db import models
from django.utils import six
from django.utils.encoding import force_text

from django_otp.models import Device
from django_otp.util import hex_validator, random_hex
from yubiotp.client import YubiClient10, YubiClient11, YubiClient20
from yubiotp.modhex import modhex
from yubiotp.otp import decode_otp


def default_id():
    return force_text(random_hex(6))


def id_validator(value):
    return hex_validator(6)(value)


def default_key():
    return force_text(random_hex(16))


def key_validator(value):
    return hex_validator(16)(value)


class YubikeyDevice(Device):
    """
    Represents a locally-verified YubiKey OTP
    :class:`~django_otp.models.Device`.

    .. attribute:: private_id

        *CharField*: The 6-byte private ID (hex-encoded).

    .. attribute:: key

        *CharField*: The 16-byte AES key shared with this YubiKey
        (hex-encoded).

    .. attribute:: session

        *PositiveIntegerField*: The non-volatile session counter most recently
        used by this device.

    .. attribute:: counter

        *PositiveIntegerField*: The volatile session usage counter most
        recently used by this device.
    """
    private_id = models.CharField(
        max_length=12,
        validators=[id_validator],
        default=default_id,
        verbose_name="Private ID",
        help_text="The 6-byte private ID (hex-encoded)."
    )

    key = models.CharField(
        max_length=32,
        validators=[key_validator],
        default=default_key,
        help_text="The 16-byte AES key shared with this YubiKey (hex-encoded)."
    )

    session = models.PositiveIntegerField(
        default=0,
        help_text="The non-volatile session counter most recently used by this device."
    )

    counter = models.PositiveIntegerField(
        default=0,
        help_text="The volatile session usage counter most recently used by this device."
    )

    class Meta(Device.Meta):
        verbose_name = "Local YubiKey device"

    def public_id(self):
        """
        The public ID of this device is the four-byte, big-endian,
        modhex-encoded primary key.
        """
        return modhex(pack('>I', self.id))
    public_id.short_description = 'Public Identity'
    public_id.admin_order_field = 'id'

    @property
    def bin_key(self):
        return unhexlify(self.key.encode())

    def verify_token(self, token):
        if isinstance(token, six.text_type):
            token = token.encode('utf-8')

        try:
            public_id, otp = decode_otp(token, self.bin_key)
        except Exception:
            return False

        if public_id != self.public_id():
            return False

        if hexlify(otp.uid) != self.private_id.encode():
            return False

        if otp.session < self.session:
            return False

        if (otp.session == self.session) and (otp.counter <= self.counter):
            return False

        # All tests pass. Update the counters and return the good news.
        self.session = otp.session
        self.counter = otp.counter
        self.save()

        return True


class ValidationService(models.Model):
    """
    Represents a YubiKey validation web service. By default, this will point to
    Yubico's official hosted service, which you can customize. You can also
    create instances to point at any other service implementing the same
    protocol.

    .. attribute:: name

        *CharField*: The name of this validation service.

    .. attribute:: api_id

        *IntegerField*: Your API ID. The server needs this to sign responsees.
        (Default: 1)

    .. attribute:: api_key

        *CharField*: Your base64-encoded API key, used to sign requests. This
        is optional but strongly recommended. (Default: ``''``)

    .. attribute:: base_url

        *URLField*: The base URL of the verification service. Defaults to
        Yubico's hosted API.

    .. attribute:: api_version

        *CharField*: The version of the validation API to use: '1.0', '1.1', or
        '2.0'. (Default: '2.0')

    .. attribute:: use_ssl

        *BooleanField*: If ``True``, we'll use the HTTPS versions of the
        default URLs. Because :mod:`urllib2` does not verify certificates, this
        provides little benefit. (Default: ``False``).

    .. attribute:: param_sl

        *CharField*: The level of syncing required. See
        :class:`~yubiotp.client.YubiClient20`.

    .. attribute:: param_timeout

        *CharField*: The time to allow for syncing. See
        :class:`~yubiotp.client.YubiClient20`.
    """
    API_VERSIONS = ['1.0', '1.1', '2.0']

    name = models.CharField(
        max_length=32,
        help_text="The name of this validation service."
    )

    api_id = models.IntegerField(
        default=1,
        verbose_name="API ID",
        help_text="Your API ID."
    )

    api_key = models.CharField(
        max_length=64,
        blank=True,
        default='',
        verbose_name="API key",
        help_text="Your base64-encoded API key."
    )

    base_url = models.URLField(
        blank=True,
        default='',
        verbose_name="Base URL",
        help_text="The base URL of the verification service. Defaults to Yubico's hosted API."
    )

    api_version = models.CharField(
        max_length=8,
        choices=list(zip(API_VERSIONS, API_VERSIONS)),
        default='2.0',
        help_text="The version of the validation api to use."
    )

    use_ssl = models.BooleanField(
        default=False,
        verbose_name="Use SSL",
        help_text="Use HTTPS API URLs by default?"
    )

    param_sl = models.CharField(
        max_length=16,
        blank=True,
        default=None,
        verbose_name="SL",
        help_text="The level of syncing required."
    )

    param_timeout = models.CharField(
        max_length=16,
        blank=True,
        default=None,
        verbose_name="Timeout",
        help_text="The time to allow for syncing."
    )

    class Meta(object):
        verbose_name = "YubiKey validation service"

    def __unicode__(self):
        return self.name

    def get_client(self):
        api_key = b64decode(self.api_key.encode()) or None

        if self.api_version == '2.0':
            client = YubiClient20(self.api_id, api_key, self.use_ssl, False, self.param_sl or None, self.param_timeout or None)
        elif self.api_version == '1.1':
            client = YubiClient11(self.api_id, api_key, self.use_ssl)
        else:
            client = YubiClient10(self.api_id, api_key, self.use_ssl)

        if self.base_url:
            client.base_url = self.base_url

        return client


class RemoteYubikeyDevice(Device):
    """
    Represents a YubiKey device that is to be verified with a remote validation
    service. In order create these devices, you must have at least one
    :class:`~otp_yubikey.models.ValidationService` in the database.

    .. attribute:: service

        *ForeignKey*: The validation service to use for this device.

    .. attribute:: public_id

        *CharField*: The public identity of the YubiKey (modhex-encoded).
    """
    service = models.ForeignKey(ValidationService, on_delete=models.CASCADE)
    public_id = models.CharField(max_length=32, verbose_name="Public ID", help_text="The public identity of the YubiKey (modhex-encoded).")

    class Meta(Device.Meta):
        verbose_name = "Remote YubiKey device"

    def verify_token(self, token):
        verified = False

        if token[:-32] == self.public_id:
            client = self.service.get_client()
            response = client.verify(token)
            verified = response.is_ok()

        return verified
