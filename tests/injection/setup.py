from setuptools import setup, Extension

setup(name='injection', ext_modules=[Extension('injection', sources=['injection.c'])])
