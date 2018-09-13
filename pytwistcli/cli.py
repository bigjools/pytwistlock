#!/usr/bin/env python3
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


"""This module contains the Command Line Interface."""


# pytwistcli image search <searchspec> [os|python|node|etc]

import click

from pytwistcli import api
from pytwistcli import exceptions
from pytwistcli import sources


def userspec_from_params(user, password):
    """Given username and password, return a dict containing them."""
    return dict(
        username=user,
        password=password,
    )


def abort(error):
    """Print the error and terminate execution."""
    click.echo(error)
    raise click.Abort()


SUPPORTED_PACKAGE_TYPES = [
    'binary',
    'gem',
    'jar',
    'nodejs',
    'package',
    'python',
    'windows',

    'list'  # Special type, lists available types in an image.
]


def _get_image_spec(image_id):
    """Get kwargs suitable for api.find_image()"""
    ID_PREFIX = 'sha256:'
    image_spec = {}
    if image_id.startswith(ID_PREFIX):
        image_id = image_id.split(':', 1)[1]
        image_spec['image_sha'] = image_id
    else:
        image_spec['image_tag'] = image_id
    return image_spec


def display_packages(display_type, images, search_spec):
    """Print to stdout package information.

    :param display_type: One of the Twistlock supported package type
        specifiers. See cli.SUPPORTED_PACKAGE_TYPES.
    :param images: Images data in json format.
    :param search_spec: Any search criteria as recognised by the Twistlock
        server.
    """
    if display_type not in SUPPORTED_PACKAGE_TYPES:
        abort("{} is not a valid package type".format(display_type))

    image_spec = _get_image_spec(search_spec)
    if display_type == 'list':
        types = api.list_available_package_types(images, **image_spec)
        if len(types) != 0:
            click.echo(" ".join(types))
        return

    try:
        pkgs = api.find_packages(display_type, images, **image_spec)
    except exceptions.NoPackages:
        abort("No packages found")

    # Work out max column widths.
    name_w = max([len(pkg['name']) for pkg in pkgs])
    ver_w = max([len(pkg['version']) for pkg in pkgs])
    license_w = max([len(pkg['license']) for pkg in pkgs])

    # Print heading.
    print('{name:<{name_w}} {version:<{ver_w}} '
          '{license:<{license_w}}\n'.format(
            name='NAME', name_w=name_w,
            version='VERSION', ver_w=ver_w,
            license='LICENSE', license_w=license_w))

    # Print all packages.
    for pkg in sorted(pkgs, key=lambda t: t['name']):
        print('{name:<{name_w}} {version:<{ver_w}} '
              '{license:<{license_w}}'.format(
                name=pkg['name'], name_w=name_w,
                version=pkg['version'], ver_w=ver_w,
                license=pkg['license'], license_w=license_w))


@click.group()
def main():
    pass


@click.group()
def image():
    """Retrieve information about images."""
    pass


main.add_command(image)


@image.command()
@click.option('--twistlock-url', envvar='TWISTLOCK_URL', required=True)
@click.option('--twistlock-user', envvar='TWISTLOCK_USER', required=True)
@click.option(
    '--twistlock-password', envvar='TWISTLOCK_PASSWORD', required=True)
@click.argument('searchspec')
@click.argument('searchtype', type=click.Choice(SUPPORTED_PACKAGE_TYPES))
def search(
    twistlock_url, twistlock_user, twistlock_password, searchspec,
        searchtype):
    """Examine images on a Twistlock server."""
    try:
        images = sources.search_remote(
            twistlock_url,
            userspec_from_params(twistlock_user, twistlock_password),
            searchspec)
    except Exception as e:
        abort(e)

    if images is None:
        return

    if len(images) > 1:
        click.echo("Multiple images match: {}".format(
            api.all_image_ids(images)))
        return

    display_packages(searchtype, images, searchspec)


@image.command()
@click.argument('filename')
@click.argument('image_id')
@click.argument('searchtype', type=click.Choice(SUPPORTED_PACKAGE_TYPES))
def file(filename, image_id, searchtype):
    """Examine images from a local file."""
    try:
        images = sources.read_images_file(filename)
    except Exception as e:
        abort(e)

    display_packages(searchtype, images, image_id)


if __name__ == '__main__':
    main()
