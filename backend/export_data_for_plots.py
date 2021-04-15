#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Export accession number abundances values for proteins which passed filtering on missing values and variation coefficient
"""

import argparse
import pandas as pd
import helpers as h


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def select_columns_with_abundances_measures(df, accession_column, prefix_columns_abundances):
    res = pd.concat([df[accession_column], df.filter(regex=prefix_columns_abundances)], axis=1)
    return res


if __name__ == "__main__":
    args = get_args()

    logger = h.get_logger(args.file_id, 'export_data_for_plots')

    # get parameters
    rule_params = h.load_json_parameter(args.file_id)
    accession_col = rule_params['all']['id_col']
    prefix_abundances_col = rule_params['all']['values_cols_prefix']

    # load data
    data = pd.read_csv(args.input_file)

    # select protein identifier column and abundances values columns
    result = select_columns_with_abundances_measures(data, accession_col, prefix_abundances_col)

    # export resulting dataframe as csv
    h.export_result_to_csv(result, args.output_file)
