from setuptools import setup
from distutils.extension import Extension

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
