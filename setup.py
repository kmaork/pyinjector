from pathlib import Path
from setuptools import setup
from distutils.core import Extension

PROJECT_ROOT = Path(__file__).parent
INJECTOR_DIR = PROJECT_ROOT / 'injector'

libinjector = Extension('libinjector',
                        include_dirs=[str(INJECTOR_DIR / 'include')],
                        sources=[str(INJECTOR_DIR / 'src' / 'linux' / c) for c in
                                 ('elf.c', 'injector.c', 'ptrace.c', 'remote_call.c', 'util.c')])

setup(
    ext_modules=[libinjector],
    entry_points={"console_scripts": ["inject=pyinjector:main"]},
)
