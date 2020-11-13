import os
import sys

from setuptools import setup, Extension

# Building with limited API only works on 3.x, and on non-Windows OSes
if sys.version_info[0] > 2 and os.name != 'nt':
    # Declare support for all Python versions newer than the current one
    pyver = 'cp' + str(sys.version_info[0]) + str(sys.version_info[1])

    # Bad heuristic, but good enough, I guess?
    if any('bdist' in arg for arg in sys.argv[1:]):
        sys.argv.extend(['--py-limited-api', pyver])

setup(
  name='nsmblib',
  version='2020.10.07.0',
  ext_modules=[
    Extension(
      'nsmblib',
      sources=['nsmblibmodule.c', 'list.c'],
      extra_compile_args=['-Wno-implicit-function-declaration'],
      py_limited_api=True,
    )
  ]
)
