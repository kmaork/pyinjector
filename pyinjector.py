from argparse import ArgumentParser, Namespace
from importlib.util import find_spec
from dataclasses import dataclass
from ctypes import CDLL, Structure, POINTER, c_int32, byref, c_char_p
from typing import List, Optional, AnyStr, Callable, Any

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


def call_c_func(func: Callable[..., int], *args: Any) -> None:
    ret = func(*args)
    assert ret == 0, f'{func.__name__} returned {ret}'


@dataclass
class Injector:
    injector_p: injector_pointer_t

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


def parse_args(args: Optional[List[str]]) -> Namespace:
    parser = ArgumentParser(description='Inject a dynamic library to a running process.')
    parser.add_argument('pid', type=int, help='pid of the process to inject the library into')
    parser.add_argument('library_path', type=str.encode, help='path of the library to inject')
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> None:
    parsed_args = parse_args(args)
    inject(parsed_args.pid, parsed_args.library_path)


if __name__ == '__main__':
    main()
