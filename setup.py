#!/usr/bin/env python
# -*- coding: utf-8 -*-



import io
import os
import re
from setuptools import find_packages, setup, Command

# What packages are required for this module to be executed?
REQUIRED = [
    'pandas>=0.23.4',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

current_dir = os.path.abspath(os.path.dirname(__file__))


def get_meta():
    meta_re = re.compile(r"(?P<name>__\w+__) = '(?P<value>[^']+)'")
    meta_d = {}
    with open(os.path.join(current_dir, 'china_idiom', '__init__.py'),
              encoding='utf8') as fp:
        for match in meta_re.finditer(fp.read()):
            meta_d[match.group('name')] = match.group('value')
    return meta_d

meta_d = get_meta()

try:
    with io.open(os.path.join(current_dir, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = meta_d['__description__']

packages = [
    'china_idiom',
]


# Where the magic happens:
setup(
    name=meta_d['__title__'],
    version=meta_d['__version__'],
    description=meta_d['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=meta_d['__author__'],
    author_email='sfyc23@gmail.com',
    license=meta_d['__license__'],
    python_requires='>=3.6.0',
    url='https://github.com/sfyc23/China-idiom',
    # packages=find_packages(exclude=('tests',)),
    packages=packages,
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    package_data={'china_idiom': ['idiom.csv']},

    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    keywords='China,idiom,成语,成语接龙,成语大全',

)
# python setup.py sdist bdist_wheel
# twine upload dist/*


