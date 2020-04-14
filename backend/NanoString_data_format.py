#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
    nSolver export :

    first line: column header (Probe Name, several infos, then names of RCC files as header for each samples results.
    Second and + line : empty expect below RCC files names, with annotations defined in nSolver. Can be one or several line
    as per the number of annotations.

    Empty line

    Data : each line correspond to one probe

    => Get data above empty line as column header and metadata ; data below empty line as numeric data
    => Rename column with annotations (mapping step)
    => Keep only column defined in the config file (example : Probe Name, Species Name, Positive Flag...)
    => return dataframe
"""

import argparse
import os
import pandas as pd
import logging.config
import helpers as h
import collections
import json


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (data from nSolver) (csv)')
    parser.add_argument("--mapping_file", "-m", help='Output file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


def split_data(df):
    # detect empty line to split df between header and core

    empty_line_index = df.index[df.isna().all(axis=1)].values[0]
    header = df[:empty_line_index]
    data = df[empty_line_index+1:] # +1 to get rid of nan line

    return header, data


def rename_col_abundance_withjson(mapping_df, data_df):
    id_columns_dict = collections.defaultdict(list)
    prefix_col = rule_params['all']['value_col_prefix']

    for line in mapping_df.index.values:
        new_col_id = str(prefix_col)
        for level in rule_params['mapping']['column_for_mapping']:
            col = mapping_df.iloc[line][level]
            new_col_id = new_col_id + '_{}'.format(col)

        old_col_id = rule_params['mapping']['column_initial_label']
        old_col_value = mapping_df.iloc[line][old_col_id]
        id_columns_dict.update({old_col_value: new_col_id})
    print(id_columns_dict)
    data_df.rename(columns=id_columns_dict, inplace=True)

    return data_df


def df_to_nested_dict(df):
    if len(df.columns) == 1:
        return list(set(df.iloc[:,0].tolist()))

    grouped = df.groupby(df.columns[0])

    d = {k: df_to_nested_dict(g.iloc[:, 1:]) for k, g in grouped}
    return d


def build_json(mapping_df, path_to_json):
    col_to_group_by = rule_params['mapping']['column_for_mapping']
    mapp = mapping_df[col_to_group_by]

    d = df_to_nested_dict(mapp)

    with open(path_to_json, 'w+') as json_file:
        json.dump(d, json_file)

    logging.info('Writing dictionary in : {}'.format(path_to_json))
    logging.info('Dictionary with data structure : {}'.format(d))
    return d


def suppress_defined_columns(df):
    metadata_col = rule_params['all']['metadata_col']

    data_col_str = rule_params['all']['value_col_prefix'] + '_'
    data_col = df.filter(regex=data_col_str)
    #data_col = data_col.apply(pd.to_numeric) # à déplacer

    res = pd.concat([df[metadata_col], data_col], axis=1)
    return res


def suppress_panel_genes(df):
    res = df[df['Class Name'] == 'Endogenous']
    return res


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)

    logpath = os.path.join(rule_params['all']['logpath'], 'NanoString_data_format.log')
    logger = h.get_logger(logpath)

    input_df = pd.read_csv(args.input_file, header=0, index_col=None, sep='\t')
    print(input_df.head())

    if args.mapping_file:
        # annotate columns based on mapping file information
        df_metadata, df_numeric_data = split_data(input_df)

        header = df_metadata.iloc[0]  # discard rows with annotations
        data = pd.concat([header, df_numeric_data], axis=1)


        mapping_df = pd.read_csv(args.mapping_file, header=0, index_col=None)
        result_df = rename_col_abundance_withjson(mapping_df, data)

        path_to_json = rule_params['mapping']["path_to_json_mapping"] + "{}.json".format(filename)
        if not os.path.isdir(os.path.dirname(path_to_json)):
            os.makedirs(os.path.dirname(path_to_json))
        d = build_json(mapping_df, path_to_json)

    else:
        # need to extract informations from file
        # if no row for annotation, return error

        df_metadata, df_numeric_data = split_data(input_df)

        # TODO: check if value in annotation are consistent with mapping file ?


    result_df = suppress_defined_columns(result_df)

    result_df = suppress_panel_genes(result_df)

    result_df = result_df.apply(lambda x: x.str.replace(',', '.'))

    try:
        result_df.to_csv(args.output_file, index=False, decimal=".")
        logging.info('Writing in ' + args.output_file)

    except OSError:
        os.makedirs(args.output_file)
        result_df.to_csv(args.output_file, index=False)
        logging.info('Creating directory : ' + os.path.dirname(args.output_file))
        logging.info('Writing in ' + args.output_file)

    except TypeError as e:
        logging.info('Error writing output file:  ' + e )

    logging.info(' ------------------')