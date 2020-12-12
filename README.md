# Pyinjector

[![Tests (GitHub Actions)](https://github.com/kmaork/pyinjector/workflows/Tests/badge.svg)](https://github.com/kmaork/pyinjector)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/pyinjector.svg)](https://pypi.python.org/pypi/pyinjector/)
[![PyPI version](https://badge.fury.io/py/pyinjector.svg)](https://badge.fury.io/py/pyinjector)
[![Downloads](https://pepy.tech/badge/pyinjector)](https://pepy.tech/project/pyinjector)
[![GitHub license](https://img.shields.io/github/license/kmaork/pyinjector)](https://github.com/kmaork/pyinjector/blob/master/LICENSE.txt)

A cross-platform tool/library allowing dynamic library injection into running processes.
If you are looking for a way to inject *python* code into a running process, try the [hypno](https://github.com/kmaork/hypno) library.

Pyinjector has no external python dependencies.
It is implemented as a python wrapper for [kubo/injector](https://github.com/kubo/injector).

### Installation
```shell script
pip install pyinjector
```
Both source distributions, `manylinux2010` wheels and windows wheels are uploaded to Pypi for every release.

### Usage
#### CLI
```shell script
inject <pid> <path/to/shared/library>
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
