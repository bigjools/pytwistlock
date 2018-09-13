# Pytwistcli - a Python wrapper around the Twistlock API

Pytwistcli is a pure Python 3 wrapper around the [Twistlock] RESTful API. It
provides convenient Pythonic access to the data and functions available
from the Twistlock server.

There is also a CLI to provide access to the same API functions.

At this stage only a very small subset of functionality is available;
namely interrogation of the packages available inside a container image,
as returned from the [Images API].

[Twistlock]: https://www.twistlock.com/
[Images API]: https://docs.twistlock.com/docs/latest/api/api_reference.html#images_get

## Examples

 `pytwistcli image file analysis.json myproject/container:latest list`

 Will return a list of the different types of packages available in the
 container identified by the tag `myproject/container:latest` in the
 data file `analysis.json`. Currently this is one of binary, gem, jar,
 nodejs, package (OS packages), python, and windows.

 `pytwistcli image file analysis.json sha256:940c39377c1a42ab19aa78b890037092aefd17edacd7ec135b1abb6876ad011a packages`

 Will return the list of operating system packages contained in the
 image with the given SHA256 whose data is in the `analysis.json` file.

 `pytwistcli image file analysis.json myproject/container:latest python`

 Will return the list of Python packages contained in the image with the
 given tag whose data is in the `analysis.json` file.

 `pytwistcli image search myproject/container:latest nodejs`

 Will search the Twistlock server directly for the container with tag `myproject/container:latest` and return its nodejs packages.

When searching the server you need to tell pytwistcli the server
details. You can do this in two different ways:

 - Pass CLI options `--twistlock-url`, `--twistlock-user` and
   `--twistlock-password`, or,
 - Set environment variarbles `TWISTLOCK_URL`, `TWISTLOCK_PASSWORD`, and
   `TWISTLOCK_USER`

 `pytwistcli image save data.json myproject/container:latest`

 Will save the data for myproject/container:latest to the file
 data.json. The search spec can also be anything matching multiple
 images, resulting in a data file containing multiple images.

 `pytwistcli image file --list-images <file>`
 `pytwistcli image search --list-images <searchspec>`

 Will show all images either in a file or on the server that match the
 search spec.


## Running tests
`tox`
Will run the Python 3 tests, the PEP8 tests, and Bandit (security
checker).

`tox -e cover`
will give you a test coverage report.

`tox -e debug`
Runs the tests in single threaded mode so you can add breakpoints.

`tox -e test pytwistcli.tests.test_file.TestClass.test_name`
Runs the pytwistcli.tests.test_file.TestClass.test_name test only.

## Running the application
`tox -e run`

Runs the CLI and passes in any arguments also given.

## Other handy environments
`tox -e repl`
gives you an iPython prompt in the virtualenv context

## Building RPMs
If setup.py or setup.cfg changes, re-build the spec file with:

```
python setup.py bdist_rpm --spec-only
```

