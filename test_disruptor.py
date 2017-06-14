# -*- coding: utf-8 -*-
# Copyright 2017, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2017, Ryan Dorothy <ryan.dorothy@rackspace.com>

import unittest
import disruptor
import json
from mock import Mock, mock_open, patch


class ReadInventoryTest(unittest.TestCase):

    def setUp(self):
        self.disruptor = disruptor
        self.inv = '{"_meta": {"host": {"galera": {"phys_host": "local"}}}}'

    def test_read_inventory_file(self):
        # Mock the open file read and provide the self.inv as a return value.
        with patch("__builtin__.open", mock_open(read_data=self.inv),
                   create=True) as m:
            h = disruptor.read_inventory('/dev/null')
            result = json.dumps(h)
        self.assertEqual(self.inv, str(result))
        m.assert_called_once_with('/dev/null', 'r')


class GetSimilarGroupsTest(unittest.TestCase):

    def test_get_similar_groups(self):
        inv = {"galera1": "1", "galera2": "2", "rabbitmq1": "1"}
        result = disruptor.get_similar_groups("galera", inv)
        self.assertEqual(['galera1', 'galera2'], result)


# Run the tests
if __name__ == '__main__':
        unittest.main()
