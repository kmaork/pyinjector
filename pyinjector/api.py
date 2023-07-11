import os
from importlib.util import find_spec
from ctypes import CDLL, Structure, POINTER, c_int32, byref, c_char_p, c_void_p, pointer
from typing import AnyStr, Callable, Any, Mapping, Type, Optional, Tuple
from sys import platform

libinjector_path = find_spec('.libinjector', __package__).origin
libinjector = CDLL(libinjector_path)

injector_t = type('injector_t', (Structure,), {})
injector_pointer_t = POINTER(injector_t)
pid_t = c_int32

libinjector.injector_attach.argtypes = POINTER(injector_pointer_t), pid_t
libinjector.injector_attach.restype = c_int32
libinjector.injector_inject.argtypes = injector_pointer_t, c_char_p, POINTER(c_void_p)
libinjector.injector_inject.restype = c_int32
libinjector.injector_detach.argtypes = injector_pointer_t,
libinjector.injector_detach.restype = c_int32
libinjector.injector_error.argtypes = ()
libinjector.injector_error.restype = c_char_p


class PyInjectorError(Exception):
    pass


class LibraryNotFoundException(PyInjectorError):
    def __init__(self, path: bytes):
        self.path = path

    def __str__(self):
        return f'Could not find library: {self.path}'


class InjectorError(PyInjectorError):
    def __init__(self, func_name: str, ret_val: int, error_str: Optional[bytes]):
        self.func_name = func_name
        self.ret_val = ret_val
        self.error_str = error_str.decode()

    def _get_extra_explanation(self):
        return None

    def __str__(self):
        extra = self._get_extra_explanation()
        explanation = \
            'see error code definition in injector/include/injector.h' if self.error_str is None else \
                (self.error_str if extra is None else '{}\n{}'.format(self.error_str, extra))
        return '{} returned {}: {}'.format(self.func_name, self.ret_val, explanation)


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


def call_c_func(func: Callable[..., int], *args: Any,
                exception_map: Mapping[Tuple[int, str], Type[InjectorError]] = None) -> None:
    ret = func(*args)
    if ret != 0:
        exception_map = {} if exception_map is None else exception_map
        exception_cls = exception_map.get((ret, platform), InjectorError)
        raise exception_cls(func.__name__, ret, libinjector.injector_error())


class Injector:
    def __init__(self, injector_p: injector_pointer_t):
        self.injector_p = injector_p

    @classmethod
    def attach(cls, pid: int) -> 'Injector':
        assert isinstance(pid, int)
        injector_p = injector_pointer_t()
        call_c_func(libinjector.injector_attach, byref(injector_p), pid,
                    exception_map={(-8, 'linux'): LinuxInjectorPermissionError,
                                   (-1, 'darwin'): MacUnknownInjectorError})
        return cls(injector_p)

    def inject(self, library_path: AnyStr) -> int:
        if isinstance(library_path, str):
            library_path = library_path.encode()
        assert isinstance(library_path, bytes)
        assert os.path.isfile(library_path), f'Library not found at "{library_path.decode()}"'
        handle = c_void_p()
        call_c_func(libinjector.injector_inject, self.injector_p, library_path, pointer(handle))
        return handle.value

    def detach(self) -> None:
        call_c_func(libinjector.injector_detach, self.injector_p)


def inject(pid: int, library_path: AnyStr) -> int:
    """
    Inject the shared library at library_path to the process (or thread) with the given pid.
    Return the handle to the loaded library.
    """
    if not os.path.isfile(library_path):
        raise LibraryNotFoundException(library_path)
    injector = Injector.attach(pid)
    try:
        return injector.inject(library_path)
    finally:
        injector.detach()
