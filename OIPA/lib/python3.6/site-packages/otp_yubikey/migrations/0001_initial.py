# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import otp_yubikey.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteYubikeyDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('public_id', models.CharField(help_text='The public identity of the YubiKey (modhex-encoded).', max_length=32, verbose_name='Public ID')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Remote YubiKey device',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ValidationService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The name of this validation service.', max_length=32)),
                ('api_id', models.IntegerField(default=1, help_text='Your API ID.', verbose_name='API ID')),
                ('api_key', models.CharField(default='', help_text='Your base64-encoded API key.', max_length=64, verbose_name='API key', blank=True)),
                ('base_url', models.URLField(default='', help_text="The base URL of the verification service. Defaults to Yubico's hosted API.", verbose_name='Base URL', blank=True)),
                ('api_version', models.CharField(default='2.0', help_text='The version of the validation api to use.', max_length=8, choices=[('1.0', '1.0'), ('1.1', '1.1'), ('2.0', '2.0')])),
                ('use_ssl', models.BooleanField(default=False, help_text='Use HTTPS API URLs by default?', verbose_name='Use SSL')),
                ('param_sl', models.CharField(default=None, help_text='The level of syncing required.', max_length=16, verbose_name='SL', blank=True)),
                ('param_timeout', models.CharField(default=None, help_text='The time to allow for syncing.', max_length=16, verbose_name='Timeout', blank=True)),
            ],
            options={
                'verbose_name': 'YubiKey validation service',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='YubikeyDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('private_id', models.CharField(default=otp_yubikey.models.default_id, help_text='The 6-byte private ID (hex-encoded).', max_length=12, verbose_name='Private ID', validators=[otp_yubikey.models.id_validator])),
                ('key', models.CharField(default=otp_yubikey.models.default_key, help_text='The 16-byte AES key shared with this YubiKey (hex-encoded).', max_length=32, validators=[otp_yubikey.models.key_validator])),
                ('session', models.PositiveIntegerField(default=0, help_text='The non-volatile session counter most recently used by this device.')),
                ('counter', models.PositiveIntegerField(default=0, help_text='The volatile session usage counter most recently used by this device.')),
                ('user', models.ForeignKey(help_text='The user that this device belongs to.', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Local YubiKey device',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='remoteyubikeydevice',
            name='service',
            field=models.ForeignKey(to='otp_yubikey.ValidationService', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='remoteyubikeydevice',
            name='user',
            field=models.ForeignKey(help_text='The user that this device belongs to.', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
