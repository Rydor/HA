# -*- coding: utf-8 -*-
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

# Run the tests

if __name__ == '__main__':
        unittest.main()
