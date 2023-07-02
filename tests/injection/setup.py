from setuptools import setup, Extension

setup(name='pyinjector_tests_injection', ext_modules=[Extension('pyinjector_tests_injection', sources=['injection.c'])])
