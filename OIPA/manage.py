#!/usr/bin/env python
import os
import sys

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

if __name__ == "__main__":
    current_settings = os.getenv("DJANGO_SETTINGS_MODULE", None)

    if not current_settings:
        raise Exception(
            "Please configure your .env file along-side manage.py file and "
            "set 'DJANGO_SETTINGS_MODULE=OIPA.settings_file' variable there!"
        )

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", current_settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
