from sys import platform
from pathlib import Path
from setuptools import setup, Extension
from distutils.extension import Extension

PROJECT_ROOT = Path(__file__).parent.resolve()
LIBINJECTOR_DIR = PROJECT_ROOT / 'injector'
LIBINJECTOR_SRC = LIBINJECTOR_DIR / 'src' / ('windows' if platform == 'win32' else 'linux')
LIBINJECTOR_WRAPPER = PROJECT_ROOT / 'libinjector.c'

libinjector = Extension('pyinjector.libinjector',
                        sources=[str(c.relative_to(PROJECT_ROOT))
                                 for c in [LIBINJECTOR_WRAPPER, *LIBINJECTOR_SRC.iterdir()]
                                 if c.suffix == '.c'],
                        include_dirs=[str(LIBINJECTOR_DIR.relative_to(PROJECT_ROOT) / 'include')],
                        export_symbols=['injector_attach', 'injector_inject', 'injector_detach'],
                        define_macros=[('EM_AARCH64', '183')])  # Needed on CentOS for some reason

setup(
    ext_modules=[libinjector],
    entry_points={"console_scripts": ["inject=pyinjector.__main__:main"]}
)
