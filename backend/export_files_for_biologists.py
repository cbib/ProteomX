#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Pattern:
    dir1: A_vs_B.csv
    dir2: B_vs_A.csv
Objective:
    match files to merge data frame
"""

import argparse
import logging.config
import os
import pandas as pd
import numpy as np
import helpers as h
import paths
import scipy.stats as stats
from os.path import isfile, join
import collections
import loguru



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='')
    parser.add_argument("--output_file", "-o", help='')
    parser.add_argument("--input_directory", "-di", help='')
    parser.add_argument("--output_directory", "-do", help='')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    # export parameters --> config file ?
    parser.add_argument("--inverse_overlap", "-io", action="store_true")
    parser.add_argument("--log10pval", "-logpval", action="store_true")
    parser.add_argument("--protein_bank", "-b", action="store_true",
                        help='If true, remove proteins that are in TrEMBL ')
    parser.add_argument("--protein_bank_column", "-bc", action="store_true",
                        help='If true, remove column with name of proteomic bank ')
    parser.add_argument("--rm_overlap_column", "-oc", action="store_true",
                        help='If true, remove column with name of proteomic bank ')

    args = parser.parse_args()
    return args


def clean_dataframe(df, prefix_values):
    cv_col = df.filter(regex='CV_')
    values_col = df.filter(regex=prefix_values)
    abundance_rank_col = df.filter(regex='rank_')
    gmean_col = df.filter(regex='gmean_')
    nan_col = df.filter(regex='nan_')
    exclude_col = df.filter(regex='exclude_')
    specific_col = df.filter(regex='specific')

    col2drop = ["analyse_in_distr", "zscore", "exclude_CV", "specific", "pvalue_right", "pvalue_left",
                "pvalue_to_drop", "pvalue_onsided", "pvalue_best_side", "pvalue_approx",
                *cv_col,
                *values_col,
                *abundance_rank_col,
                *gmean_col,
                *nan_col,
                *exclude_col,
                *specific_col]

    res = df.drop(col2drop, errors='ignore', axis=1)
    return res


def compute_log10pvalue(df, col):
    # computa values
    col_log10pval = -np.log10(df[col])

    # insert new column just after the one used for computations
    loc = df.columns.get_loc(col) + 1
    df.insert(loc=loc, column="-log10({})".format(col), value=col_log10pval)
    return df


def list_files_in_dir(directory, extension='.csv') -> list:
    file_names_list = [join(directory, f) for f in os.listdir(directory)
                       if isfile(join(directory, f)) and extension in f]
    return file_names_list


def inverse_overlap(df):
    res = df.copy()

    res['score_overlap'] = -df['score_overlap']

    return res

def remove_trembl_proteins(df):
    res = df[df['gene_name_bank'] != "TrEMBL"]
    return res


def remove_bank_column(df):
    res = df.drop('gene_name_bank', axis=1)
    return res


def remove_overlap_column(df):
    res = df.drop('score_overlap', axis=1)
    return res


if __name__ == "__main__":
    args = get_args()

    rule_params = h.load_json_parameter(args.file_id)
    prefix_col_values = rule_params['all']['values_cols_prefix']

    # get data
    if args.input_file:
        data_df = pd.read_csv(args.input_file, header=0, index_col=None)

        if "pvalue_approx" in data_df.columns.tolist():
            data_df.rename({"pvalue": "pvalue_to_drop"}, axis=1, inplace=True)
            data_df.rename({"pvalue_approx": "pvalue"}, axis=1, inplace=True)

        # trim data frame for user export
        clean_df = clean_dataframe(data_df, prefix_col_values)

        # add -log10(pval)
        if args.log10pval:
            final_df = compute_log10pvalue(clean_df, 'pvalue')
        else:
            final_df = clean_df.copy()

        if args.inverse_overlap:
            print("Inversing overlap score")
            final_df = inverse_overlap(final_df)

        if args.protein_bank:
            print("Removing TrEMBL proteins")
            final_df = remove_trembl_proteins(final_df)

        if args.protein_bank_column:
            final_df = remove_bank_column(final_df)


        if args.rm_overlap_column:
            final_df = remove_overlap_column(final_df)

        # export result
        final_df=final_df.set_index('gene_name')
        h.export_result_to_csv(final_df, args.output_file, index=True)

    elif args.input_directory:
        files = list_files_in_dir(args.input_directory, '.csv')

        for file in files:
            try:
                data_df = pd.read_csv(file, header=0, index_col=None)
            except pd.errors.EmptyDataError:
                continue
            filename = h.filename(file)

            # trim data frame for user export
            clean_df = clean_dataframe(data_df, prefix_col_values)

            if args.log10pval:
                try:
                    # add -log10(pval)
                    final_df = compute_log10pvalue(clean_df, 'pvalue')
                except KeyError:
                    print("Column \'pvalue\'' not found")
                    final_df = clean_df.copy()
                    pass
            else:
                final_df = clean_df.copy()

            if args.inverse_overlap:
                print("Inversing overlap score")
                final_df = inverse_overlap(final_df)

            if args.protein_bank:
                print("Removing TrEMBL proteins")
                final_df = remove_trembl_proteins(final_df)

            if args.protein_bank_column:
                final_df = remove_bank_column(final_df)

            if args.rm_overlap_column:
                final_df = remove_overlap_column(final_df)

            # export result
            loguru.logger.debug(args.output_directory)
            output = os.path.join(args.output_directory, '{}.csv'.format(filename))
            final_df = final_df.set_index('gene_name')
            h.export_result_to_csv(final_df, output, index=True)
