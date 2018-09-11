# Copyright (C) Julian Edwards. All Rights Reserved.
# Copyright (C) Cisco, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""This module contains tests for the CLI."""


import doctest
import os
import subprocess  # nosec
from testtools import matchers
import textwrap

from pytwistcli.tests.testcase import PyTwistcliTestCase


class TestCLI(PyTwistcliTestCase):
    """Tests for pytwistlock.cli"""

    def _run(self, args):
        cli = [os.path.join(os.path.dirname(__file__), '..', 'cli.py')]
        cli.extend(args.split())
        proc = subprocess.Popen(  # nosec
            cli,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return out, err, proc.returncode

    def test_returns_packages_from_file_search(self):
        images, tag, packages = self.make_image_with_os_packages(
            num_packages=3)
        input_file = self.make_test_file(images)
        args = 'image file {filename} {searchspec} package'.format(
            filename=input_file, searchspec=tag)
        out, err, code = self._run(args)

        self.assertEqual(0, code, err)

        p_sorted = sorted(packages, key=lambda t: t['name'])
        expected = textwrap.dedent("""\
            NAME       VERSION    LICENSE
            <BLANKLINE>
            {} {} {}
            {} {} {}
            {} {} {}
        """.format(
            p_sorted[0]['name'],
            p_sorted[0]['version'], p_sorted[0]['license'],
            p_sorted[1]['name'],
            p_sorted[1]['version'], p_sorted[1]['license'],
            p_sorted[2]['name'],
            p_sorted[2]['version'], p_sorted[2]['license'],
            ))
        u_out = out.decode('utf-8')
        self.assertThat(
            u_out, matchers.DocTestMatches(
                expected, flags=doctest.NORMALIZE_WHITESPACE))
