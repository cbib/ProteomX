#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski

"""
Apply reduction of abundance values for each protein per line or groups of samples
# TODO : pouvoir changer de méthode ?
"""

import argparse
import pandas as pd
import os
import locale
import numpy as np
import paths
import helpers as h


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def get_abundance_subset(data_structure, depth, ab_col_prefix):
    # +1 for col prefix (ex: 'VAL')
    abundance_col_names = h.dict_to_list(data_structure, depth, ab_col_prefix, [])
    return abundance_col_names


def compute_reduction(df, ddof):
    res = df.copy()
    for protein in df.index.values:
        # get array with abundances values
        protein_values = np.array(
            df.iloc[protein].map(lambda x: locale.atof(x) if type(x) == str else x))

        # return array with each value divided by standard deviation of the whole array
        reduced_abundances = protein_values / np.nanstd(protein_values, ddof=ddof)

        # replace values in result df
        res.loc[protein] = reduced_abundances
    return res


def reduction_row_all_line(df: pd.DataFrame, values_cols_prefix: str, ddof) -> pd.DataFrame:
    data = df.filter(regex=values_cols_prefix)
    reduced_data = compute_reduction(data, ddof)
    return reduced_data


def reduction_row_by_group(df, groups, ddof):
    res = pd.DataFrame()

    for group in groups:
        # get data for samples in group
        data_group = df.filter(regex=group)

        # compute reduction on this data
        reduced_data_group = compute_reduction(data_group, ddof)

        # add result to result df
        res = pd.concat([res, reduced_data_group], axis=1)
    return res


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)
    filename = h.filename(args.input_file)
    data_structure = h.load_json_data(args.file_id, filename)

    # get logger
    logger = h.get_logger(args.file_id, 'data_reduction')

    # load data
    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # get parameters
    ddof = rule_params['reduction']['ddof']
    values_cols_prefix = rule_params['all']['values_cols_prefix']
    depth = len(rule_params['reduction']['on']) + 1  # +1 for prefix

    # save all columns but abundances columns
    base_df = data_df.drop(data_df.filter(regex=values_cols_prefix).columns,axis=1)

    # compute reduction per chosen group for each protein
    if rule_params['reduction']['on'] is list:
        groups = get_abundance_subset(data_structure, depth, values_cols_prefix)
        reduced_df = reduction_row_by_group(data_df, groups, ddof)

    # compute reduction with all abundances values for each protein
    elif rule_params['reduction']['on'] == "line":
        reduced_df = reduction_row_all_line(data_df, values_cols_prefix, ddof)

    # Concatenate reduced values to other columns
    result_df = pd.concat([base_df, reduced_df], axis=1)

    # export result
    h.export_result_to_csv(result_df, args.output_file)
