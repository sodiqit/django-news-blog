from configurations import importer

from mypy_django_plugin import main

def plugin(version):
    importer.install()
    return main.plugin(version)