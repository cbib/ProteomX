#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski

import collections
import json
import logging
import logging.config
import os
import pickle
import operator
from loguru import logger
import paths
import pandas as pd
import numpy as np


# TODO a réecrire


def autovivify(levels=1, final=dict):
    return (collections.defaultdict(final) if levels < 2 else
            collections.defaultdict(lambda: autovivify(levels - 1, final)))


# https://stackoverflow.com/questions/12734517/json-dumping-a-dict-throws-typeerror-keys-must-be-a-string
def stringify_keys(d):
    """Convert a dict's keys to strings if they are not."""
    for key in list(d):

        # check inner dict
        if isinstance(d[key], dict):
            value = stringify_keys(d[key])
        else:
            value = d[key]

        # convert nonstring to string if needed
        if not isinstance(key, str):
            try:
                d[str(key)] = value
            except Exception:
                try:
                    d[repr(key)] = value
                except Exception:
                    raise
            # delete old key
            del d[key]
    return d


# https://stackoverflow.com/questions/2235173/file-name-path-name-base-name-naming-standard-for-pieces-of-a-path
# TODO : harmoniser noms ?
def filename(file):
    basename = os.path.basename(file)
    stemname = os.path.splitext(basename)[0]
    return stemname


# https://python-guide-pt-br.readthedocs.io/fr/latest/writing/logging.html
# https://docs.python.org/3.6/howto/logging-cookbook.html
def get_logger(folder_id: str, rule: str):
    # create path string to log output
    path_to_log_file = os.path.join(paths.global_data_dir, folder_id, 'log/{}.log'.format(rule))

    # load logging configuration
    assert os.path.exists(paths.global_logging_config_file), "Couldn't logging config file"
    logging.config.fileConfig(paths.global_logging_config_file, defaults={'logfilename': path_to_log_file},
                              disable_existing_loggers=False)
    # create logger
    logger = logging.getLogger('main')
    return logger


# TODO: ugly function
# TODO: à généraliser
def get_ab_col(filename, subset, rule_params):
    path_to_mapping = rule_params["mapping"]["path_to_json_mapping"]
    with open(os.path.join(path_to_mapping, 'dict_file_{}.txt'.format(filename)), 'r') as dict_file:
        dict_mapping = json.load(dict_file)

    list_col = []
    for group in dict_mapping:
        for sample in dict_mapping[group]["samples"]:
            col_sample = dict_mapping[group]["samples"][sample]["col_id"]
            list_col.append(col_sample)
    if subset == "group":
        list_col = [item for sublist in list_col for item in sublist]

    return list_col


def load_json_parameter(file_id):
    path_to_json = os.path.join(paths.global_data_dir, file_id)
    with open(path_to_json + '/config_file.json') as f:
        parameters = json.load(f)
    return parameters


def load_txt_mapping(project, version, filename):
    path_to_json = os.path.join(paths.global_root_dir, paths.global_config_dir, project, version,
                                "dict_file_{}.txt".format(filename))
    with open(path_to_json) as f:
        parameters = json.load(f)
    return parameters


def load_json_data(file_id, filename, divide=False):
    if not divide:  # case when initial file is kept through all analysis step
        path_to_json = os.path.join(paths.global_data_dir, file_id, "metadata_{}.json".format(filename))
        with open(path_to_json) as f:
            data = json.load(f)
    elif divide:  # case when initial file contains more than 2 conditions and is split during the analysis
        initial_filename = filename.split('_')[0]
        path_to_json = os.path.join(paths.global_data_dir, file_id, "metadata_{}.json".format(initial_filename))
        with open(path_to_json) as f:
            data = json.load(f)
    return data


# see: https://stackoverflow.com/questions/19798112/convert-pandas-dataframe-to-a-nested-dict
def recur_dictify(dataframe):
    if len(dataframe.columns) == 1:
        if dataframe.values.size == 1: return dataframe.values[0][0]
        return dataframe.values.squeeze()
    grouped = dataframe.groupby(dataframe.columns[0])
    d = {k: recur_dictify(g.ix[:, 1:]) for k, g in grouped}
    return d


# https://stackoverflow.com/questions/8230315/how-to-json-serialize-sets
class PythonObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}


def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct


def dict_to_list(d, depth, col_name, list_col_prefix):
    for k, v in d.items():
        new_colname = col_name + '_' + str(k)
        list_col_prefix.append(new_colname)

        if isinstance(v, collections.Mapping):
            new_list_prefix = list_col_prefix
            dict_to_list(v, depth, new_colname, new_list_prefix)

        # else:
        # depth = 4
    list_prefix = [x for x in list_col_prefix if len(x.split('_')) == depth]

    return list_prefix


def export_result_to_csv(result_df, output_file, index_col=False):
    try:
        result_df.to_csv(output_file, index=False)
        logging.info('Writing in ' + output_file)

    except OSError:
        # create folder
        folder_name = os.path.dirname(output_file)
        os.makedirs(folder_name)

        # export file
        result_df.to_csv(output_file, index=index_col)
        logging.info('Creating directory : ' + os.path.dirname(output_file))
        logging.info('Writing in ' + output_file)

    except TypeError as e:
        logging.info('Error writing output file:  ' + str(e))
    return True


