#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Take a data frame as input and change column names according to mapping file ; return also a json file with mapping
data as dictionary
"""


import argparse
import pandas as pd
import json
import os
import logging.config
import collections
import helpers as h
import paths


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--mapping_file", "-map")
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')
    parser.add_argument("--config_file", "-c", help='Config file')

    args = parser.parse_args()
    return args


def rename_col_abundance_withjson(mapping_df, data_df):
    id_columns_dict = collections.defaultdict(list)
    prefix_col = rule_params['all']['values_cols_prefix']

    for line in mapping_df.index.values:
        new_col_id = str(prefix_col)
        for level in rule_params['mapping']['col_for_mapping']:
            col = mapping_df.iloc[line][level]
            new_col_id = new_col_id + '_{}'.format(col)

        old_col_id = rule_params['mapping']['col_label']
        old_col_value = mapping_df.loc[line][old_col_id]
        id_columns_dict.update({old_col_value: new_col_id})

    data_df.rename(columns=id_columns_dict, inplace=True)

    return data_df


# TODO: data type for json
def df_to_nested_dict(df):
    if len(df.columns) == 1:
        return list(set(df.iloc[:,0].tolist()))

    grouped = df.groupby(df.columns[0])

    d = {k: df_to_nested_dict(g.iloc[:, 1:]) for k, g in grouped}
    return d


def build_json(mapping_df, path_to_json):
    col_to_group_by = rule_params['mapping']['col_for_mapping']
    mapp = mapping_df[col_to_group_by]

    d = df_to_nested_dict(mapp)

    with open(path_to_json, 'w+') as json_file:
        json.dump(d, json_file)

    logging.info('Writing dictionary in : {}'.format(path_to_json))
    logging.info('Dictionary with data structure : {}'.format(d))
    return d


if __name__ == "__main__":
    args = get_args()
    filename = h.filename(args.input_file)

    if not args.config_file:
        rule_params = h.load_json_parameter(args.project, args.version)
    else:
        with open(args.config_file) as f:
            rule_params = json.load(f)

    logpath = os.path.join(paths.root_dir, paths.data_dir, args.project, args.version, 'log/mapping.log')
    logger = h.get_logger(logpath)

    logging.info('Starting mapping file: ' + args.input_file)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)
    mapping_df = pd.read_csv(args.mapping_file, header=0, index_col=None)

    result_df = rename_col_abundance_withjson(mapping_df, data_df)

    path_to_json = rule_params['mapping']["path_to_json_mapping"] + "{}.json".format(filename)
    path_to_json = os.path.join(paths.root_dir, paths.data_dir, args.project, args.version, path_to_json)

    # TODO 
    if not os.path.isdir(os.path.dirname(path_to_json)):
        os.makedirs(os.path.dirname(path_to_json))
    d = build_json(mapping_df, path_to_json)

    h.export_result_to_csv(result_df, args.output_file)
