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

__metaclass__ = type


class PyTwistCliException(Exception):
    """Base class for all exceptions in PyTwistCli"""


class ParameterError(PyTwistCliException):
    """API function called with incorrect parameters."""


class ImageNotFound(PyTwistCliException):
    """Requested image cannot be found."""


class NoPackages(PyTwistCliException):
    """No packages of requested type in an image."""
