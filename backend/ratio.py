#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Compute ratio et log2FoldChange

json:
- which method (arithmetic mean, geometric mean...)
- which subset as reference
"""

import argparse
import os
import numpy as np
import pandas as pd
import helpers as h
import logging.config
import paths
import scipy.stats as stats


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def compute_gmean_per_protein(df):
    numeric_data = df.filter(regex=rule_params['all']['values_cols_prefix'])
    reference = rule_params['ratio']['reference']

    subset_reference = numeric_data.loc[:, numeric_data.columns.str.contains(reference)]
    subset_condition = numeric_data.loc[:, ~numeric_data.columns.str.contains(reference)]

    for protein in df.index.values:
        values_reference = subset_reference.iloc[protein]
        values_condition = subset_condition.iloc[protein]

        gmean_reference = stats.gmean(values_reference[~np.isnan(values_reference)])
        gmean_condition = stats.gmean(values_condition[~np.isnan(values_condition)])

        df.loc[protein, 'gmean_reference'] = gmean_reference
        df.loc[protein, 'gmean_condition'] = gmean_condition

    return df


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)
    filename = h.filename(args.input_file)
    data_structure = h.load_json_data(args.file_id, filename, rule_params['all']['divide'])

    logpath = os.path.join(paths.global_data_dir, args.file_id, 'log/ratio.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    reference = rule_params['ratio']['reference']

    # compute gmean per group
    result_df = compute_gmean_per_protein(data_df)

    # compute ratio
    result_df['ratio'] = result_df['gmean_condition'] / result_df['gmean_reference']

    # add arbitrary ratio value for specific protein
    if rule_params['all']['specific_proteins']['keep']:
        columns_reference = result_df.filter(regex=reference)

        # add ratio for proteins specific to reference
        mask = (result_df['specific'] == "specific") & (~columns_reference.isna().any(axis=1))
        result_df['ratio'][mask] = 0.001


        # add ratio for proteins specific to studied condition
        mask = (result_df['specific'] == "specific") & (columns_reference.isna().any(axis=1))
        result_df['ratio'][mask] = 1000


    # compute log2FC
    result_df['log2FoldChange'] = np.log2(result_df["ratio"])

    # export results
    result_df.drop(['gmean_reference', 'gmean_condition'], axis=1, inplace=True)
    h.export_result_to_csv(result_df, args.output_file)
