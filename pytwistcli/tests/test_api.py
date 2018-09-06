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


import json
from string import Template
import testtools
from testtools.matchers import (
    Contains,
    Equals,
)

from pytwistcli import api
from pytwistcli import exceptions
from pytwistcli.tests.factory import factory


# This is a partial representation of the current response as documented at
# https://docs.twistlock.com/docs/latest/api/api_reference.html#images_get
# I am assured it won't change any time soon.
response_template = Template('''
{
    "images": [
    {
        "hostname": "${hostname}",
        "scanTime": "${scantime}",
        "info": {
          "image": {
              "ID": "sha256:${image_sha256}",
              "RepoTags": [
                  "${image_tag1}",
                  "${image_tag2}"
              ],
          "Many more things": "omitted"
          },
          "complianceVulnerabilities": [],
          "allCompliance": {},
          "cveVulnerabilities": [],
          "data": {
              "binaries": [],
              "packages": [
              {
                  "pkgsType": "package",
                  "pkgs": [
                  {
                      "version": "${package1version}",
                      "name": "${package1name}",
                      "license": "${package1license}"
                  },
                  {
                      "version": "${package2version}",
                      "name": "${package2name}",
                      "license": "${package2license}"
                  },
                  {
                      "version": "${package3version}",
                      "name": "${package3name}",
                      "license": "${package3license}"
                  }
                ]
              },
              {
                  "pkgsType": "nodejs",
                  "pkgs": []
              },
              {
                  "pkgsType": "python",
                  "pkgs": []
              }
              ],
              "files": null
          }
        }
    }
    ]
}
''')

_template_args = {
    'hostname': None,
    'scantime': None,
    'image_sha256': None,
    'image_tag1': None,
    'image_tag2': None,
    'package1version': None,
    'package1name': None,
    'package1license': None,
    'package2version': None,
    'package2name': None,
    'package2license': None,
    'package3version': None,
    'package3name': None,
    'package3license': None,
}


class PyTwistcliTestCase(testtools.TestCase):
    """Base test class containing helpers."""
    def get_response_template(self, **kwargs):
        # Some day it would be better to take a list of package details to
        # add and repeatedly insert a tempalte into the response, but today
        # is not that day.

        # Populate template with default random values where not provided by
        # the caller.
        template_args = _template_args.copy()
        for key in template_args:
            if kwargs.get(key, None) is None:
                template_args[key] = factory.make_string(key)
            else:
                template_args[key] = kwargs[key]
        string_response = response_template.substitute(**template_args)
        return json.loads(string_response)


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
        images = self.get_response_template(image_sha256=actual_sha)
        self.assertRaises(
            exceptions.ImageNotFound,
            api.find_image, images, image_sha=search_sha)

    def test_find_image_tag_returns_not_found(self):
        actual_tag = factory.make_string("actualtag")
        search_tag = factory.make_string("searchtag")
        images = self.get_response_template(image_tag1=actual_tag)
        self.assertRaises(
            exceptions.ImageNotFound,
            api.find_image, images, image_tag=search_tag)

    def test_find_image_by_sha_returns_correct_image_data(self):
        sha = factory.make_string("sha")
        images = self.get_response_template(image_sha256=sha)
        image = api.find_image(images, image_sha=sha)
        expected_id = 'sha256:{}'.format(sha)
        self.assertEqual(expected_id, image['image']['ID'])

    def test_find_image_by_tag_returns_correct_image_data(self):
        tag = factory.make_string("tag")
        other_tag = factory.make_string("tag")
        images = self.get_response_template(
            image_tag1=tag, image_tag2=other_tag)
        image = api.find_image(images, image_tag=tag)
        self.expectThat(image['image']['RepoTags'], Contains(tag))
        self.expectThat(image['image']['RepoTags'], Contains(other_tag))

    def make_image_with_os_packages(self):
        tag = factory.make_string("tag")
        packages = dict(
            package1name=factory.make_string(),
            package1version=factory.make_string(),
            package1license=factory.make_string(),
            package2name=factory.make_string(),
            package2version=factory.make_string(),
            package2license=factory.make_string(),
            package3name=factory.make_string(),
            package3version=factory.make_string(),
            package3license=factory.make_string(),
        )

        images = self.get_response_template(image_tag1=tag, **packages)
        return images, tag, packages

    def assertOSPackages(self, packages, observed_pkg_data):
        expected_packages = [
            dict(
                name=packages['package1name'],
                version=packages['package1version'],
                license=packages['package1license'],
            ),
            dict(
                name=packages['package2name'],
                version=packages['package2version'],
                license=packages['package2license'],
            ),
            dict(
                name=packages['package3name'],
                version=packages['package3version'],
                license=packages['package3license'],
            ),
        ]
        # This works without sorting as it relies on the
        # package ordering in the returned data.
        self.expectThat(observed_pkg_data, Equals(expected_packages))

    def test_all_packages_returns_all_packages(self):
        images, tag, packages = self.make_image_with_os_packages()
        observed_packages = api.all_packages(images, image_tag=tag)
        for pkg_data in observed_packages:
            if pkg_data['pkgsType'] == 'package':
                self.assertOSPackages(packages, pkg_data['pkgs'])

    def test_os_packages_returns_only_os_packages(self):
        images, tag, packages = self.make_image_with_os_packages()
        observed_packages = api.os_packages(images, image_tag=tag)
        self.assertOSPackages(packages, observed_packages)
