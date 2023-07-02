from .api import inject, LibraryNotFoundException, InjectorError

from types import ModuleType


def legacy_pyinjector_import():
    # A truly disgusting hack to cover for an import mistake in hypno<1.0.1
    from sys import modules
    pyinjector = ModuleType('pyinjector.pyinjector')
    pyinjector.__package__ = "pyinjector"
    pyinjector.InjectorError = InjectorError
    modules[pyinjector.__name__] = pyinjector


legacy_pyinjector_import()