def create_mapping(headers: list, group1: str, group1_name: list, group2: str, group2_name: list) -> pd.DataFrame:
    """Input : header structure and 2 groups (name and list of samples for each one)
       Returns a dataframe for these groups with automatically assigned sample numbers"""
    if not len(headers) == 3:
        raise IndexError("Expected 3 column headers, got % s", headers)

    grp1_size = len(group1) + 1
    grp2_size = len(group2) + 1
    grp1 = list(zip([group1_name] * grp1_size, list(range(1, grp1_size)), group1))
    grp2 = list(zip([group2_name] * grp2_size, list(range(1, grp2_size)), group2))
    df1 = pd.DataFrame(grp1, columns=headers)
    df2 = pd.DataFrame(grp2, columns=headers)

    return pd.concat([df1, df2])


def create_mapping_from_csv_file(csv_file: str) -> pd.DataFrame:
    """
    Input : path to tab separated file with first column: group names, and second column : label of column with
    abundances values to analyse

    Output : data frame with one sample per line + name of input samples + arbitrary replicate numbering
    """

    mapping_info = pd.read_csv(csv_file, sep="\t", header=0, index_col=None)

    map = {'group': mapping_info.iloc[:,0],
           'sample': np.nan,
           'data_column': mapping_info.iloc[:,1]}

    res = pd.DataFrame(data = map)

    unique_group_df = res [~res .duplicated(subset=['group'], keep='first')]
    unique_group = unique_group_df['group'].tolist()

    group1_name = unique_group[0]
    group2_name = unique_group[1]
    group1_size = len(res[res['group'] == group1_name]) + 1
    group2_size = len(res[res['group'] == group2_name]) + 1

    group1_serie = pd.Series([i for i in range(1, group1_size)])
    group2_serie = pd.Series([i for i in range(1, group2_size)])

    sample_col = pd.concat([group1_serie, group2_serie], axis=0).reset_index(drop=True)
    res["sample"] = sample_col

    return res


def create_mapping_from_txt_file(txt_file: str) -> pd.DataFrame:
    """
    Input : path to tab separated file with first column: group names, and second column : label of column with
    abundances values to analyse

    Output : data frame with one sample per line + name of input samples + arbitrary replicate numbering
    """

    mapping_info = pd.read_csv(txt_file, sep="\t", header=0, index_col=None)

    map = {'group': mapping_info.iloc[:,0],
           'columns': mapping_info.iloc[:,1]}

    res = pd.DataFrame(data = map)
    unique_group_df = res [~res .duplicated(subset=['group'], keep='first')]
    unique_group = unique_group_df['group'].tolist()

    group1_name = unique_group[0]
    group2_name = unique_group[1]
    group1_size = len(res[res['group'] == unique_group[0]]) + 1
    group2_size = len(res[res['group'] == unique_group[1]]) + 1

    group1 = [f'{group1_name}_{i}' for i in range(1, group1_size)]
    group2 = [f'{group2_name}_{i}' for i in range(1, group2_size)]


    return res


def get_data_subset(df, values_cols_prefix, group_reference):
    numeric_data = df.filter(regex=values_cols_prefix)

    subset_reference = numeric_data.loc[:, numeric_data.columns.str.contains(group_reference)]
    subset_condition = numeric_data.loc[:, ~numeric_data.columns.str.contains(group_reference)]

    df_list = list([subset_reference, subset_condition])

    return df_list


def path_to_analysis(unique_id):
    path_analysis = os.path.join(paths.global_data_dir, unique_id)
    return path_analysis


def subset_data(df: pd.DataFrame, subset_filters) -> dict:
    """
    Inputs:
        - df:
        - subset_filters: dictionary with the filters to apply for each subset to create : columns on which to apply
        filters, threshold and operator to use

    Returns:
        A dictionary with subset names as key and filtered data frame as values

    Example:
        df = pd.DataFrame(np.array([[1, 2, 3], [4, 10, 6], [5, 8, 9]]), columns=['a', 'b', 'c'])
        subset_filters=
            {"subset1":
                {"column": ["a", "b"],
                "threshold": [2, 5],
                "mode": ["inferior", "superior"]},
            "subset2":
                {"column": ["b"],
                "threshold": [4],
                "mode": ["superior"]}

        res =
            {"subset1":
    """
    # look-up table for criteria in config file
    ops = {"<": operator.lt,
           "<=": operator.le,
           ">": operator.gt,
           ">=": operator.ge,
           "!=": operator.ne,
           "==": operator.eq,
           }

    # create a dictionary storing the name of the subset and the associated dataframe
    res = autovivify(levels=2, final=dict)

    # check all filters for one subset
    for subset in subset_filters:
        logging.info("Subset: {}".format(subset))
        filtered_df = df.copy()

        for col, threshold, op in zip(*subset_filters[subset].values()):
            logger.info("column: {}".format(col))
            logger.info("threshold: {}".format(threshold))
            logger.info("operator: {}".format(op))

            # keep row compliant with filters
            filtered_df = filtered_df[ops[op](filtered_df[col], threshold)]

        # store results
        res[subset] = filtered_df

    return res


def remove_absent_groups(df: pd.DataFrame, groups_list: list, values_cols_prefix: str) -> list:
    ab_df = df.filter(regex=values_cols_prefix)

    groups_to_remove = list()
    for group in groups_list:
        ab_subset = ab_df.filter(regex=group)
        if ab_subset.empty:
            groups_to_remove.append(group)

    filtered_groups_list = [g for g in groups_list if g not in groups_to_remove]
    return filtered_groups_list
