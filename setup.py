import os
import sys

from setuptools import setup, Extension

# Building with limited API only works on 3.x, and on non-Windows OSes
if sys.version_info[0] > 2 and os.name != 'nt':
    # Declare support for all Python versions newer than the current one
    pyver = 'cp' + str(sys.version_info[0]) + str(sys.version_info[1])
    sys.argv.extend(['--py-limited-api', pyver])

setup(
  name='nsmblib',
  version='2020.05.17.0',
  ext_modules=[
    Extension(
      'nsmblib',
      sources=['nsmblibmodule.c', 'list.c'],
      py_limited_api=True,
    )
  ]
)
