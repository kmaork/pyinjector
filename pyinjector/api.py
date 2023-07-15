from __future__ import annotations
import os
from typing import AnyStr
from sys import platform

from .injector import Injector, InjectorException


class PyInjectorError(Exception):
    pass


class LibraryNotFoundException(PyInjectorError):
    def __init__(self, path: bytes):
        self.path = path

    def __str__(self):
        return f'Could not find library: {self.path}'


class InjectorError(PyInjectorError):
    def __init__(self, error: InjectorException):
        self.ret_val, self.error_str = error.args

    def _get_extra_explanation(self):
        return None

    def __str__(self):
        extra = self._get_extra_explanation()
        explanation = \
            'see error code definition in injector/include/injector.h' if self.error_str is None else \
                (self.error_str if extra is None else '{}\n{}'.format(self.error_str, extra))
        return 'Injector failed with {}: {}'.format(self.ret_val, explanation)


class LinuxInjectorPermissionError(InjectorError):
    def _get_extra_explanation(self):
        return """Failed attaching to process due to permission error.
This is most likely due to ptrace scope limitations applied to the kernel for security purposes.
Possible solutions:
 - Rerun as root
 - Temporarily remove ptrace scope limitations usin
`echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope`
 - Persistently remove ptrace scope limitations by editing /etc/sysctl.d/10-ptrace.conf
More details can be found here: https://stackoverflow.com/q/19215177/2907819')"""


class MacUnknownInjectorError(InjectorError):
    def _get_extra_explanation(self):
        issue_link = "https://github.com/kmaork/pyinjector/issues/26"
        return (
            """Mac restricts injection for security reasons. Please report this error in the issue:
{}""".format(issue_link)
            if os.geteuid() == 0 else
            """Mac restricts injection for security reasons. Please try rerunning as root.
If you need to inject without root permissions, please report here:
{}""".format(issue_link)
        )


def inject(pid: int, library_path: AnyStr) -> int:
    """
    Inject the shared library at library_path to the process (or thread) with the given pid.
    Return the handle to the loaded library.
    """
    if isinstance(library_path, str):
        encoded_library_path = library_path.encode()
    else:
        encoded_library_path = library_path
    assert isinstance(encoded_library_path, bytes)
    if not os.path.isfile(encoded_library_path):
        raise LibraryNotFoundException(encoded_library_path)

    exception_map = {(-8, 'linux'): LinuxInjectorPermissionError,
                     (-1, 'darwin'): MacUnknownInjectorError}
    injector = Injector()
    try:
        injector.attach(pid)
        try:
            return injector.inject(encoded_library_path)
        finally:
            injector.detach()
    except InjectorException as e:
        exception_cls = exception_map.get((e.args[0], platform), InjectorError)
        raise exception_cls(e) from e

# todo:
#   "# If defined(__APPLE__) || defined(__linux)" in pyi
#   make attach a class method that returns an injector instance? what happens if we call non attach methods first?
#   read all that garbage c code...
