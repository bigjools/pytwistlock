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

__metaclass__ = type
__all__ = [
    'factory',
    ]

try:
    from itertools import imap
except ImportError:
    # Python 3
    imap = map
from itertools import (
    islice,
    repeat,
)
import random
import string


class Factory:
    """Class that defines helpers that make things for you."""

    random_letters = imap(
        random.choice, repeat(string.ascii_letters + string.digits))

    def make_string(self, prefix="", size=10):
        return prefix + "".join(islice(self.random_letters, size))


# Factory is a singleton.
factory = Factory()