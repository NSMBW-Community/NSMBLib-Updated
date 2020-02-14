
yml = []

yml.append("""
name: Build wheels
on: [push]

jobs:
""")

if False:
    yml.append("""
  mac_windows:

    strategy:
      matrix:
        python-version: [2.7, 3.5, 3.6, 3.7, 3.8]
        platform: [macos-latest, windows-latest]
    runs-on: ${{ matrix.platform }}

    steps:
    - uses: actions/checkout@v2
    - uses: ilammy/msvc-dev-cmd@v1
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install Microsoft Visual C++ Compiler for Python 2.7
      if: (matrix.platform == 'windows-latest') && (matrix.python-version == '2.7')
      uses: crazy-max/ghaction-chocolatey@v1
      with:
        args: install vcpython27
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install setuptools wheel
    - name: Build
      run: |
        python setup.py bdist_wheel
    - name: Upload artifacts
      uses: actions/upload-artifact@v1
      with:
        name: build-${{ matrix.platform }}-${{ matrix.python-version }}
        path: dist
""")

for pyver in ['27', '35', '36', '37', '38']:
    if pyver == '27':
        pycommand = 'python'
    elif pyver == '38':
        pycommand = '/opt/python/cp38-cp38/bin/python'
    else:
        pycommand = f'/opt/python/cp{pyver}-cp{pyver}m/bin/python'
    yml.append(f"""
  manylinux-{pyver}:
""")

    if pyver == '27':
        yml.append(f"""
    strategy:
      matrix:
        python-version: [2.7]
""")

    yml.append(f"""
    runs-on: ubuntu-latest
    {'container: quay.io/pypa/manylinux2014_x86_64' if pyver != '27' else ''}

    steps:
    - uses: actions/checkout@v2
    - name: Install dependencies
      run: |
        {pycommand} -m pip install --upgrade pip
        {pycommand} -m pip install setuptools wheel
    - name: Build
      run: |
        {pycommand} setup.py bdist_wheel
    - name: Upload artifacts
      uses: actions/upload-artifact@v1
      with:
        name: build-manylinux-{pyver}
        path: dist
""")

with open('wheels.yml', 'w', encoding='utf-8') as f:
    f.write(''.join(yml))