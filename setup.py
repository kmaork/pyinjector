from pathlib import Path
from setuptools import setup, Extension

PROJECT_ROOT = Path(__file__).parent.resolve()
LIBINJECTOR_DIR = PROJECT_ROOT / 'injector'
LIBINJECTOR_SRC = LIBINJECTOR_DIR / 'src' / 'linux'

libinjector = Extension('libinjector',
                        sources=[str(c.relative_to(PROJECT_ROOT)) for c in LIBINJECTOR_SRC.iterdir()
                                 if c.suffix == '.c'],
                        include_dirs=[str(LIBINJECTOR_DIR.relative_to(PROJECT_ROOT) / 'include')])

setup(
    ext_modules=[libinjector],
    entry_points={"console_scripts": ["inject=pyinjector:main"]}
)
