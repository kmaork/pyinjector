from importlib.util import find_spec
from ctypes import CDLL, Structure, POINTER, c_int32, byref, c_char_p
from typing import AnyStr, Callable, Any

libinjector_path = find_spec('.libinjector', __package__).origin
libinjector = CDLL(libinjector_path)

injector_t = type('injector_t', (Structure,), {})
injector_pointer_t = POINTER(injector_t)
pid_t = c_int32

libinjector.injector_attach.argtypes = POINTER(injector_pointer_t), pid_t
libinjector.injector_attach.restype = c_int32
libinjector.injector_inject.argtypes = injector_pointer_t, c_char_p
libinjector.injector_inject.restype = c_int32
libinjector.injector_detach.argtypes = injector_pointer_t,
libinjector.injector_detach.restype = c_int32


def call_c_func(func: Callable[..., int], *args: Any) -> None:
    ret = func(*args)
    assert ret == 0, '{} returned {}'.format(func.__name__, ret)  # Gotta support dem old pythons!


class Injector:
    def __init__(self, injector_p: injector_pointer_t):
        self.injector_p = injector_p

    @classmethod
    def attach(cls, pid: int) -> 'Injector':
        assert isinstance(pid, int)
        injector_p = injector_pointer_t()
        call_c_func(libinjector.injector_attach, byref(injector_p), pid)
        return cls(injector_p)

    def inject(self, library_path: AnyStr) -> None:
        if isinstance(library_path, str):
            library_path = library_path.encode()
        assert isinstance(library_path, bytes)
        call_c_func(libinjector.injector_inject, self.injector_p, library_path)

    def detach(self) -> None:
        call_c_func(libinjector.injector_detach, self.injector_p)


def inject(pid: int, library_path: AnyStr) -> None:
    injector = Injector.attach(pid)
    try:
        injector.inject(library_path)
    finally:
        injector.detach()

