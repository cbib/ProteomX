import unittest
import sys

sys.path.extend(['/home/claire/Documents/ProteomX', '/home/claire/Documents/ProteomX/backend'])
import helpers


class Test(unittest.TestCase):
    def test_create_mapping(self):
        headers = ["group", "sample", "original labels"]
        df = helpers.create_mapping(headers, ["P1", "P2", "P3", "P4"], "foo", ["P10", "P11", "P12"], "bar")
        self.assertEqual(df.shape, (7, 3))

        with self.assertRaises(IndexError):
            # wrong call
            headers = ["some", "crappy headers"]
            df = helpers.create_mapping(headers, ["P1", "P2"], "foo", ["P10", "P11", "P12"], "bar")


if __name__ == '__main__':
    unittest.main()
