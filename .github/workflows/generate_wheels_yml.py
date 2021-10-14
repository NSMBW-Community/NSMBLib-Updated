# Script for auto-generating wheels.yml.

# Note: we build with the *oldest* available Python version, not the
# latest, because "The Stable ABI is not generally forward-compatible:
# an extension built and tested with CPython 3.10 will not generally be
# compatible with CPython 3.9." -- PEP 652

# Specifically, we build with the oldest Python version available in the
# manylinux container (since doing otherwise would be a logistical
# nightmare), but still test with older 3.x versions because in practice
# they generally *are* forward-compatible for relatively simple
# extension modules.

PLATFORMS = ['windows', 'macos', 'ubuntu']
CPYTHON_2_TEST_VERSIONS = [(2,7)]
CPYTHON_3_TEST_VERSIONS = [(3,5), (3,6), (3,7), (3,8), (3,9), (3,10)]
CPYTHON_TEST_VERSIONS = CPYTHON_2_TEST_VERSIONS + CPYTHON_3_TEST_VERSIONS
CPYTHON_2_BUILD_VERSION = CPYTHON_2_TEST_VERSIONS[0]
CPYTHON_3_BUILD_VERSION = (3,6)
MANYLINUX_CONTAINER = 'quay.io/pypa/manylinux2014_x86_64'


def strings_for(platform: str, pyver: tuple) -> (str, str, str):
    """
    Given a (major, minor) tuple (e.g. (3,7)), return three strings:
    - '3.7'
    - '37'
    - the appropriate command for calling that Python on the specified platform
    """
    pyver_str_dot = '.'.join(str(x) for x in pyver)
    pyver_str_none = ''.join(str(x) for x in pyver)

    if platform == 'ubuntu':
        # Use the Python installations provided by the manylinux container.
        # <3.8 have to be in the form "cpXY-cpXYm"; >=3.8 have to be in the form "cpXY-cpXY"
        if pyver >= (3,8):
            py_cmd = f'/opt/python/cp{pyver_str_none}-cp{pyver_str_none}/bin/python'
        elif pyver >= CPYTHON_3_BUILD_VERSION:
            py_cmd = f'/opt/python/cp{pyver_str_none}-cp{pyver_str_none}m/bin/python'
        else:
            py_cmd = 'python'
    else:
        py_cmd = 'python'

    return pyver_str_dot, pyver_str_none, py_cmd


def make_sdist_job(pyver: tuple) -> str:
    """
    Make a job that runs `setup.py sdist`
    """
    pyver_str_dot, pyver_str_none, _ = strings_for('ubuntu', pyver)
    # Ignore strings_for()'s py_cmd, since it gives us the one for the
    # manylinux container but we're just in a regular Ubuntu VM for this job
    py_cmd = 'python'

    return f"""
  sdist:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python {pyver_str_dot}
      uses: actions/setup-python@v2
      with:
        python-version: "{pyver_str_dot}"
    - name: Install dependencies
      run: |
        {py_cmd} -m pip install --upgrade pip
        {py_cmd} -m pip install --upgrade setuptools
    - name: Build
      shell: bash
      run: |
        {py_cmd} setup.py sdist
    - name: Upload artifacts
      uses: actions/upload-artifact@v1
      with:
        name: sdist
        path: dist
    """


def make_build_job(platform: str, arch: int, pyver: tuple) -> str:
    """
    Make a build job for the specified platform and Python version
    """
    pyver_str_dot, pyver_str_none, py_cmd = strings_for(platform, pyver)

    def only_on(platform_2, text, additional_condition=True):
        return text if (platform == platform_2 and additional_condition) else ''

    def only_on_not(platform_2, text, additional_condition=True):
        return text if (platform != platform_2 and additional_condition) else ''

    if pyver < (3,0) and platform == 'ubuntu':
        return f"""
  build-ubuntu-{arch}-27:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python 2.7
      uses: actions/setup-python@v2
      with:
        python-version: 2.7
        architecture: {'x64' if arch == 64 else 'x86'}
    - name: Install dependencies
      run: |
        {py_cmd} -m pip install --upgrade pip
        {py_cmd} -m pip install --upgrade setuptools wheel
    - name: Build
      run: |
        {py_cmd} setup.py bdist_wheel
    - name: Upload artifacts
      uses: actions/upload-artifact@v1
      with:
        name: build-ubuntu-{arch}-27
        path: dist
        """

    elif pyver < (3,0):
        return f"""
  build-{platform}-{arch}-27:
    runs-on: {platform}-latest
    steps:
    - uses: actions/checkout@v2
    - uses: ilammy/msvc-dev-cmd@v1
    - name: Set up Python 2.7
      uses: actions/setup-python@v2
      with:
        python-version: 2.7
        architecture: {'x64' if arch == 64 else 'x86'}
    - name: Install dependencies
      run: |
        {py_cmd} -m pip install --upgrade pip
        {py_cmd} -m pip install --upgrade setuptools wheel
    - name: Build
      run: |
        {py_cmd} setup.py bdist_wheel
    - name: Upload artifacts
      uses: actions/upload-artifact@v1
      with:
        name: build-{platform}-{arch}-27
        path: dist
        """

    else:
        interpreter_tags = ' '.join(f'cp{a}{b}' for a, b in CPYTHON_TEST_VERSIONS if a > 2)

        return f"""
  build-{platform}-{arch}-abi3:

    runs-on: {platform}-latest
    {only_on('ubuntu', f'container: {MANYLINUX_CONTAINER}')}

    steps:
    - uses: actions/checkout@v2
    {only_on_not('ubuntu', f'''
    - name: Set up Python {pyver_str_dot}
      uses: actions/setup-python@v2
      with:
        python-version: "{pyver_str_dot}"
        architecture: {'x64' if arch == 64 else 'x86'}
    ''')}
    - name: Install dependencies
      run: |
        {py_cmd} -m pip install --upgrade pip
        {py_cmd} -m pip install --upgrade setuptools wheel packaging {only_on('ubuntu', 'auditwheel')}
    - name: Build
      shell: bash
      run: |
        {py_cmd} setup.py bdist_wheel
    {only_on('ubuntu', f'''
    - name: Run auditwheel
      run: |
        mkdir dist/wheelhouse
        {py_cmd} -m auditwheel repair -w dist/wheelhouse/ dist/*.whl
        rm dist/*.whl
        mv dist/wheelhouse/* dist/
        rm -rf dist/wheelhouse
    ''')}
    - name: Rename wheel file
      shell: bash
      run: |
        cd dist
        {py_cmd} ../.github/workflows/rename_wheel.py *.whl - {interpreter_tags}
    - name: Upload artifacts
      uses: actions/upload-artifact@v1
      with:
        name: build-{platform}-{arch}-abi3
        path: dist
        """


