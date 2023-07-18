from sys import platform
from pathlib import Path
from setuptools import setup, Extension

PROJECT_ROOT = Path(__file__).parent.resolve()
INJECTOR_DIR = PROJECT_ROOT / 'injector'
DIR_MAPPING = {
    'linux': 'linux',
    'win32': 'windows',
    'darwin': 'macos',
}
INJECTOR_SRC = INJECTOR_DIR / 'src' / DIR_MAPPING[platform]
INJECTOR_WRAPPER = PROJECT_ROOT / 'pyinjector' / 'injector.c'
SOURCES = [str(c.relative_to(PROJECT_ROOT))
           for c in [INJECTOR_WRAPPER, *INJECTOR_SRC.iterdir()]
           if c.suffix == '.c']

injector_extension = Extension(
    'pyinjector.injector',
    sources=SOURCES,
    include_dirs=[str(INJECTOR_DIR.relative_to(PROJECT_ROOT) / 'include')],
    export_symbols=['injector_attach', 'injector_inject', 'injector_detach', 'injector_error'],
    define_macros=[('EM_AARCH64', '183')]  # Needed on CentOS for some reason
)

setup(
    ext_modules=[injector_extension],
    entry_points={"console_scripts": ["inject=pyinjector.__main__:main"]}
)
