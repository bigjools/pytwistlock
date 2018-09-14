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
import json

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
        try:
            types = api.list_available_package_types(images, **image_spec)
        except exceptions.ImageNotFound:
            abort("No matching image found")
        if len(types) != 0:
            click.echo(" ".join(types))
        return

    if display_type == 'binary':
        return display_binaries(images, image_spec)

    try:
        pkgs = api.find_packages(display_type, images, **image_spec)
    except exceptions.NoPackages:
        abort("No packages found")
    except exceptions.ImageNotFound:
        abort("No matching image found")

    # Work out max column widths.
    name_w = max([len(pkg['name']) for pkg in pkgs])
    ver_w = max([len(pkg['version']) for pkg in pkgs])
    license_w = max([len(pkg['license']) for pkg in pkgs])
    cve_w = 9

    # Print heading.
    print('{name:<{name_w}} {version:<{ver_w}} '
          '{cveCount:<{cve_w}} {license:<{license_w}}\n'.format(
            name='NAME', name_w=name_w,
            version='VERSION', ver_w=ver_w,
            cveCount='CVE COUNT', cve_w=cve_w,
            license='LICENSE', license_w=license_w))

    # Print all packages.
    for pkg in sorted(pkgs, key=lambda t: t['name']):
        print('{name:<{name_w}} {version:<{ver_w}} '
              '{cveCount:{cve_w}} {license:<{license_w}}'.format(
                name=pkg['name'], name_w=name_w,
                version=pkg['version'], ver_w=ver_w,
                cveCount=pkg['cveCount'], cve_w=cve_w,
                license=pkg['license'], license_w=license_w))


def display_binaries(images, image_spec):
    """Print to stdout the binaries for an image.

    :param images: Images data in json format.
    :param image_spec: dict as returned by _get_image_spec.
    """
    try:
        binaries = api.find_binaries(images, **image_spec)
    except exceptions.ImageNotFound:
        abort("No matching image found")

    if len(binaries) == 0:
        return

    # Work out column width.
    path_w = max([len(binary['path']) for binary in binaries])

    print('{path:<{path_w}} {cveCount:<10}\n'.format(
        path='PATH', path_w=path_w,
        cveCount='CVE COUNT',
    ))
    for binary in binaries:
        print('{path:<{path_w}} {cveCount:<10}'.format(
            path=binary['path'], path_w=path_w,
            cveCount=binary['cveCount'],
        ))


def _process_images(searchtype, images, searchspec):
    if images is None:
        return

    display_packages(searchtype, images, searchspec)


def _list_images(images):
    click.echo(api.all_image_ids(images))


@click.group()
def main():
    pass


@click.group()
def image():
    """Retrieve information about images."""
    pass


main.add_command(image)


def _validate_image_params(ctx, expect_spec=False):
    if ctx.params['list_images']:
        return

    searchspec = ctx.params.get('searchspec')
    searchtype = ctx.params.get('searchtype')
    if (searchspec is None and expect_spec) and searchtype is None:
        raise click.BadParameter(
            'SEARCHSPEC and SEARCHTYPE must be specified when not listing '
            'images')


@image.command()
@click.option('--twistlock-url', envvar='TWISTLOCK_URL', required=True)
@click.option('--twistlock-user', envvar='TWISTLOCK_USER', required=True)
@click.option(
    '--twistlock-password', envvar='TWISTLOCK_PASSWORD', required=True)
@click.argument('searchspec')
@click.argument(
    'searchtype', type=click.Choice(SUPPORTED_PACKAGE_TYPES), required=False)
@click.option('--list-images', is_flag=True, default=False)
def search(
    twistlock_url, twistlock_user, twistlock_password, searchspec=None,
        searchtype=None, list_images=False):
    """Examine images on a Twistlock server."""
    if not list_images and searchspec is None:
            raise click.BadParameter(
                'SEARCHSPEC must be specified when not listing images')
    try:
        images = sources.search_remote(
            twistlock_url,
            userspec_from_params(twistlock_user, twistlock_password),
            searchspec)
    except Exception as e:
        abort(e)

    if list_images:
        return _list_images(images)

    return _process_images(searchtype, images, searchspec)


@image.command()
@click.argument('filename')
@click.argument('searchspec', required=False)
@click.argument(
    'searchtype', type=click.Choice(SUPPORTED_PACKAGE_TYPES), required=False)
@click.option('--list-images', is_flag=True, default=False)
def file(filename, searchspec=None, searchtype=None, list_images=False):
    """Examine images from a local file."""
    if not list_images:
        if searchtype is None or searchspec is None:
            raise click.BadParameter(
                'SEARCHTYPE and SEARCHSPEC must be specified when not listing '
                'images')
    try:
        images = sources.read_images_file(filename)
    except Exception as e:
        abort(e)

    if list_images:
        return _list_images(images)

    _process_images(searchtype, images, searchspec)


@image.command()
@click.option('--twistlock-url', envvar='TWISTLOCK_URL', required=True)
@click.option('--twistlock-user', envvar='TWISTLOCK_USER', required=True)
@click.option(
    '--twistlock-password', envvar='TWISTLOCK_PASSWORD', required=True)
@click.argument('searchspec')
@click.argument('filename', type=click.File('w'))
def save(
    twistlock_url, twistlock_user, twistlock_password, searchspec,
        filename):
    """Download image scan results from a Twistlock server and save locally."""
    try:
        images = sources.search_remote(
            twistlock_url,
            userspec_from_params(twistlock_user, twistlock_password),
            searchspec)
    except Exception as e:
        abort(e)

    if images is None:
        abort("No matching images")

    json.dump(images, filename)


if __name__ == '__main__':
    main()
