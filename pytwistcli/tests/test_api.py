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


"""This module contains tests for callable API functions."""


from testtools.matchers import (
    Equals,
)

from pytwistcli import api
from pytwistcli import exceptions
from pytwistcli.tests.factory import factory
from pytwistcli.tests.testcase import PyTwistcliTestCase


class TestAPI(PyTwistcliTestCase):
    """API Test cases."""

    def test_find_image_validates_params(self):
        # Raises ParameterError if both image_id and image_tag are
        # passed.
        self.assertRaises(
            exceptions.ParameterError,
            api.find_image, None, factory.make_string("id"),
            factory.make_string("tag"))

    def test_find_image_sha_returns_not_found(self):
        actual_sha = factory.make_string("actualsha")
        search_sha = factory.make_string("searchsha")
        images = self.factory.get_response_template(image_sha256=actual_sha)
        self.assertRaises(
            exceptions.ImageNotFound,
            api.find_image, images, image_sha=search_sha)

    def test_find_image_tag_returns_not_found(self):
        actual_tag = factory.make_string("actualtag")
        search_tag = factory.make_string("searchtag")
        images = self.factory.get_response_template(image_tag1=actual_tag)
        self.assertRaises(
            exceptions.ImageNotFound,
            api.find_image, images, image_tag=search_tag)

    def test_find_image_by_sha_returns_correct_image_data(self):
        sha = factory.make_string("sha")
        images = self.factory.get_response_template(image_sha256=sha)
        image = api.find_image(images, image_sha=sha)
        expected_id = 'sha256:{}'.format(sha)
        self.assertEqual(expected_id, image['id'])

    def test_find_image_by_tag_returns_correct_image_data(self):
        tag = factory.make_string("tag")
        images = self.factory.get_response_template(image_tag=tag)
        image = api.find_image(images, image_tag=tag)
        self.expectThat(image['repoTag']['tag'], Equals(tag))

    def test_all_packages_returns_all_packages(self):
        images, tag, packages = self.factory.make_image_with_os_packages()
        observed_packages = api.all_packages(images, image_tag=tag)
        for pkg_data in observed_packages:
            if pkg_data['pkgsType'] == 'package':
                self.expectThat(pkg_data['pkgs'], Equals(packages))

    def test_find_packages_returns_only_requested_packages(self):
        images, tag, packages = self.factory.make_image_with_os_packages()
        observed_packages = api.find_packages('package', images, image_tag=tag)
        self.assertThat(observed_packages, Equals(packages))

    def test_list_available_package_types_lists_all_package_types(self):
        images, tag, packages = self.factory.make_image_with_os_packages()
        list_of_types = api.list_available_package_types(images, image_tag=tag)

        # TODO: Using fixed sample data is bad; make a way to inject
        # different packages in the response data template.
        expected = ['package', 'python', 'nodejs']
        self.assertEqual(sorted(expected), sorted(list_of_types))
