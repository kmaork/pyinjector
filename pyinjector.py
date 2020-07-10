from importlib.util import find_spec
import sys
from dataclasses import dataclass
from ctypes import CDLL, Structure, POINTER, c_int32, byref, c_char_p

libinjector_path = find_spec('libinjector').origin
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


@dataclass
class Injector:
    injector_p: injector_pointer_t

    @classmethod
    def attach(cls, pid: int) -> 'Injector':
        injector_p = injector_pointer_t()
        assert libinjector.injector_attach(byref(injector_p), pid) == 0
        return cls(injector_p)

    def inject(self, library_path: str) -> None:
        assert libinjector.injector_inject(self.injector_p, library_path) == 0

    def detach(self) -> None:
        assert libinjector.injector_detach(self.injector_p) == 0


def inject(pid: int, library_path: str) -> None:
    injector = Injector.attach(pid)
    try:
        injector.inject(library_path)
    finally:
        injector.detach()


if __name__ == '__main__':
    pid, library_path = sys.argv[1:]
    inject(int(pid), library_path.encode())
