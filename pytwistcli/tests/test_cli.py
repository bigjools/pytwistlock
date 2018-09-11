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
        # foo
        images, tag, packages = self.make_image_with_os_packages()
        input_file = self.make_test_file(image_tag1=tag, **packages)
        args = 'image file {filename} {searchspec} package'.format(
            filename=input_file, searchspec=tag)
        out, err, code = self._run(args)

        self.assertEqual(0, code, err)

        # I hate myself.
        p_list = {
            packages['package1name']:
                (packages['package1version'], packages['package1license']),
            packages['package2name']:
                (packages['package2version'], packages['package2license']),
            packages['package3name']:
                (packages['package3version'], packages['package3license'])
        }
        sorted_names = sorted(p_list)
        expected = textwrap.dedent("""\
            NAME       VERSION    LICENSE
            <BLANKLINE>
            {} {} {}
            {} {} {}
            {} {} {}
        """.format(
            sorted_names[0],
            p_list[sorted_names[0]][0], p_list[sorted_names[0]][1],
            sorted_names[1],
            p_list[sorted_names[1]][0], p_list[sorted_names[1]][1],
            sorted_names[2],
            p_list[sorted_names[2]][0], p_list[sorted_names[2]][1],
            ))
        u_out = out.decode('utf-8')
        self.assertThat(
            u_out, matchers.DocTestMatches(
                expected, flags=doctest.NORMALIZE_WHITESPACE))
