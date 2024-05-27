#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Compare two groups in file, add information on protein present in only one of the two groups
To do AFTER missing values control == à faire avec ? même analyses == à fire après mais en reprenant fonctions utilisées
"""

import argparse
import logging.config
import pandas as pd
import os
import helpers as h
import paths
import numpy as np
import matplotlib_venn as mv
import matplotlib.pyplot as plt
import re
import json
import matplotlib
matplotlib.use('Agg')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--json_names", "-j", help='Optional: provide more suitable name for plot')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--output_figure", "-of", help='Path for Venn diagram')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def get_groups(data_structure, values_cols_prefix):
    """
    Returns list of strings that describe the beginning of values column to select.
        Example: ['VAL_Patient', 'VAL_Control']
    # TODO : move to helpers.py
    """

    # +1 for all data columns prefix (ex: 'VAL')
    depth = len(rule_params['set_comparison']['on']) + 1
    list_group_prefix = h.dict_to_list(data_structure, depth, values_cols_prefix, [])

    return list_group_prefix


def remove_absent_groups(df, groups_list, values_cols_prefix):
    ab_df = df.filter(regex=values_cols_prefix)

    groups_to_remove = list()
    for group in groups_list:
        ab_subset = ab_df.filter(regex='{}_'.format(group), axis=1)
        if ab_subset.empty:
            groups_to_remove.append(group)

    filtered_groups_list = [g for g in groups_list if g not in groups_to_remove]
    return filtered_groups_list


def get_protein_repartition(df: pd.DataFrame, id_col: str, groups: list) -> tuple:
    # Idée : checker df et retourne une colonne avec "group1", "group2" (as defined in mapping) or "both"
    # deuxième façon de faire : retourne une colonne pour chaque groupe avec code si présent ou non ?
    # parait plus lourd mais plus adaptable si ngroup > 1
    # Deuxieme question: est ce que les informations ont besoin d'être présentes sur le df ?  ou juste cuisine interne
    # Si ngroup = 2, résultat doit être sauvegardé
    # Si ngroups > 2, que va t-on faire de cette information ? Pour visualisation, pas besoin de conserver ; pour
    # analyse, à faire uniquement après divide

    stats_per_groups = df[id_col]

    for group in groups:
        data = df.filter(regex='{}_'.format(group), axis=1)

        column_to_add_name = 'All_nan_{}'.format(group)
        column_to_add_values = data.isna().all(axis=1)

        kwargs = {column_to_add_name: column_to_add_values}

        # Save results
        # stats_per_groups.join(pd.DataFrame(kwargs))
        df = df.assign(**kwargs)  # keyword in assign can't be an expression

        # Save results aside
        stats_per_groups = pd.concat([stats_per_groups, df[column_to_add_name]], axis=1)
    return df, stats_per_groups


def add_column_overview(stats, groups):
    # Which one are ok in both groups
    conditions = [
        (stats["All_nan_{}".format(groups[0])] == True) & (stats["All_nan_{}".format(groups[1])] == False),
        (stats["All_nan_{}".format(groups[0])] == False) & (stats["All_nan_{}".format(groups[1])] == True),
        (stats["All_nan_{}".format(groups[0])] == False) & (stats["All_nan_{}".format(groups[1])] == False)
    ]

    choices = [groups[1], groups[0], "both"]
    # TODO: add column name in the config file
    stats['specific_sc'] = np.select(conditions, choices)
    return stats


def prepare_data_for_venn(stats, groups):
    specific_proteins_g1 = stats[stats["specific_sc"] == groups[0]][id_col].tolist()
    specific_proteins_g2 = stats[stats["specific_sc"] == groups[1]][id_col].tolist()

    ubiquitous_proteins = stats[stats["specific_sc"] == "both"][id_col].tolist()

    proteins_g1 = set(specific_proteins_g1 + ubiquitous_proteins)
    proteins_g2 = set(specific_proteins_g2 + ubiquitous_proteins)
    values = [proteins_g1, proteins_g2]
    names = [re.sub(str(values_col_prefix + '_'), "", g) for g in groups]

    plot_subtitle = ' vs. '.join(names)
    plot_subtitle = re.sub(" vs. $", "", plot_subtitle)

    if args.json_names:
        path_to_json = args.json_names
        with open(path_to_json) as f:
            look_up_table = json.load(f)

        names_user = [look_up_table[n] for n in names]
        plot_subtitle_user = look_up_table[plot_subtitle]
    else:
        names_user = names
        plot_subtitle_user = plot_subtitle
    return values, names_user, plot_subtitle_user


def plot_venn_diagram(stats: pd.DataFrame, groups):
    values, names, plot_subtitle = prepare_data_for_venn(stats, groups)
    colors = rule_params['set_comparison']['venn_colors']
    plt.rc('font', size=15)
    mv.venn2_unweighted(values, names, set_colors=colors)
    plt.suptitle(plot_subtitle, fontsize=16)
    plt.tight_layout()
    plt.savefig(args.output_figure)
    plt.close()
    return


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)
    filename = h.filename(args.input_file)
    data_structure = h.load_json_data(args.file_id, filename, rule_params['all']['divide'])

    logpath = os.path.join(paths.global_data_dir, args.file_id, 'log/set_comparison.log')
    logger = h.get_logger(logpath)
    logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)


    id_col = rule_params["all"]["id_col"]
    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    values_col_prefix = rule_params['all']['values_cols_prefix']
    if type(data_structure) is dict:
        groups = get_groups(data_structure, values_col_prefix)
    elif type(data_structure) is list:
        groups = [str(values_col_prefix + '_' + g) for g in data_structure]

    if rule_params['all']['divide']:
        groups = remove_absent_groups(data_df, groups, values_col_prefix)

    res, stats_per_group = get_protein_repartition(data_df, id_col, groups)
    stats_per_group = add_column_overview(stats_per_group, groups)

    if rule_params["set_comparison"]["plot"]:
        plot_venn_diagram(stats_per_group, groups)

    if rule_params["set_comparison"]["add_result_to_csv"]:
        res = res.merge(stats_per_group[[id_col, 'specific_sc']], on=id_col, how="left")

    # TODO
    h.export_result_to_csv(data_df, args.output_file)
