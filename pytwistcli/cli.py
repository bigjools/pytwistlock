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
import sys

from pytwistcli import api
from pytwistcli import sources


def url_from_context(ctx):
    return ctx.find_root().params['twistlock_url']


def userspec_from_context(ctx):
    return dict(
        username=ctx.find_root().params['twistlock_user'],
        password=ctx.find_root().params['twistlock_password'],
    )


def userspec_from_params(user, password):
    return dict(
        username=user,
        password=password,
    )


def abort(error):
    """Print the error and terminate execution."""
    click.echo(error)
    raise click.Abort()


def _display(display_type, *args, **kwargs):
    try:
        funcname = 'display_{}_packages'.format(display_type)
        f = getattr(sys.modules[__name__], funcname)
    except AttributeError:
        abort("{} is not a valid package type")
    f(*args, **kwargs)


def display_os_packages(images, image_id):
    image_id = image_id.lstrip('sha256:')
    pkgs = api.os_packages(images, image_id)
    for pkg in pkgs:
        print('{}\t{}\t{}\n'.format(
            pkg['name'], pkg['version'], pkg['license']
        ))


@click.group()
def main():
    pass


@click.group()
def image():
    pass


main.add_command(image)


@image.command()
@click.option('--twistlock-url', envvar='TWISTLOCK_URL', required=True)
@click.option('--twistlock-user', envvar='TWISTLOCK_USER', required=True)
@click.option(
    '--twistlock-password', envvar='TWISTLOCK_PASSWORD', required=True)
@click.argument('searchspec')
@click.argument('searchtype', type=click.Choice(['os']))
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

    _display(searchtype, images, searchspec)


@image.command()
@click.argument('filename')
@click.argument('image_id')
@click.argument('searchtype', type=click.Choice(['os']))
def file(filename, image_id, searchtype):
    """Examine images from a local file."""
    try:
        images = sources.read_images_file(filename)
    except Exception as e:
        abort(e)

    _display(searchtype, images, image_id)


if __name__ == '__main__':
    main()
