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


# TODO: Map this into a Click sub-command
SUPPORTED_SEARCH_TYPES = [
    'binary',
    'gem',
    'jar',
    'nodejs',
    'package',
    'python',
    'windows',

    'list',  # Special type, lists available types in an image.
    'cves',  # Special type, lists CVEs in image.
]


def format_output(data, columns, sort_by):
    """Send formatted output to stdout.

    :param data: A list of dicts, one dict per output line. Each dict
        contains the columns to output.
    :param columns: A dict containing keys whose value is the key to
        pull out of the data dicts, which maps to the heading for that
        column in the output.
    :param sort_by: Which dict key by which to sort the rows
    """
    if sort_by not in columns:
        abort("Invalid field for sorting: {}".format(sort_by))
    widths = {}
    heading = ""
    for column in columns:
        if column not in data[0]:
            abort("{} is not a valid field".format(column))
        if type(data[0][column]) is int:
            # Just use heading width for int types.
            width = len(columns[column])
        else:
            width = max([len(d[column]) for d in data])
        # Width is the max of the column heading or the data itself.
        width = max(width, len(columns[column]))
        widths[column] = width
        heading += '{h:<{width}} '.format(h=columns[column], width=width)

    print(heading + '\n')
    for d in sorted(data, key=lambda key: key[sort_by]):
        line = ""
        for column in columns:
            line += '{item:<{width}} '.format(
                item=d[column], width=widths[column])
        print(line)


def _get_columns_from_fields(fields, default_columns):
    if not fields:
        return default_columns
    columns = {}
    for field in fields:
        columns[field] = field.upper()
    return columns


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


def display_packages(display_type, images, search_spec, sort_by, fields):
    """Print to stdout package information.

    :param display_type: One of the supported search type
        specifiers. See cli.SUPPORTED_SEARCH_TYPES.
        e.g 'package' will display OS packages.
    :param images: Images data in json format.
    :param search_spec: Any search criteria as recognised by the Twistlock
        server.
    :param sort_by: field in `fields` by which to sort the output
    :param fields: List of fields to display - must be keys in the package
        data.
    """
    if display_type not in SUPPORTED_SEARCH_TYPES:
        types = " ".join(SUPPORTED_SEARCH_TYPES)
        abort("{} is not a valid search type, require one of: {}".format(
            display_type, types))

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
        return display_binaries(images, image_spec, sort_by, fields)

    if display_type == 'cves':
        return display_cves(images, image_spec, sort_by, fields)

    try:
        pkgs = api.find_packages(display_type, images, **image_spec)
    except exceptions.NoPackages:
        abort("No packages found")
    except exceptions.ImageNotFound:
        abort("No matching image found")

    default_columns = {
        'name': 'NAME',
        'version': 'VERSION',
        'license': 'LICENSE',
    }
    columns = _get_columns_from_fields(fields, default_columns)

    if sort_by is None:
        sort_by = 'name'
    return format_output(pkgs, columns, sort_by)


def display_binaries(images, image_spec, sort_by, fields):
    """Print to stdout the binaries for an image.

    :param images: Images data in json format.
    :param image_spec: dict as returned by _get_image_spec.
    :param sort_by: field in `fields` by which to sort the output
    :param fields: List of fields to display - must be keys in the package
        data.
    """
    try:
        binaries = api.find_binaries(images, **image_spec)
    except exceptions.ImageNotFound:
        abort("No matching image found")

    if len(binaries) == 0:
        return

    default_columns = {
        'path': 'PATH',
        'cveCount': 'CVE COUNT',
    }
    columns = _get_columns_from_fields(fields, default_columns)
    if sort_by is None:
        sort_by = 'path'
    return format_output(binaries, columns, sort_by)


def display_cves(images, image_spec, sort_by, fields):
    """Print to stdout the CVEs for an image.

    :param images: Images data in json format.
    :param image_spec: dict as returned by _get_image_spec
    :param sort_by: field in `fields` by which to sort the output
    :param fields: List of fields to display - must be keys in the package
        data.
    """
    try:
        cves = api.find_cves(images, **image_spec)
    except exceptions.ImageNotFound:
        abort("No matching image found")

    if cves is None or len(cves) == 0:
        return

    default_columns = {
        'packageName': 'PACKAGE',
        'packageVersion': 'VERSION',
        'cve': 'CVE',
        'severity': 'SEVERITY',
        'status': 'STATUS',
        'link': 'LINK',
    }
    columns = _get_columns_from_fields(fields, default_columns)
    if sort_by is None:
        sort_by = 'packageName'
    format_output(cves, columns, sort_by)


def _process_images(searchtype, images, searchspec, sort_by, fields):
    if images is None:
        return

    display_packages(searchtype, images, searchspec, sort_by, fields)


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


def add_options(options):
    """Decorator to add a list of options."""
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def _validate_image_params(ctx, expect_spec=False):
    if ctx.params['list_images']:
        return

    searchspec = ctx.params.get('searchspec')
    searchtype = ctx.params.get('searchtype')
    if (searchspec is None and expect_spec) and searchtype is None:
        raise click.BadParameter(
            'SEARCHSPEC and SEARCHTYPE must be specified when not listing '
            'images')


twistlock_server_options = [
    click.option('--twistlock-url', envvar='TWISTLOCK_URL', required=True),
    click.option('--twistlock-user', envvar='TWISTLOCK_USER', required=True),
    click.option(
        '--twistlock-password', envvar='TWISTLOCK_PASSWORD', required=True),
]


format_options = [
    click.option('--sort-by'),
    click.option('--field', '-f', 'fields', multiple=True),
]


@image.command()
@add_options(twistlock_server_options)
@click.argument('searchspec')
@click.argument(
    'searchtype', type=click.Choice(SUPPORTED_SEARCH_TYPES), required=False)
@click.option('--list-images', is_flag=True, default=False)
@add_options(format_options)
def search(
    twistlock_url, twistlock_user, twistlock_password, searchspec=None,
        searchtype=None, list_images=False, sort_by=None, fields=None):
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

    return _process_images(searchtype, images, searchspec, sort_by, fields)


@image.command()
@click.argument('filename')
@click.argument('searchspec', required=False)
@click.argument(
    'searchtype', type=click.Choice(SUPPORTED_SEARCH_TYPES), required=False)
@click.option('--list-images', is_flag=True, default=False)
@add_options(format_options)
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
@add_options(twistlock_server_options)
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
