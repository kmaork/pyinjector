import sys
import time
from subprocess import Popen, PIPE
from importlib.util import find_spec
from pyinjector import inject

INJECTION_LIB_PATH = find_spec('injection').origin
STRING_PRINTED_FROM_LIB = b'Hello, world!'
TIME_TO_WIT_FOR_PROCESS_TO_INIT = 0.1


def test_inject():
    with Popen([sys.executable, '-c', 'while True: pass'], stdout=PIPE) as process:
        try:
            time.sleep(TIME_TO_WIT_FOR_PROCESS_TO_INIT)
            inject(process.pid, INJECTION_LIB_PATH)
            assert process.stdout.read() == STRING_PRINTED_FROM_LIB
        finally:
            process.kill()
