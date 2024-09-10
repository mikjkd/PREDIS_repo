from injector import singleton

from backend.core.core import PREDISCore


def configure(binder):
    binder.bind(PREDISCore, to=PREDISCore(), scope=singleton)
