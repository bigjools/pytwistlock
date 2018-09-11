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


import json
import requests

from pytwistcli import exceptions


def read_images_file(filename):
    """Read an images json file from disk.

    The Twistlock API has a /images call that returns all image scan reports.
    In the case that the user has saved this to a file, this function will
    read that file.

    :return: A dict as return by json.read()
    :exception: FileNotFoundError
    :exception: json.JSONDecodeError
    """
    with open(filename, 'r') as f:
        return json.load(f)


def search_remote(remote_url, user_spec, search_spec):
    """Look for scan results on a remote Twistlock console.

    :param remote_url: Base URL for the Twistlock instance,
        e.g. https://my-console.twistlock.com:8083/
    :param user_spec: Dictionary containing "username" and "password" items
    :param search_spec: Any search criteria allowed by the Twistlock API
        that will return scan results for a container,
        e.g. "sha256:b8f0d72e47390a50d60c8ffe44d623ce57be521bca9869..."
    """
    if 'username' not in user_spec or 'password' not in user_spec:
        raise exceptions.ParameterError(
            "user_spec must contain username and password")

    url_template = '{baseurl}/api/v1/images?search={searchspec}'
    url = url_template.format(baseurl=remote_url, searchspec=search_spec)
    reply = requests.get(
        url, auth=(user_spec['username'], user_spec['password']))

    reply.raise_for_status()

    # TODO: Check API return codes
    return reply.json()
