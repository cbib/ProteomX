#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Compute statistical tests : Student, Welch or Wilcoxon (Mann-Whitney) tests
"""

import argparse
import pandas as pd
import statsmodels.stats.multitest as smm
from loguru import logger
from scipy import stats
import helpers as h
import numpy as np



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


def compute_p_value(df, id_col):

    reference = rule_params["ttest"]["reference"]
    equal_var = rule_params["ttest"]["equal_var"]

    ttest_df = pd.DataFrame(columns=[id_col, 'pvalue'], index=data_df.index)

    values_df = df.filter(regex=rule_params["all"]["values_cols_prefix"])

    reference_columns = [x for x in values_df.columns.values if reference in x]
    condition_columns = [x for x in values_df.columns.values if reference not in x]

    for i in df.index.values:
        reference_values = np.array(df.iloc[i][reference_columns], dtype=float)
        condition_values = np.array(df.iloc[i][condition_columns], dtype=float)

        # two-tailed t-test
        stat, p_value = stats.ttest_ind(condition_values, reference_values, equal_var=equal_var, nan_policy='omit')

        ttest_df.loc[i] = [df.loc[i][id_col], p_value]

    return ttest_df


def compute_p_adjusted(df):
    correction_method = rule_params["ttest"]["correction_method"]

    rej, pval_corr = smm.multipletests(df['pvalue'].values, alpha=float('0.05'), method=correction_method)[:2]
    df['padj'] = pval_corr
    return df


def merge_and_sort_results(df, padj_df, id_col):
    res = df.merge(padj_df, how='left', on=id_col)
    res = res.sort_values(rule_params["ttest"]["sort_res_by"])
    return res


def log_significant_protein_number(res):
    significant = len(result_df.loc[res['padj'] < 0.05])
    logger.info(" {} significant proteins (p-adj < 0.05) in {}".format(significant, filename))
    return


if __name__ == "__main__":
    args = get_args()
    filename = h.filename(args.input_file)
    rule_params = h.load_json_parameter(args.project, args.version)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    id_col = rule_params["all"]["id_col"]

    ttest_pval = compute_p_value(data_df, id_col)
    ttest_padj = compute_p_adjusted(ttest_pval)
    result_df = merge_and_sort_results(data_df, ttest_padj, id_col)

    log_significant_protein_number(result_df)

    h.export_result_to_csv(result_df, args.output_file)

