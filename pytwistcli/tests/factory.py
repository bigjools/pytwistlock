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

"""Factory functions and classes for tests."""

try:
    from itertools import imap
except ImportError:
    # Python 3
    imap = map
from itertools import (
    islice,
    repeat,
)
import json
import random
import string


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
                  "pkgs": ${package}
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
}


class Factory:
    """Class that defines helpers that make things for you."""

    random_letters = imap(
        random.choice, repeat(string.ascii_letters + string.digits))

    def make_string(self, prefix="", size=10):
        return prefix + "".join(islice(self.random_letters, size))

    def get_response_template(self, **kwargs):
        # Populate template with default random values where not provided by
        # the caller.
        template_args = _template_args.copy()
        for key in template_args:
            if kwargs.get(key, None) is None:
                template_args[key] = self.make_string(key)
            else:
                template_args[key] = kwargs[key]

        # Package is a special case as its default must be an empty
        # list.
        if 'package' in kwargs:
            template_args['package'] = json.dumps(kwargs['package'])
        else:
            template_args['package'] = []

        string_response = response_template.substitute(**template_args)
        return json.loads(string_response)

    def make_package_list(self, num_packages=3):
        packages = []
        for i in range(0, num_packages):
            p = dict(
                name=self.make_string(),
                version=self.make_string(),
                license=self.make_string(),
            )
            packages.append(p)
        return packages

    def make_image_with_os_packages(self, num_packages=3):
        tag = self.make_string("tag")
        packages = self.make_package_list(num_packages)
        images = self.get_response_template(image_tag1=tag, package=packages)
        return images, tag, packages


# Factory is a singleton.
factory = Factory()
