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
[
    {
        "hostname": "${hostname}",
        "scanTime": "${scantime}",
        "info": {
          "id": "sha256:${image_sha256}",
          "repoTag": {
            "registry": "",
            "repo": "myregistry/foo",
            "tag": "${image_tag}",
            "digest": ""
          },
          "complianceVulnerabilities": [],
          "allCompliance": {},
          "cveVulnerabilities": ${cveVulnerabilities},
          "data": {
              "binaries": ${binaries},
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
''')

_template_args = {
    'hostname': None,
    'scantime': None,
    'image_sha256': None,
    'image_tag': None,
}
_template_empty_list_defaults = ('package', 'binaries', 'cveVulnerabilities')

VULN_ID_CHOICES = (
    # Taken directly from Twistlock API docs at
    # https://docs.twistlock.com/docs/latest/api/api_reference.html#images_get
    "46",
    "47",
    "48",
    "49",
    "410",
    "411",
    "412",
    "413",
)
VULN_SEVERITY_CHOICES = (
    "Critical",
    "High",
    "Medium",
    "Low",
)


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

        # Special cases where defaults must be an empty list.
        for default in _template_empty_list_defaults:
            if default in kwargs:
                template_args[default] = json.dumps(kwargs[default])
            else:
                template_args[default] = []

        string_response = response_template.substitute(**template_args)
        return json.loads(string_response)

    def make_package_list(self, num_packages=3):
        packages = []
        for i in range(0, num_packages):
            p = dict(
                name=self.make_string(),
                version=self.make_string(),
                license=self.make_string(),
                cveCount=random.randint(0, 10),  # nosec
            )
            packages.append(p)
        return packages

    def make_binaries_list(self, num_binaries=3):
        binaries = []
        for i in range(0, num_binaries):
            b = dict(
                name=self.make_string("name"),
                path=self.make_string("path"),
                md5=self.make_string("md5"),
                cveCount=random.randint(0, 10),  # nosec
            )
            binaries.append(b)
        return binaries

    def make_cvevulnerabilities_list(self, num_vulns=3):
        vulns = []
        for i in range(0, num_vulns):
            v = dict(
                text=self.make_string("text"),
                id=random.choice(VULN_ID_CHOICES),  # nosec
                severity=random.choice(VULN_SEVERITY_CHOICES),  # nosec
                cvss=random.randint(0, 10),  # nosec
                status=self.make_string("status"),
                cve=self.make_string("CVE-"),
                description=self.make_string("description"),
                link=self.make_string("link"),
                type="image",
                packageName=self.make_string("packagename"),
                packageVersion=self.make_string("packageversion"),
            )
            vulns.append(v)
        return vulns

    def make_image_with_os_packages(self, num_packages=3):
        tag = self.make_string("tag")
        packages = self.make_package_list(num_packages)
        images = self.get_response_template(image_tag=tag, package=packages)
        return images, tag, packages

    def make_image_with_binaries(self, num_binaries=3):
        tag = self.make_string("tag")
        binaries = self.make_binaries_list(num_binaries)
        images = self.get_response_template(image_tag=tag, binaries=binaries)
        return images, tag, binaries

    def make_image_with_vulnerabilities(self, num_vulns=3):
        tag = self.make_string("tag")
        vulns = self.make_cvevulnerabilities_list(num_vulns)
        images = self.get_response_template(
            image_tag=tag, cveVulnerabilities=vulns)
        return images, tag, vulns


# Factory is a singleton.
factory = Factory()