def make_test_job(platform: str, arch: int, pyver: tuple) -> str:
    """
    Make a test job for the specified platform and Python version
    (tests both the built wheel and the sdist)
    """
    pyver_str_dot, pyver_str_none, py_cmd = strings_for(platform, pyver)

    def only_if(condition, text):
        return text if condition else ''

    def only_on(platform_2, text):
        return only_if(platform == platform_2)

    def only_on_not(platform_2, text):
        return only_if(platform != platform_2)

    package_type = '27' if pyver < (3,0) else 'abi3'

    return f"""
  test-{platform}-{arch}-{pyver_str_none}:

    needs: [build-{platform}-{arch}-{package_type}, sdist]
    runs-on: {platform}-latest
    {only_if(platform == 'ubuntu' and pyver >= CPYTHON_3_BUILD_VERSION, f'container: {MANYLINUX_CONTAINER}')}

    steps:
    - uses: actions/checkout@v2
    {only_if((platform == 'ubuntu' and pyver < CPYTHON_3_BUILD_VERSION) or platform != 'ubuntu', f'''
    - name: Set up Python {pyver_str_dot}
      uses: actions/setup-python@v2
      with:
        python-version: "{pyver_str_dot}"
        architecture: {'x64' if arch == 64 else 'x86'}
    ''')}
    - name: Download build artifact
      uses: actions/download-artifact@v2
      with:
        name: build-{platform}-{arch}-{package_type}
    - name: Download sdist artifact
      uses: actions/download-artifact@v2
      with:
        name: sdist
    - name: Install dependencies
      run: |
        {py_cmd} -m pip install --upgrade pip
        {py_cmd} -m pip install pytest
    - name: Install wheel
      shell: bash
      run: |
        {py_cmd} -m pip install *.whl
    - name: Test wheel with pytest
      run: |
        cd tests
        {py_cmd} -m pytest
    - name: Uninstall wheel
      shell: bash
      run: {py_cmd} -m pip uninstall -y nsmblib
    - name: Install sdist
      shell: bash
      run: {py_cmd} -m pip install *.tar.gz
    - name: Test sdist with pytest
      run: |
        cd tests
        {py_cmd} -m pytest
    """


# YAML header
yml = ["""
name: Build and test
on: [push]

jobs:
"""]


# Make one build per platform (abi3),
# and perform one test per platform / Python version combo
yml.append(make_sdist_job(CPYTHON_3_BUILD_VERSION))
for arch in [32, 64]:
    for platform in PLATFORMS:

        if arch == 32 and platform != 'windows':
            # GHA actions/setup-python only provides 32-bit Python builds for Windows
            continue

        if platform != 'windows':
            # Microsoft Visual C++ Compiler for Python 2.7 can no longer
            # be legally used in CI contexts
            yml.append(make_build_job(platform, arch, CPYTHON_2_BUILD_VERSION))

        yml.append(make_build_job(platform, arch, CPYTHON_3_BUILD_VERSION))

        for pyver in CPYTHON_TEST_VERSIONS:
            if platform == 'windows' and pyver == (2,7):
                # MS VC++ Compiler for Py2.7 again (see above)
                continue
            yml.append(make_test_job(platform, arch, pyver))


# Write the output file
with open('wheels.yml', 'w', encoding='utf-8') as f:
    f.write("""################################################################
# THIS FILE IS AUTOGENERATED -- DO NOT EDIT DIRECTLY
# Edit the Python script in this same folder instead, and then run it to
# regenerate this file.
################################################################
""")

    for line in ''.join(yml).splitlines():
        line = line.rstrip()
        if not line: continue
        f.write(line + '\n')
