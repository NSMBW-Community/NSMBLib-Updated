import os
import sys

from setuptools import setup, Extension

# # Building with limited API only works on 3.x, and on non-Windows OSes
# if sys.version_info[0] > 2:
#     # Declare support for all Python versions newer than the current one
#     pyver = 'cp35'# + str(sys.version_info[0]) + str(sys.version_info[1])

#     # Bad heuristic, but good enough, I guess?
#     if any('bdist' in arg for arg in sys.argv[1:]):
#         sys.argv.extend(['--py-limited-api', pyver])

# Workaround for what looks like a weird Python bug?
if os.name == 'nt':
    extra_compile_args = []
else:
    extra_compile_args = ['-Wno-implicit-function-declaration']
extra_compile_args += ['-DPy_LIMITED_ABI', '-DPy_LIMITED_API']

setup(
  name='nsmblib',
  version='2020.10.07.0',
  ext_modules=[
    Extension(
      'nsmblib',
      sources=['nsmblibmodule.c', 'list.c'],
      extra_compile_args=extra_compile_args,
      # py_limited_api=True,
    )
  ]
)
