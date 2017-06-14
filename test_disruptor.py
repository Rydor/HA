# -*- coding: utf-8 -*-
import unittest
import disruptor
import json
from mock import Mock, mock_open, patch


class ReadInventoryTest(unittest.TestCase):

    def setUp(self):
        self.disruptor = disruptor
        self.inv = '{"_meta": {"host": {"galera": {"phys_host": "local"}}}}'

    @patch("__builtin__.open", create=True)
    def test_read_inventory_file(self, mo):
        mo.side_effect = [
            mock_open(read_data=self.inv).return_value
        ]
        execute = disruptor.read_inventory("/dev/null")
        result = json.dumps(execute)
        self.assertEqual(self.inv, str(result))

# Run the tests

if __name__ == '__main__':
        unittest.main()
