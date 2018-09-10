import sys
from setuptools import find_packages, setup

install_reqs = [
    'click',
    'requests',
]

tests_require = [
    'bandit',
    'coverage',
    'fixtures',
    'flake8',
    'ipython',
    'testrepository',
    'testtools',
]

target_dir = "lib/python{major}.{minor}/site-packages/pytwistcli".format(
    major=sys.version_info[0], minor=sys.version_info[1]
)

setup(
    name="pytwistcli",
    version="0.0.0",
    description="Python CLI/API client for Twistlock",
    url="https://github.com/bigjools/pytwistcli",
    author="Julian Edwards",
    license="Apache",
    packages=find_packages(exclude=['tests']),
    install_requires=install_reqs,
    include_package_data=True,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    zip_safe=False,
    entry_points={
      'console_scripts': [
          'pytwistcli = pytwistcli.cli:main',
      ]
    }

)
