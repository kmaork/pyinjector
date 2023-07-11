from os import environ
from subprocess import check_call
from sys import platform
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.develop import develop
from setuptools.command.install import install


PROJECT_ROOT = Path(__file__).parent.resolve()
LIBINJECTOR_DIR = PROJECT_ROOT / 'injector'
DIR_MAPPING = {
    'linux': 'linux',
    'win32': 'windows',
    'darwin': 'macos',
}
LIBINJECTOR_SRC = LIBINJECTOR_DIR / 'src' / DIR_MAPPING[platform]
LIBINJECTOR_WRAPPER = PROJECT_ROOT / 'libinjector.c'
SOURCES = [str(c.relative_to(PROJECT_ROOT))
           for c in [LIBINJECTOR_WRAPPER, *LIBINJECTOR_SRC.iterdir()]
           if c.suffix == '.c']

libinjector = Extension('pyinjector.libinjector',
                        sources=SOURCES,
                        include_dirs=[str(LIBINJECTOR_DIR.relative_to(PROJECT_ROOT) / 'include')],
                        export_symbols=['injector_attach', 'injector_inject', 'injector_detach', 'injector_error'],
                        define_macros=[('EM_AARCH64', '183')])  # Needed on CentOS for some reason


def build_executable():
    env = environ.copy()
    # https://developer.apple.com/forums/thread/694062#replyname-719723022
    env["PATH"] = f"/usr/bin:{env['PATH']}"
    check_call(["make"], cwd='injector', env=env)
    check_call(["bash", "genkey.sh"], cwd='injector/cmd/macos-sign')
    check_call(["bash", "sign.sh"], cwd='injector/cmd/macos-sign')


class DevelopAndBuildExecutable(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        build_executable()


class InstallAndBuildExecutable(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        build_executable()


setup(
    ext_modules=[libinjector],
    entry_points={"console_scripts": ["inject=pyinjector.__main__:main"]},
    cmdclass={
        'develop': DevelopAndBuildExecutable,
        'install': InstallAndBuildExecutable,
    } if platform == "darwin" else {},
)
