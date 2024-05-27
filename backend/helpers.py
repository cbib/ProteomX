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
import functools


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
# TODO : looging.conf hardcoded
def get_logger(logfilename):
    assert os.path.exists(paths.global_logging_config_file), "Couldn't logging config file"
    logging.config.fileConfig(paths.global_logging_config_file, defaults={'logfilename': logfilename},
                              disable_existing_loggers=False)
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
        if isinstance(v, collections.abc.Mapping):
            new_list_prefix = list_col_prefix
            dict_to_list(v, depth, new_colname, new_list_prefix)
    list_prefix = [x for x in list_col_prefix if len(x.split('_')) == depth]

    return list_prefix


def export_result_to_csv(result_df, output_file, index=False):
    try:

        result_df.to_csv(output_file, index=index)
        logging.info('Writing  ' + str(len(result_df)) + ' proteins ')
        logging.info('Writing in ' + output_file)

    except OSError as e:
        logging.info('OSError writing output file:  ' + str(e))
    #     os.makedirs(output_file, exist_ok=True)
    #     result_df.to_csv(output_file, index=False)
    #     logging.info('Creating directory : ' + os.path.dirname(output_file))
    #     logging.info('Writing in ' + output_file)
    #
    except TypeError as e:
         logging.info('TypeError writing output file:  ' + str(e))
    return True


def create_mapping(headers: list, group1: str, group1_name: list, group2: str, group2_name: list) -> pd.DataFrame:
    '''Input : header structure and 2 groups (name and list of samples for each one)
       Returns a dataframe for these groups with automatically assigned sample numbers'''
    if not len(headers) == 3:
        raise IndexError("Expected 3 column headers, got % s", headers)

    grp1_size = len(group1) + 1
    grp2_size = len(group2) + 1
    grp1 = list(zip([group1_name] * grp1_size, list(range(1, grp1_size)), group1))
    grp2 = list(zip([group2_name] * grp2_size, list(range(1, grp2_size)), group2))
    df1 = pd.DataFrame(grp1, columns=headers)
    df2 = pd.DataFrame(grp2, columns=headers)

    return pd.concat([df1, df2])


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
    # look-up table for operators in config file
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
        logger.info("Subset: {}".format(subset))
        filtered_df = df.copy()
        for col, threshold, op in zip(*subset_filters[subset].values()):
            filtered_df.dropna(subset=[col], inplace=True)
            # Remove "--" values for pvalue and padj (came from scipy ttest_ind)
            filtered_df = filtered_df[filtered_df.pvalue != "--"]
            logger.info("column: {}".format(col))
            logger.info("threshold: {}".format(threshold))
            logger.info("operator: {}".format(op))

            if col != "specific":
                filtered_df = filtered_df.astype({col: 'float64'})
            dataTypeSeries = filtered_df.dtypes
            # keep row compliant with filters
            filtered_df = filtered_df[ops[op](filtered_df[col], threshold)]

        # store results
        res[subset] = filtered_df

    return res


def remove_absent_groups(df: pd.DataFrame, groups_list: list, values_cols_prefix: str) -> list:
    ab_df = df.filter(regex=values_cols_prefix)
    groups_to_remove = list()
    for group in groups_list:
        ab_subset = ab_df.filter(regex='{}_'.format(group), axis=1)
        if ab_subset.empty:
            groups_to_remove.append(group)

    filtered_groups_list = [g for g in groups_list if g not in groups_to_remove]
    return filtered_groups_list


def list_files_in_directory(directory, requirement=False):
    '''
    input:
        directory : directory where files will be listed. No recursive search
        stemname_only : return complete path (if False) or only stem name (file name without extension and dirname)
        requirement : str to find in the path
    '''

    files_list = [os.path.join(directory, f) for f in os.listdir(directory) if
                  os.path.isfile(os.path.join(directory, f))]

    # ignore hidden files
    files_list = [f for f in files_list if not filename(f).startswith('.')]
    # add constraint ?
    if requirement:
        if isinstance(requirement, str):
            files_list = [f for f in files_list if requirement in f]
        elif isinstance(requirement, list):
            files_list = [f for f in files_list if all(r in f for r in requirement if r != None)]
    return files_list


def list_files_in_directory_complete(directory_to_list, stemname_only=False, requirement_pos=False,
                                     requirement_neg=False):
    '''
     input:
         directory : directory where files will be listed. No recursive search
        stemname_only : return complete path (if False) or only stem name (file name without extension and dirname)
        requirement_pos : str to find in the path
        requirement_neg : str to not find in the path
     '''

    files_list = [os.path.join(directory_to_list, f) for f in os.listdir(directory_to_list) if
                  os.path.isfile(os.path.join(directory_to_list, f))]

    # ignore hidden files
    files_list = [f for f in files_list if not filename(f).startswith('.')]

    # add constraint ?
    if requirement_pos:
        if isinstance(requirement_pos, str):
            files_list = [f for f in files_list if requirement_pos in f]
        elif isinstance(requirement_pos, list):
            files_list = [f for f in files_list if all(r in f for r in requirement_pos)]

    if requirement_neg:
        if isinstance(requirement_neg, str):
            files_list = [f for f in files_list if requirement_neg not in f]
        elif isinstance(requirement_neg, list):
            files_list = [f for f in files_list if all(r not in f for r in requirement_neg)]
            
    if stemname_only:
        files_list = [ filename(f) for f in files_list]
    return files_list

def merge_dataframes(*args, on:str, how:str) -> pd.DataFrame:
    res = functools.reduce(lambda left,right: pd.merge(left,right,on=on, how=how), args)
    return res
