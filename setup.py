import os
from setuptools import setup
from distutils.core import Extension

injector_dir = './injector'
libinjector = Extension('libinjector',
                        include_dirs=[os.path.join(injector_dir, 'include')],
                        sources=[os.path.join(injector_dir, 'src', 'linux', c) for c in
                                 ('elf.c', 'injector.c', 'ptrace.c', 'remote_call.c', 'util.c')])

setup(name='pyinjector',
      py_modules=['pyinjector'],
      ext_modules=[libinjector])
