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
import string
import testtools

from pytwistcli.tests.factory import factory


# This is a partial representation of the current response as documented at
# https://docs.twistlock.com/docs/latest/api/api_reference.html#images_get
# I am assured it won't change any time soon.
response_template = string.Template('''
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

    factory = factory

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

    def make_test_file(self, *args, **kwargs):
        data = self.get_response_template(*args, **kwargs)
        tempdir = self.useFixture(fixtures.TempDir()).path
        data_file = os.path.join(tempdir, factory.make_string("testinput"))
        with open(data_file, "w") as f:
            f.write(json.dumps(data))
        return data_file
