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

"""Base test class and utilities."""

import fixtures
import json
import os
import testtools

from pytwistcli.tests.factory import factory


class PyTwistcliTestCase(testtools.TestCase):
    """Base test class containing helpers."""

    factory = factory

    def make_test_file(self, images):
        tempdir = self.useFixture(fixtures.TempDir()).path
        data_file = os.path.join(tempdir, factory.make_string("testinput"))
        with open(data_file, "w") as f:
            f.write(json.dumps(images))
        return data_file
