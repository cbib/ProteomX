#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cedric Usureau, Aurélien Barré, Hayssam Soueidan


"""
Collection of functions used in quality check of data :
- missing values
"""

import pandas as pd
import re
import numpy as np
import collections
import json
from loguru import logger


def na_per_group(df: pd.DataFrame, list_group_prefix: list, values_cols_prefix: str):
    """
    Input : df with abundances values, list of string to select appropriate value columns per groups (list_group_prefix)
    and prefix used for data column (values_cols_prefix)
    The script creates one column per group containing % of missing value for each protein.
    Returns : the resulting columns as a dataframe (stats_per_groups), and input df augmented with the resulting columns
    """
    stats_per_groups = pd.DataFrame()

    for group in list_group_prefix:
        data = df.filter(regex=group)

        # strip prefix shared with all other groups
        prefix_to_remove = values_cols_prefix + '_'
        group_name = re.sub(prefix_to_remove, "", group)

        column_to_add_name = "nan_percentage_{}".format(group_name)

        # Add percentage of NaN in the data
        column_to_add_values = data.isna().sum(axis=1) / len(data.columns.tolist()) * 100
        kwargs = {column_to_add_name: column_to_add_values}
        df = df.assign(**kwargs)  # keyword in assign can't be an expression

        # Save results aside
        stats_per_groups = pd.concat([stats_per_groups, df[column_to_add_name]], axis=1)
    return df, stats_per_groups


def cv_per_group(df: pd.DataFrame, list_group_prefix: list, values_cols_prefix: str):
    """
    Input : df with abundances values, list of string to select appropriate value columns per groups (list_group_prefix)
    and prefix used for data column (values_cols_prefix)
    The script creates one column per group containing CV for each protein.
    Returns : the resulting columns as a dataframe (stats_per_groups), and input df augmented with the resulting columns
    """
    stats_per_groups = pd.DataFrame()

    for group in list_group_prefix:
        data = df.filter(regex=group)

        # strip prefix shared with all other groups
        prefix_to_remove = values_cols_prefix + '_'
        group_name = re.sub(prefix_to_remove, "", group)

        column_to_add_name = "CV_{}".format(group_name)

        # Compute CV
        column_to_add_values = np.nanstd(data, axis=1) / np.nanmean(data, axis=1)

        kwargs = {column_to_add_name: column_to_add_values}
        df = df.assign(**kwargs)  # keyword in assign can't be an expression

        # Save results aside
        stats_per_groups = pd.concat([stats_per_groups, df[column_to_add_name]], axis=1)
    return df, stats_per_groups


def flag_row_supp(df: pd.DataFrame, stats_per_groups: pd.DataFrame, threshold_value: int, name: str) -> pd.DataFrame:
    # Do we have more samples than the threshold (percentage)
    problematic_groups = pd.concat([stats_per_groups.loc[:, col] >= threshold_value
                                    for col in stats_per_groups.columns.tolist()], axis=1)

    logger.info("Problematic groups: ", problematic_groups)
    # Which one are ok in all groups
    to_keep = problematic_groups.sum(axis=1) == 0
    df['exclude_{}'.format(name)] = np.where(to_keep == True, 0, 1)

    return df


def flag_row_inf(df: pd.DataFrame, stats_per_groups: pd.DataFrame, threshold_value: int, name: str) -> pd.DataFrame:
    # Do we have more samples than the threshold (percentage)
    print('This function should work)')
    problematic_groups = pd.concat([stats_per_groups.loc[:, col] > threshold_value
                                    for col in stats_per_groups.columns.tolist()], axis=1)

    logger.info("Problematic groups: ", problematic_groups)

    # Which one are ok in all groups
    to_keep = problematic_groups.sum(axis=1) == 0

    df['exclude_{}'.format(name)] = np.where(to_keep == True, 0, 1)

    return df


def keep_specific_proteins_na(df, filter, name):
    """
    Assumption : only 2 conditions
    """
    # filter nan percentage info columns
    subset_df = df.filter(regex=filter)

    # create column to store info if protein is specific to one condition
    df['specific'] = 'both'

    # create mask : true if one of the condition has 100% missing values and the other none : specific strict
    mask = (subset_df == 100).any(axis=1) & (subset_df == 0).any(axis=1)

    # apply mask
    df['exclude_{}'.format(name)][mask] = 0
    df['specific'][mask] = 'specific'

    return df


def keep_specific_proteins_cv(df, filter, threshold):
    """
    Assumption : only 2 conditions
    """
    # filter info columns
    subset_df = df.filter(regex=filter)

    # create mask : true if one of the condition has 100% missing values and the other none : specific strict
    mask = (df['specific'] != 'both') & (subset_df < threshold).any(axis=1)

    # apply mask
    df['exclude_CV'][mask] = 0

    return df


def remove_flagged_rows(df: pd.DataFrame, col: str, exclude_code=1) -> pd.DataFrame:
    """ Remove rows based on specific value ('exclude_code') in specified column (col)"""
    res = df[df[col] != exclude_code]
    return res


def na_per_samples(df: pd.DataFrame, values_cols_prefix: str, max_na_sample_percentage: int):
    """
    Return dataframe with number and percentage of NaN per samples ; and boolean column with True if
    the sample has to be excluded
    """
    # select columns with samples data
    data = df.filter(regex=values_cols_prefix)

    # how many nans in each sample
    stats_per_sample = pd.DataFrame(data.isna().sum(axis=0), columns=['nan_number'])
    stats_per_sample['nan_percentage'] = stats_per_sample['nan_number'] / len(data) * 100

    # Do we have more samples than the threshold
    stats_per_sample['to_exclude'] = stats_per_sample['nan_percentage'] >= max_na_sample_percentage
    return stats_per_sample


def export_json_sample(stats_per_sample: pd.DataFrame, out: str, values_cols_prefix: str):
    """
        export_json_sample: create (future: update) json with stats on samples :
        1. 'nan_percentage' : percentage of NaN
        2. 'qc' : True if the sample NaN number is below the threshold
        3. 'user' (future) : True if the sample was selected by the user
    """

    # Strip prefix used for analysis in index name
    stats_per_sample = stats_per_sample.rename(index=lambda x: re.sub(str(values_cols_prefix + '_'), '', x))

    d = collections.defaultdict(dict)
    for sample in stats_per_sample.index.values:
        d[sample]["nan_percentage"] = stats_per_sample.loc[sample, "nan_percentage"]
        d[sample]["qc"] = bool(~stats_per_sample.loc[sample, "to_exclude"])

    with open(out, 'w+') as json_file:
        json.dump(d, json_file)
    return d


def remove_flagged_samples(df: pd.DataFrame, boolean_mask, rule_params) -> pd.DataFrame:
    """
    Input : df to filter, boolean mask to apply on samples columns, config dictionary
    Remove columns corresponding to flagged samples
    Returns a dataframe with only data columns and descriptive columns defined in the config file
    """
    metadata_col = rule_params['all']['metadata_col']
    metadata = df[metadata_col]
    data = df.filter(regex=rule_params['all']['values_cols_prefix'])

    res = data.loc[:, ~boolean_mask]
    return pd.concat([metadata, res, df['specific']], axis=1)
