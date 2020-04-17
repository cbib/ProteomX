#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cédric Usureau, Aurélien Barré, Hayssam Soueidan

import unittest
from pandas.testing import assert_frame_equal

import functions_preprocessing as fp
import pandas as pd
import numpy as np

np.random.seed(30)


class Test(unittest.TestCase):
    def setUp(self):
        """Initialisation des tests"""
        self.df = pd.DataFrame(np.random.randint(0, 100, size=(6, 8)),
                               columns=["prefix_P_1", "prefix_P_2", "prefix_P_3", "prefix_P_4",
                                        "prefix_C_1", "prefix_C_2", "prefix_C_3", "prefix_C_4"])
        self.df_with_nans = self.df.mask(self.df <= 20, np.nan)

        self.list_group_prefix = ["prefix_P", "prefix_C"]

        self.values_cols_prefix = 'prefix'

        self.max_na_group_percentage = 80

        col_bool = pd.DataFrame(np.random.choice(a=[False, True], size=(6, 1)), columns=['boolean'])
        self.data_with_boolean_col = pd.concat([self.df_with_nans, col_bool], axis=1)

        self.stats_per_groups = pd.DataFrame(np.random.randint(0, 100, size=(6, 2)), columns=['max_na_1', 'max_na_2'])

    def test_na_per_group(self):
        res, stats = fp.na_per_group(self.df_with_nans, self.list_group_prefix, self.values_cols_prefix)

        # test if added columns number is the same in both result dataframes
        group_number = len(self.list_group_prefix)
        expected_col_number = len(self.df_with_nans.columns) + group_number
        self.assertEqual(len(res.columns), expected_col_number)

        # test added column names
        expected_col_names = ['nan_percentage_P', 'nan_percentage_C']
        self.assertEqual(expected_col_names, stats.columns.tolist())

        # test missing values percentage is good
        expected_value = 100 * stats.iloc[0, 0:4].isna().sum() / 8
        self.assertEqual(stats.loc[0, 'nan_percentage_P'], expected_value)

        # TODO : test if columns added to "res" and "stats" are the same
        # raise AssertionError => DataFrame.index are different. Not what I is tested but ?
        # assert_frame_equal(stats[['nan_percentage_P', 'nan_percentage_C']],
        #                    res[['nan_percentage_P', 'nan_percentage_C']])

    def test_flag_row_with_nas(self):
        res = fp.flag_row_with_nas(self.df_with_nans, self.stats_per_groups, self.max_na_group_percentage)

        # test result instance
        self.assertIsInstance(res, pd.DataFrame)

        # test 'exclude_na' column encoding
        in_exclude_na = [0, 1]

        self.assertLessEqual(len(res['exclude_na'].value_counts()), 2)
        for element in res['exclude_na']:
            self.assertIn(element, in_exclude_na)

        # test if values above threshold correspond to si les valeurs bien au dessus du seuils sont bien flaggées
        for idx in self.stats_per_groups.index:
            val1 = self.stats_per_groups.iloc[idx, 0]
            val2 = self.stats_per_groups.iloc[idx, 1]

            if val1 >= self.max_na_group_percentage or val2 >=self.max_na_group_percentage:
                self.assertEqual(res.loc[idx, 'exclude_na'], 1)
            else:
                self.assertEqual(res.loc[idx, 'exclude_na'], 0)

    def test_remove_flagged_rows(self):
        with self.assertRaises(KeyError):
            # wrong call
            fp.remove_flagged_rows(self.data_with_boolean_col, 'notinthecolumns', True)

        res = fp.remove_flagged_rows(self.data_with_boolean_col, 'boolean', True)

        # test if appropriate rows have not been removed
        lines_to_not_remove = self.data_with_boolean_col[self.data_with_boolean_col['boolean'] != True]
        assert_frame_equal(lines_to_not_remove, res)

        # test if appropriate rows have been removed
        lines_to_remove = self.data_with_boolean_col[self.data_with_boolean_col['boolean'] == True]
        for idx in lines_to_remove.index:
            self.assertNotIn(idx, res.index)


if __name__ == '__main__':
    unittest.main()
