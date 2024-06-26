#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


""""
Return excel file from csv file
"""

import argparse
import pandas as pd
import helpers as h
import re



def get_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (without extension)')
    parser.add_argument("--empty_file", "-e", action='store_true', help='create empty file for snakemake')
    parser.add_argument("--input_directory", "-di", help='')
    parser.add_argument("--output_directory", "-do", help='')
    parser.add_argument("--file_id", "-f", help='Unique ID')
    args = parser.parse_args()
    return args


def list_files_in_dir(directory, extension='.csv') -> list:
    file_names_list = [join(directory, f) for f in os.listdir(directory)
                       if isfile(join(directory, f)) and extension in f]
    return file_names_list


def update_overlap(df, analysis_test_type):
    if analysis_test_type == "right-tailed" or analysis_test_type == "left-tailed":
        print("Updating overlap score for one-sided test")
        mask = ((df['pvalue'] == 0) & (df['ratio'] == 1000))
        df['score_overlap'][mask] = 5
    elif analysis_test_type == "two-sided":
        mask = ((df['pvalue'] == 0) & ((df['ratio'] == 1000) | (df['ratio'] == 0.001)))
        df['score_overlap'][mask] = 5
        #df.loc['score_overlap',mask] = 5
    return df


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)
    test_type = rule_params['distribution']['test_type']
    try:
        subset_filters = rule_params['filter_data']['subset_filters']
    except KeyError:
        subset_filters = rule_params['gsea']['subset_filters']

    # load data
    if args.input_file:
        data_df = pd.read_csv(args.input_file, header=0, index_col=None)

        if rule_params['all']['specific_proteins']['keep']:
            print("Updating overlap score for specific proteins")
            result = update_overlap(data_df, test_type)
        else:
            result = data_df.copy()

        # get subset of data on which to perform enrichment - returns dictionary with dataframe
        subsets_data = h.subset_data(data_df, subset_filters)

        for subset_name in subsets_data:

            df = subsets_data[subset_name]

            # remove extension in path file
            output_file = re.sub('.csv', '', args.output_file) + '_{}.csv'.format(subset_name)

            h.export_result_to_csv(df, output_file)

    elif args.input_directory:
        files = list_files_in_dir(args.input_directory, '.csv')
        for file in files:
            data_df = pd.read_csv(file, header=0, index_col=None)

            if rule_params['all']['specific_proteins']['keep']:
                # update overlap
                result = update_overlap(data_df, test_type)
            else:
                result = data_df.copy()

            # get subset of data on which to perform enrichment - returns dictionary with dataframe
            subsets_data = h.subset_data(data_df, subset_filters)

            for subset_name in subsets_data:
                df = subsets_data[subset_name]

                # remove extension in path file
                output_file = re.sub('.csv', '', args.output_file) + '_{}.csv'.format(subset_name)
                h.export_result_to_csv(df, output_file)

    else:
        print('Input file(s) must be provided')

    if args.empty_file:
        dummy = pd.DataFrame()
        h.export_result_to_csv(dummy, args.output_file)
