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


"""This module contains all externally callable API functions."""


from pytwistcli import exceptions


def find_image(images, image_sha=None, image_tag=None):
    """Given images data, find the required image.

    One of image_sha or image_tag must be specified.

    :param images: images context data
    :param image_sha: The full sha256 of the image
    :param image_tag: The tag for the image, e.g. foo/bar:latest

    :return: A dict containing the image context.
    :exception: exceptions.ImageNotFound
    :exception: exceptions.ParameterError
    """
    if image_sha is None and image_tag is None:
        raise exceptions.ParameterError(
            "One of image_sha or image_tag must be specified")
    if image_sha is not None and image_tag is not None:
        raise exceptions.ParameterError(
            "Only one of image_sha or image_tag may be specified")

    if images is None:
        raise exceptions.ImageNotFound()

    for data in images:
        info = data['info']
        if info['id'] == 'sha256:{}'.format(image_sha):
            return info
        if image_tag == info['repoTag']['tag']:
            return info

    raise exceptions.ImageNotFound()


def all_packages(*args, **kwargs):
    """Given images data, return dict of all packages for the
    requested image.

    :params: See `find_image`
    :exception: exceptions.ImageNotFound
    :exception: exceptions.ParameterError
    """
    image = find_image(*args, **kwargs)
    return image['data']['packages']


def all_image_ids(images):
    """Given images data, return a dict of all image IDs therein.

    :param images: images data from Twistlock, decoded from json
    :return: A dict whose keys are the IDs of the images, and values are
        the tag for that image (if present)
    """
    results = {}
    for image in images:
        info = image['info']
        results[info['id']] = info['repoTag']['tag']
    return results


def find_packages(package_type, *args, **kwargs):
    """Given the images data, return a list of packages in image
    which can be identified with image_id, or image_tag, matching
    the package type given.

    One of image_id or image_tag must be specified.

    :params: See `find_image`
    :param package_type: One of the supported "pkgsType" returned in the
        Twistlock image scan data. e.g. "packages", "nodejs", "python".
    :exception: exceptions.ImageNotFound
    :exception: exceptions.ParameterError
    :exception: exceptions.NoPackages
    """
    for pkg_dict in all_packages(*args, **kwargs):
        if pkg_dict['pkgsType'] == package_type:
            return pkg_dict['pkgs']

    raise exceptions.NoPackages()


def find_binaries(*args, **kwargs):
    """Given images data, return a list of dicts containing details of
    all binaries in the image which can be identified with image_id or
    image_tag.

    One of image_id or image_tag must be specified.

    :params: See `find_image`
    :exception: exceptions.ImageNotFound
    :exception: exceptions.ParameterError
    :exception: exceptions.NoPackages

    :return: A list of dicts:
        As per the Twistlock API, each dict takes the form:
        {
            name: 'binary name',
            path: 'full path to the binary including the name'
            md5: 'md5 hash for the binary'
            cveCount: 'Number of CVEs reported for the binary'
        }
    """
    image = find_image(*args, **kwargs)
    return image['data']['binaries']


def list_available_package_types(*args, **kwargs):
    """Given the images data, return a list of package types for which
    data is available.

    One of image_id or image_tag must be specified.""

    :params: See `find_image`
    """
    return [pkg_dict['pkgsType'] for pkg_dict in all_packages(*args, **kwargs)]
