import os
from configurations import importer

from mypy_django_plugin import main

def plugin(version):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    os.environ.setdefault("DJANGO_CONFIGURATION", "EnvConfig")
    importer.install()
    return main.plugin(version)