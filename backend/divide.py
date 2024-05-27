#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Divide input dataframe according to contrast matrix
Useful when several groups of sample in one large file and analysis has to be seperated for each comparison
Comparison file = contrast matrix
Format :
each ensemble of samples (ex : Control_groupA, Control_groupB
Must follow order given in mapping file (ex: Group, Treatment, Sample ==>
"""

import argparse
import logging.config
import pandas as pd
import os
import helpers as h
import paths
import re
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--comparison_file", "-c")
    parser.add_argument("--output_file", "-o", help='Output file')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


# TODO condition and reference = list !
def get_comparison_data(contrast_df: pd.DataFrame) -> dict:
    """
    Input format:
    Column == transposed index : subsets of samples (ex: Control_groupA)
        1 where there is a comparison to perform. In this case, the
        0 elsewhere

    Returns a dictionary with the name of each comparison (what is compared, string to use as file name) and the name
    of each value column to get for this comparison
    """

    comparisons_dict = h.autovivify(2, list)

    for i in range(contrast_df.shape[0]):
        for j in range(contrast_df.shape[1]):
            if contrast_df.iloc[i][j] == 1:
                # get name of reference condition and compared condition, stripped of whitespaces
                reference = contrast_df.index[i].strip()
                condition = contrast_df.columns[j].strip()

                comparison_name = "{}_{}_vs_{}.csv".format(filename, condition, reference)
                comparisons_dict[comparison_name]['condition'] = condition
                comparisons_dict[comparison_name]['reference'] = reference

    return comparisons_dict


def get_base_df(df: pd.DataFrame, values_prefix: str) -> pd.DataFrame:
    # basically get every columns except the ones with abundances values
    return df[df.columns[~df.columns.str.startswith(values_prefix)]]


def subset_df_for_each_comparison(df: pd.DataFrame, base_df: pd.DataFrame, comparisons_dict: dict):
    values_prefix = rule_params["all"]["values_cols_prefix"]
    abundance_df = df.filter(regex=values_prefix)
    for comparison in comparisons_dict:
        # get abundances values for reference
        reference_abundances_col = abundance_df.filter(
            regex="{}_(.+?)?{}_".format(values_prefix, comparisons_dict[comparison]["reference"]))


        # Add a descriptor in column names / useful if several different control to use, more flexible than in the
        # config file (
        reference_abundances_col = reference_abundances_col.add_suffix('_reference')

        # get abundances values for the condition to compare with reference
        condition_abundances_col = abundance_df.filter(
            regex="{}_(.+?)?{}_".format(values_prefix, comparisons_dict[comparison]["condition"]))

        # create complete dataframe
        result_df = pd.concat([base_df, reference_abundances_col, condition_abundances_col], axis=1)

        # export result
        output_result = os.path.join(os.path.dirname(args.output_file), '{}'.format(comparison))

        logging.debug('Path to file: {}'.format(output_result))
        h.export_result_to_csv(result_df, output_result)
        logger.info('Data for {} exported to csv'.format(comparison))

    return


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)
    filename = h.filename(args.input_file)

    # get logger
    logpath = os.path.join(paths.global_data_dir, args.file_id, 'log/divide.log')
    logger = h.get_logger(logpath)

    # get data
    logger.debug("Loading data : {}".format(args.input_file))
    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # parameters
    values_cols_prefix = rule_params['all']['values_cols_prefix']
    how_to_divide = rule_params['divide']['how']
    divide_on = rule_params['divide']['on']

    if how_to_divide == "comparison":
        if divide_on != "comparison_file":
            logger.info("WARNING: discrepancy between two options")
            sys.exit(0)

        # get contrast matrix
        logger.debug("Loading contrast matrix : {}".format(args.comparison_file))
        comparison_df = pd.read_csv(args.comparison_file, index_col=0, header=0, sep='\t')

        comparisons = get_comparison_data(comparison_df)

        # get columns to keep in every results file (metadata col in the config file + every other columns previously
        # computed (log2FC, etc.)
        base_df = get_base_df(data_df, values_cols_prefix)

        # get every subset data frame and export
        subset_df_for_each_comparison(data_df, base_df, comparisons)

    elif how_to_divide == "analyte":
        # keep all columns for each data frame subset but filter rows based on the list provided
        for col in divide_on:
            for value in divide_on[col]:
                # subset row with regex expression (value) in the appropriate column (col)
                res = data_df[data_df[col].str.contains(value)]

                # avoid regex characters in file name
                value_str = re.sub('[^A-Za-z0-9]+', '', value)

                # export data frame
                out_res = os.path.join(os.path.dirname(args.output_file), '{}_{}.csv'.format(filename, value_str))
                h.export_result_to_csv(res, out_res)
