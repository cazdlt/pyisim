# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev
#Tomado de : https://github.com/navdeep-G/setup.py/blob/master/setup.py

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'pyisim'
DESCRIPTION = "Easy to use Python client for IBM Security Identity Manager (ISIM/ITIM) web services (SOAP and REST APIs) "
URL = 'https://github.com/cazdlt/pyisim'
EMAIL = 'cazdlt@gmail.com'
AUTHOR = 'Andrés Zamora'
REQUIRES_PYTHON = '>=3.8.0'
VERSION = "0.1.0" # Get the version from the package __init__.py
REQUIRED = [
    "requests >= 2.23.0",
    "zeep >= 3.4.0"
]
EXTRAS={}

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    download_url=f'{URL}/archive/v{VERSION}.tar.gz',
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*","pycolp"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    keywords = ['isim', 'ibm-security', 'iam'],
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.8',
    ]

)