#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski

import collections
import os
import logging
import logging.config
import json
import pickle
import paths
import pandas as pd


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
    logging.config.fileConfig('logging.conf', defaults={'logfilename': logfilename}, disable_existing_loggers=False)
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


def load_json_parameter(project, version):
    path_to_json = os.path.join(paths.global_root_dir, paths.global_config_dir, project, version)
    with open(path_to_json + '/config_file.json') as f:
        parameters = json.load(f)
    return parameters


def load_txt_mapping(project, version, filename):
    path_to_json = os.path.join(paths.global_root_dir, paths.global_config_dir, project, version, "dict_file_{}.txt".format(filename))
    with open(path_to_json ) as f:
        parameters = json.load(f)
    return parameters


def load_json_data(project, version, filename):
    path_to_json = os.path.join(paths.global_root_dir, paths.global_data_dir, project, version, "mapping/samples_json", "{}.json".format(filename))
    with open(path_to_json ) as f:
        data = json.load(f)
    return data


# see: https://stackoverflow.com/questions/19798112/convert-pandas-dataframe-to-a-nested-dict
def recur_dictify(dataframe):
    if len(dataframe.columns) == 1:
        if dataframe.values.size == 1: return dataframe.values[0][0]
        return dataframe.values.squeeze()
    grouped = dataframe.groupby(dataframe.columns[0])
    d = {k: recur_dictify(g.ix[:,1:]) for k,g in grouped}
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
        else:
            depth = 4
    list_prefix = [x for x in list_col_prefix if len(x.split('_')) == depth]
    return list_prefix


def export_result_to_csv(result_df, output_file):
    try:
        result_df.to_csv(output_file, index=False)
        logging.info('Writing in ' + output_file)

    except OSError:
        os.makedirs(output_file)
        result_df.to_csv(output_file, index=False)
        logging.info('Creating directory : ' + os.path.dirname(output_file))
        logging.info('Writing in ' + output_file)

    except TypeError as e:
        logging.info('Error writing output file:  ' + str(e))
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
