import sys

from setuptools import setup
from distutils.extension import Extension

sys.argv.extend(['--py-limited-api', 'cp32'])

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
