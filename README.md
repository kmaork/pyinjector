# Pyinjector

[![PyPI version](https://badge.fury.io/py/pyinjector.svg)](https://badge.fury.io/py/pyinjector)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/pyinjector.svg)](https://pypi.python.org/pypi/pyinjector/)
[![GitHub license](https://img.shields.io/github/license/kmaork/pyinjector)](https://github.com/kmaork/pyinjector/blob/master/LICENSE.txt)
[![Tests (GitHub Actions)](https://github.com/kmaork/pyinjector/workflows/Tests/badge.svg)](https://github.com/kmaork/pyinjector)

A tool/library allowing dynamic library injection into running processes.
Has no external python dependencies.
Implemented as a python wrapper for [kubo/injector](https://github.com/kubo/injector).

### Installation
```shell script
pip install pyinjector
```
Both source distributions and `manylinux2010` wheels are upoloaded to pypi for every release.

### Usage
#### CLI
```shell script
inject <pid> <path to .so file>
```

#### API
```python
from pyinjector import inject

inject(pid, path_to_so_file)
```

### How it works
We build [kubo/injector](https://github.com/kubo/injector) as a C-extension and use its interface using `ctypes`.
[kubo/injector](https://github.com/kubo/injector) is an awesome repo allowing to inject shared libraries into running
processes both on windows (`CreateRemoteThread`+`LoadLibrary`) and on linux (`ptrace`).