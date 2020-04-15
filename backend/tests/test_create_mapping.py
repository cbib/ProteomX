from unittest import TestCase

import create_mapping_file

class Test(TestCase):
    def test_create_mapping(self):
        df = self.create_mapping(["P1", "P2", "P3", "P4"], "foo", ["P10", "P11", "P12"], "bar")
        print(df)
        self.assertEqual(df.shape, (7, 3))
