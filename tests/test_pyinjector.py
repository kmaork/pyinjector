import sys
import time
from subprocess import Popen, PIPE
from importlib.util import find_spec

from pyinjector import inject, LibraryNotFoundException, InjectorError
from pytest import raises, mark, xfail

INJECTION_LIB_SPEC = find_spec('pyinjector_tests_injection')
assert INJECTION_LIB_SPEC is not None, 'Could not find pyinjector_tests_injection'
origin = INJECTION_LIB_SPEC.origin
assert isinstance(origin, str), 'Could not find pyinjector_tests_injection'
# mypy is weird
INJECTION_LIB_PATH = origin
STRING_PRINTED_FROM_LIB = b'Let it be green\n'
TIME_TO_WAIT_FOR_PROCESS_TO_INIT = 1
TIME_TO_WAIT_FOR_INJECTION_TO_RUN = 1


@mark.parametrize('uninject', [True, False])
def test_inject(uninject: bool):
    if uninject and sys.platform == 'linux' and 'musl' in open('/proc/self/maps').read():
        xfail("Can't uninject on musl")
    # In new virtualenv versions on Windows, python.exe invokes the original python.exe as a subprocess, so the
    # injection does not affect the target python process.
    python = getattr(sys, '_base_executable', sys.executable)
    with Popen([python, '-c', 'while True: pass'], stdout=PIPE) as process:
        assert process.stdout is not None
        try:
            time.sleep(TIME_TO_WAIT_FOR_PROCESS_TO_INIT)
            handle1 = inject(process.pid, INJECTION_LIB_PATH, uninject=uninject)
            handle2 = inject(process.pid, INJECTION_LIB_PATH, uninject=uninject)
            time.sleep(TIME_TO_WAIT_FOR_INJECTION_TO_RUN)
            assert process.stdout.read(len(STRING_PRINTED_FROM_LIB)) == STRING_PRINTED_FROM_LIB
            if uninject:
                assert process.stdout.read(len(STRING_PRINTED_FROM_LIB)) == STRING_PRINTED_FROM_LIB
        finally:
            process.kill()
            assert process.stdout.read() == b''
    assert isinstance(handle1, int)
    assert isinstance(handle2, int)


def test_inject_no_such_lib():
    with raises(LibraryNotFoundException):
        inject(-1, 'nosuchpath.so')


def test_inject_no_such_pid():
    with raises(InjectorError) as excinfo:
        inject(-1, INJECTION_LIB_PATH)
    assert excinfo.value.ret_val == -3


@mark.skipif(sys.platform != 'linux', reason='safe injection (cloned thread) is Linux x86-64 only')
def test_inject_safe():
    python = getattr(sys, '_base_executable', sys.executable)
    with Popen([python, '-c', 'while True: pass'], stdout=PIPE) as process:
        assert process.stdout is not None
        try:
            time.sleep(TIME_TO_WAIT_FOR_PROCESS_TO_INIT)
            handle = inject(process.pid, INJECTION_LIB_PATH, safe=True)
            time.sleep(TIME_TO_WAIT_FOR_INJECTION_TO_RUN)
            assert process.stdout.read(len(STRING_PRINTED_FROM_LIB)) == STRING_PRINTED_FROM_LIB
        finally:
            process.kill()
    assert isinstance(handle, int)


@mark.skipif(sys.platform != 'linux', reason='remote-call test injects a Linux .so and calls into it')
def test_remote_call():
    from pyinjector.injector import Injector
    python = getattr(sys, '_base_executable', sys.executable)
    lib_path = INJECTION_LIB_PATH.encode() if isinstance(INJECTION_LIB_PATH, str) else INJECTION_LIB_PATH
    with Popen([python, '-c', 'while True: pass']) as process:
        try:
            time.sleep(TIME_TO_WAIT_FOR_PROCESS_TO_INIT)
            injector = Injector()
            injector.attach(process.pid)
            try:
                # Inject our test library, then resolve and call a function it exports.
                handle = injector.inject(lib_path)
                addr = injector.remote_func_addr(handle, 'pyinjector_tests_injection_answer')
                assert isinstance(addr, int) and addr != 0
                assert injector.remote_call(addr) == 42
            finally:
                injector.detach()
        finally:
            process.kill()
