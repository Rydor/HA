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


class GetContainersByGroupTest(unittest.TestCase):

    def setUp(self):
        self.inv = {"galera": {"hosts": ["g_host1", "g_host2"]},
                    "rabbit": {"hosts": ["r_host1", "r_host2"]}}

    def test_get_containers_by_group(self):
        result = disruptor.get_containers_by_group("galera", self.inv)
        self.assertEqual(["g_host1", "g_host2"], result)

    def test_get_containers_by_group_not_present(self):
        with self.assertRaises(SystemExit) as cm:
            disruptor.get_containers_by_group("missing_service", self.inv)
        self.assertEqual(cm.exception.code, 1)


class GetContainersTest(unittest.TestCase):

    def setUp(self):
        self.inv = {"galera": {"hosts": ["g_host1", "g_host2"]},
                    "rabbit": {"hosts": ["r_host1", "r_host2"]}}

    def test_get_containers_single(self):
        result = disruptor.get_containers(["galera"], self.inv)
        self.assertEqual(["g_host1", "g_host2"], result)

    def test_get_containers_multiple_services(self):
        result = disruptor.get_containers(["galera", "rabbit"], self.inv)
        self.assertEqual(["g_host1", "g_host2", "r_host1", "r_host2"], result)

    def test_get_containers_multiple_flag(self):
        result = disruptor.get_containers(["galera"], self.inv, True)
        self.assertEqual([['g_host1', 'g_host2']], result)

    def test_get_containers_mutiple_services_and_flag(self):
        res = disruptor.get_containers(["galera", "rabbit"], self.inv, True)
        self.assertEqual([['g_host1', 'g_host2'], ['r_host1', 'r_host2']], res)

# Run the tests
if __name__ == '__main__':
        unittest.main()
