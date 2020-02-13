import sys

from setuptools import setup
from distutils.extension import Extension

if sys.version_info[0] > 2:
    pyver = 'cp' + str(sys.version_info[0]) + str(sys.version_info[1])
    sys.argv.extend(['--py-limited-api', pyver])

setup(
  name='nsmblib',
  version='0.4.1',
  ext_modules=[
    Extension(
      'nsmblib',
      ['nsmblibmodule.c', 'list.c'],
    )
  ]
)
