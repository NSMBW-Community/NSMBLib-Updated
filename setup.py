import os
import sys

from setuptools import setup, Extension

extra_compile_args = ['-DPy_LIMITED_API']

# Workaround for what looks like a weird Python bug?
if os.name != 'nt':
    extra_compile_args.append('-Wno-implicit-function-declaration')

setup(
  name='nsmblib',
  version='2021.10.14.0',
  ext_modules=[
    Extension(
      'nsmblib',
      sources=['nsmblibmodule.c', 'list.c'],
      extra_compile_args=extra_compile_args,
      py_limited_api=True,
    )
  ]
)
