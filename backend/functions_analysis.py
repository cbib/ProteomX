#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cedric Usureau, Aurélien Barré, Hayssam Soueidan


"""
Collection of functions used in data analysis :
- log2FC
- overlap
- ttest
"""

import numpy as np
import pandas as pd
import statsmodels.stats.multitest as smm
from scipy import stats


def compute_overlap(df: pd.DataFrame, group1, group2, overlap_method: str) -> pd.DataFrame:
    for i in df.index.values:
        group1_values = np.array(group1.iloc[i])
        group2_values = np.array(group2.iloc[i])

        if overlap_method == "symmetric":
            df.loc[i, 'score_overlap'] = overlap_symmetric(group1_values, group2_values)
        else:
            df.loc[i, 'score_overlap'] = overlap_asymmetric(group1_values, group2_values)

    return df


def overlap_symmetric(x: np.array, y: np.array) -> int:
    a = [np.nanmin(x), np.nanmax(x)]
    b = [np.nanmin(y), np.nanmax(y)]

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    overlap = np.nanmax([a[0], b[0]]) - np.nanmin([a[1], b[1]])
    return overlap


def overlap_asymmetric(x: np.array, y: np.array) -> int:
    # x is the reference group
    overlap = np.nanmin(y) - np.nanmax(x)
    return overlap


def compute_p_value(df, group1, group2, id_col, equal_var, test_type):

    ttest_df = pd.DataFrame(columns=[id_col, 'pvalue'], index=df.index)

    for i in df.index.values:
        group1_values = np.array(group1.iloc[i], dtype=float)
        group2_values = np.array(group2.iloc[i], dtype=float)

        # two-tailed t-test
        stat, p_value = stats.ttest_ind(group1_values, group2_values,
                                        equal_var=equal_var,
                                        nan_policy='omit',
                                        alternative=test_type)

        ttest_df.loc[i] = [df.loc[i][id_col], p_value]

    return ttest_df


def compute_p_adjusted(df: pd.DataFrame, correction_method: str) -> pd.DataFrame:
    rej, pval_corr = smm.multipletests(df['pvalue'].values, alpha=float('0.05'), method=correction_method)[:2]
    df['padj'] = pval_corr
    return df


def merge_and_sort_results(df: pd.DataFrame, padj_df: pd.DataFrame, col_for_merge, sort_df_by):
    res = df.merge(padj_df, how='left', on=col_for_merge)
    res = res.sort_values(sort_df_by)
    return res


def update_pvalue_specific_proteins(df: pd.DataFrame, analysis_test_type, specific_column) -> pd.DataFrame:
    """
    Update 'pvalue' 'padj' column values for proteins specific to one condition/group
    """
    if analysis_test_type == "right-tailed" or analysis_test_type == "left-tailed":
        print("Updating overlap score for one-sided test")
        mask = ((df[specific_column] == "specific") & (df['ratio'] == 1000))

        df['pvalue'][mask] = np.where(mask, 0, 1)
        df['padj'][mask] = np.where(mask, 0, 1)

    elif analysis_test_type == "two-sided":
        mask = ((df[specific_column] == "specific") & (df['ratio'] == 1000) | (df[specific_column] == "specific") & (df['ratio'] == 0.001))
        df['pvalue'][mask] = 0
        df['padj'][mask] = 0

    return df