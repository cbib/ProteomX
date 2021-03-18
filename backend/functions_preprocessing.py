#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cedric Usureau, Aurélien Barré, Hayssam Soueidan


"""
Collection of functions used in data preprocessing:
- mapping
- proteomic preprocessing
"""

import pandas as pd
import numpy as np
import collections
import json
import logging.config


# mapping
def rename_col_abundance_withjson(mapping_df: pd.DataFrame, data_df: pd.DataFrame, values_cols_prefix: str, col_for_mapping: list,
                                  col_label: str) -> pd.DataFrame:
    """
    Inputs:
        - mapping_df: data frame with metadata on samples (groups, treatment, replicate, age...). Each line correspond to
                      one sample
        - df: data frame with proteomics data
        - values_col_prefix: prefix to add to all abundance column
        - col_for_mapping: name of columns to use in the mapping_df in order to create unique sample labels.
        - col_label: name of the column in the mapping_df with raw sample labels to modify.

    Returns input data frame (df) with formatted header for abundance data column, built from metadata in mapping df

    Example:
        mapping_df = pd.DataFrame()
        data_df = pd.DataFrame()

        result_df = pd.DataFrame()

    """

    # initialize dictionary
    id_columns_dict = collections.defaultdict(list)

    for line in mapping_df.index.values:
        # create formatted column id for the considered sample
        new_col_id = str(values_cols_prefix)
        for level in col_for_mapping:
            col = mapping_df.iloc[line][level]
            new_col_id = new_col_id + '_{}'.format(col)

        # get sample abundance column label in initial data frame
        old_col_id = mapping_df.loc[line][col_label]

        # update dictionary
        id_columns_dict.update({old_col_id: new_col_id})

    # change corresponding column name
    result_df = data_df.rename(columns=id_columns_dict)

    return result_df


def df_to_nested_dict(df: pd.DataFrame) -> dict or list:
    """
    Input:
        - df: data frame with metadata. Each line correspond to one sample, each column correspond to a categorical
        variable (such as "treatment" with values yes and no or "group" with values group1 and group2).
        ! Columns to order
        ! Subset of mapping file

    Recursive function. Returns a (nested) dictionary : each key is a categorical variable ; the value associated is
    either a list or another dictionary. Returns a list if the mapping file has only one column.

    Example:
    df = pd.DataFrame([['A','y', 1], ['A','n',2], ['B','y',1],['B','y',2] ], columns=['group', 'treatment', 'replicate'])
    returns:
    d = {'A': {'n': [2], 'y': [1]}, 'B': {'y': [1, 2]}}
    """

    if len(df.columns) == 1:
        return list(set(df.iloc[:, 0].tolist()))

    grouped = df.groupby(df.columns[0])

    d = {k: df_to_nested_dict(g.iloc[:, 1:]) for k, g in grouped}
    return d


def build_json(mapping_df: pd.DataFrame, path_to_json: str, col_to_group_by: list) -> dict or list:
    """
    Inputs:
        - mapping_df: data frame with metadata for each sample. Each line correspond to one sample, each column
        corresponds to one descriptor (group to which the sample belongs, replicate number, age of the sample, etc.)
        - path_to_json: path.
        - col_to_group_by: list of column in the mapping_df with categorical variables that are used for abundance
        column header formatting
    Returns a (nested) dictionary
    """
    # subset mapping df with only column with categorical variables to use as sample descriptor
    mapping_subset = mapping_df[col_to_group_by]

    # get (nested) dictionary corresponding to the subset
    d = df_to_nested_dict(mapping_subset)

    # save dictionary
    with open(path_to_json, 'w+') as json_file:
        json.dump(d, json_file)

    logging.info('Writing dictionary in : {}'.format(path_to_json))
    logging.info('Dictionary with data structure : {}'.format(d))
    return d


# Proteomic preprocessing
def preprocess_proteomic_data(df: pd.DataFrame, preprocess_params: dict) -> pd.DataFrame:
    for param in preprocess_params:
        len_df = len(df)
        if preprocess_params[param]["column_id"]:
            col = preprocess_params[param]["column_id"]

            if "to_discard" in preprocess_params[param]:
                values_to_discard = preprocess_params[param]["to_discard"]
                df = discard_values(df, values_to_discard, col)

            if "too_keep" in preprocess_params[param]:
                values_to_keep = preprocess_params[param]["to_keep"]
                df = keep_values(df, values_to_keep, col)

            if "unique" in preprocess_params[param]:
                unique = preprocess_params[param]["unique"]
                column_id = preprocess_params[param]["column_id"]
                df = df[df[column_id] == unique]

            else:
                logging.info('No values set for {} cutoff.'.format(param))

            proteins_kept = len_df - len(df)
            logging.info('Checking {}: {} proteins kept'.format(param, proteins_kept))

    return df


def discard_values(df: pd.DataFrame, values_to_discard: list, col: str):
    for value in values_to_discard:
        df = df[df[col] != value]
    return df


def keep_values(df: pd.DataFrame, values_to_keep, col: str):
    logical_filters = list()
    for value in values_to_keep:
        logical_filter = (df[col] == value)
        logical_filters.append(logical_filter)
    df = df[np.logical_or.reduce(logical_filters)]
    return df


def subset_df(df: pd.DataFrame, metadata_col: list, abundance_col_prefix: str) -> pd.DataFrame:
    """
    Inputs:
        - df: dataframe to subset
        - metadata_col: columns to keep (example: 'Accession', 'Description')
        - abundance_col_prefix: prefix present in each column with abundance values name

    Returns a data frame with only data columns and selected metadata columns
    """
    # filter relevant subset of df
    metadata_df = df.filter(metadata_col)
    values_df = df.filter(regex=abundance_col_prefix)

    # concatenate desired columns
    res = pd.concat([metadata_df, values_df], axis=1)
    return res


def clean_null_row(df: pd.DataFrame, abundance_col_prefix: str) -> pd.DataFrame:
    # get rows without a single value in abundances columns
    null_row = df.filter(regex=abundance_col_prefix).isnull().all(axis=1)

    # discard theses rows
    res = df[~null_row]
    return res
