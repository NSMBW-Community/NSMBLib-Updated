# 2020-11-13

# This is a little script that just renames the specified wheel files to
# declare support for ABI3 (Py_LIMITED_API) and the specified set of
# interpreter tags.
#
# Example usage:
# rename_wheel.py libexample-1.2.3-cp39-cp39-darwin.whl - cp37 cp38 cp39
#
# This renames libexample-1.2.3-cp39-cp39-darwin.whl in the current
# working directory to libexample-1.2.3-cp37.cp38.cp39-abi3-darwin.whl.
#
# You can specify multiple filenames and multiple platform tags -- just
# separate them with the argument "-".

import os
import sys
import typing

import packaging.tags


def split_wheel_filename(fn: str) -> typing.Tuple[str, typing.FrozenSet[packaging.tags.Tag], str]:
    """
    Split a wheel filename into the string before the platform
    compatibility tag, the tag itself (as packaging.tags.Tag), and
    the string after it.

    Example input and output:
    'libexample-1.2.3-cp36-cp36m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl'
    ('libexample-1.2.3', {Tag('cp36', 'cp36m', 'manylinux_2_17_x86_64'), Tag('cp36', 'cp36m', 'manylinux2014_x86_64')}, '.whl')
    """
    tag_start = fn.find('-', fn.find('-') + 1) + 1
    tag_end = fn.rfind('.')

    tag_set = packaging.tags.parse_tag(fn[tag_start:tag_end])
    return fn[:tag_start-1], tag_set, fn[tag_end:]


def interpreter_version_str_sorting_key(key: str) -> int:
    """
    Return a sorting key for an interpreter version string like "cp38" or
    "cp310".
    """
    if key.startswith('cp'):
        key = key[2:]
    if key.endswith('m'):  # unlikely, but just in case
        key = key[:-1]

    major = int(key[0])  # "3"
    minor = int(key[1:])  # "10"

    return (major, minor)


def make_compressed_tag(interpreter: set, abi: set, platform: set) -> str:
    """
    Create a "compressed tag set" representing the Cartesian product of
    the specified interpreters, ABIs, and platforms.
    """
    return '-'.join([
        '.'.join(sorted(interpreter, key=interpreter_version_str_sorting_key)),
        '.'.join(sorted(abi)),
        '.'.join(sorted(platform)),
    ])


def genericize_filename_for_abi3(fn: str, interpreters: set) -> str:
    """
    Assuming that a wheel with the given filename is actually ABI3,
    generate an appropriate replacement filename for it.
    """
    start, tags, end = split_wheel_filename(fn)
    platforms = set(t.platform for t in tags)
    return start + '-' + make_compressed_tag(interpreters, {'abi3'}, platforms) + end


def main():
    print('Arguments (for debugging):', sys.argv)
    print()

    if len(sys.argv) < 3:
        raise RuntimeError('Not enough arguments (%s)' % str(sys.argv))

    old_fns = sys.argv[1:sys.argv.index('-')]
    platforms = set(sys.argv[sys.argv.index('-')+1:])

    print('Filenames:', old_fns)
    print('Platforms:', platforms)
    print()

    for old_fn in old_fns:
        print('Renaming %s...' % old_fn)
        new_fn = genericize_filename_for_abi3(old_fn, platforms)
        print('...to %s' % new_fn)
        os.rename(old_fn, new_fn)

if __name__ == '__main__':
    main()
