from __future__ import annotations
import os
from contextlib import contextmanager
from typing import AnyStr, Optional
from sys import platform

from .injector import Injector, InjectorException


class PyInjectorError(Exception):
    pass


class LibraryNotFoundException(PyInjectorError):
    def __init__(self, path: AnyStr):
        self.path = path

    def __str__(self):
        return f'Could not find library: {self.path}'


class InjectorError(PyInjectorError):
    def __init__(self, func_name: str, ret_val: int, error_str: Optional[str]):
        self.func_name = func_name
        self.ret_val = ret_val
        self.error_str = error_str

    def _get_extra_explanation(self):
        return None

    def __str__(self):
        extra = self._get_extra_explanation()
        explanation = \
            'see error code definition in injector/include/injector.h' if self.error_str is None else \
                (self.error_str if extra is None else f'{self.error_str}\n{extra}')
        return f'Injector failed with {self.ret_val} calling {self.func_name}: {explanation}'


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
            f"Mac restricts injection for security reasons. Please report this error in the issue:\n{issue_link}"
            if os.geteuid() == 0 else
            f"""Mac restricts injection for security reasons. Please try rerunning as root.
If you need to inject without root permissions, please report here:
{issue_link}"""
        )


@contextmanager
def attach(pid: int):
    exception_map = {(-8, 'linux'): LinuxInjectorPermissionError,
                     (-1, 'darwin'): MacUnknownInjectorError}
    injector = Injector()
    try:
        injector.attach(pid)
        try:
            yield injector
        finally:
            injector.detach()
    except InjectorException as e:
        func_name, ret_val, error_str = e.args
        exception_cls = exception_map.get((ret_val, platform), InjectorError)
        raise exception_cls(func_name, ret_val, error_str) from e


def encode_if_needed(path: AnyStr) -> bytes:
    if isinstance(path, str):
        return path.encode()
    return path


def self_relative_path(library_path: AnyStr, process_root: AnyStr):
    if not process_root:
        return library_path
    encoded_library_path = encode_if_needed(library_path)
    encoded_proc_root = encode_if_needed(process_root)
    return os.path.normpath(encoded_proc_root + b'/' + encoded_library_path)


def inject(pid: int, library_path: AnyStr, uninject: bool = False,
           process_root: AnyStr = "") -> int:
    """
    Inject the shared library at library_path to the process (or thread) with the given pid.
    If uninject is True, the library will be unloaded after injection.
    If the target process is running in container or chroot jail, library_path
    should be given as the target process will see it, process_root should
    be the path to the target process's root e.g. /proc/<pid>/root/
    Return the handle to the injected library.
    """
    if not os.path.isfile(self_relative_path(library_path, process_root)):
        raise LibraryNotFoundException(self_relative_path(library_path, process_root))
    with attach(pid) as injector:
        handle = injector.inject(encode_if_needed(library_path))
        if uninject:
            injector.uninject(handle)
        return handle
