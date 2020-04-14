#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Plot boxplot for each protein and group
"""


import argparse
import pandas as pd
import numpy as np
import helpers as h
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sklearn.preprocessing


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (without extension)')
    parser.add_argument("--list", "-l", help='List of specific proteins to plot')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')

    args = parser.parse_args()
    return args


def get_plot_numbers(df, rule_params):
    numb_plot = rule_params['boxplot_abundances']['nb_plot']
    prot_per_plot = rule_params['boxplot_abundances']['protein_per_plot']

    if numb_plot:
        prot_per_plot = len(df) / rule_params['boxplot_abundances']['nb_plot']

    elif prot_per_plot:
        numb_plot = len(df) / rule_params['boxplot_abundances']['protein_per_plot']

    else:
        prot_per_plot = 10
        numb_plot = len(df) / prot_per_plot

    return numb_plot, prot_per_plot


def plot_boxplots(df, rule_params, xlabel, ylabel, palette):
    numeric_data = df.filter(regex=rule_params['all']['values_cols_prefix'])
    max_value = numeric_data.max().max()

    numb_plot, prot_per_plot = get_plot_numbers(df, rule_params)

    for n_plot in np.arange(0,numb_plot):

        protein_for_plot = df.loc[prot_per_plot * n_plot : prot_per_plot * n_plot + (prot_per_plot-1)]

        sub_df = pd.DataFrame(columns=[xlabel, ylabel, 'group'])
        j = 0

        for i in protein_for_plot.index.values:
            if rule_params['boxplot_abundances']['id_is_numeric']:
                protein = "CP-" + str(protein_for_plot.loc[i, rule_params['all']['id_col']])
            else:
                protein = str(protein_for_plot.loc[i, rule_params['all']['id_col']])
            for column in numeric_data.columns.values:
                value = protein_for_plot.loc[i, column]

                group='no group'
                for cond_name in rule_params['boxplot_abundances']['subset']:
                    if cond_name in column:
                        if not rule_params['boxplot_abundances']['subset_name']:
                            group = cond_name
                        else:
                            group = rule_params['boxplot_abundances']['subset_name'][cond_name]

                sub_df.loc[j] = [protein, value, group]
                j = j + 1
            sub_df = sub_df[sub_df['group'] != 'no group']

            produce_boxplot(sub_df, xlabel, ylabel, max_value, n_plot, palette)


def produce_boxplot(df, xlabel, ylabel, max_value, n_plot, palette='muted'):

    sns.set_style('ticks')
    fig, ax = plt.subplots()

    # the size of A4 paper
    fig.set_size_inches(11.7, 8.27)


    if rule_params["boxplot_abundances"]["stripplot"]:
        sns.stripplot(x=xlabel, y=ylabel, data=df, hue='group', palette= ["black"], split=True)
    sns.boxplot(x=xlabel, y=ylabel, data=df, hue='group', palette = palette)

    # Get the handles and labels. For this example it'll be 2 tuples
    # of length 4 each.
    handles, labels = ax.get_legend_handles_labels()

    # When creating the legend, only use the first two elements
    # to effectively remove the last two.
    plt.legend(handles[0:2], labels[0:2])

    sns.set_context("paper", font_scale=1.6)
    plt.xticks(rotation=0)

    # plot line between protein boxplot to help comprehension
    for i in range(len(df[xlabel].unique()) - 1):
       plt.vlines(i + .5, 0, 45, linestyles='solid', colors='gray', alpha=0.2)

    #plt.ylim(top = max_value, bottom=0)
    plt.ylim(top=max_value, bottom=0)
    #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
    plt.tight_layout()
    plt.savefig(args.output_file + '_' + str(n_plot) + ".png")
    sns.set_style('ticks')

    plt.close()


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.project, args.version)
    filename = h.filename(args.input_file)

    logpath = os.path.join(rule_params['all']['logpath'], 'overlap.log')
    logger = h.get_logger(logpath)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)
    id_col = rule_params['all']['id_col']

    if args.list:
        list_to_plot = pd.read_csv(args.list, header=None)

        data_df = data_df[data_df[id_col].isin(list_to_plot[0])]

    if rule_params['boxplot_abundances']['sort_by']:

        data_df.sort_values(by=rule_params['boxplot_abundances']['sort_by'], axis=0, inplace=True)

    if rule_params['boxplot_abundances']['top']:
        top = rule_params['boxplot_abundances']['top']
        data_df = data_df.iloc[0:top, 0:len(data_df)]

    data_df.reset_index(inplace=True, drop=True)

    if rule_params['boxplot_abundances']['reduce']:
        values_to_scale = data_df.filter(regex=rule_params['all']['values_cols_prefix'])

        colnames = values_to_scale.columns
        values_scaled = pd.DataFrame(sklearn.preprocessing.scale(values_to_scale,
                                                                 axis=1,
                                                                 with_mean=False),
                                     columns=colnames)
        data_df = pd.concat([data_df[id_col], values_scaled], axis=1)
    else:
        values = data_df.filter(regex=rule_params['all']['values_cols_prefix'])
        data_df = pd.concat([data_df[id_col], values], axis=1)

    xlabel = rule_params['boxplot_abundances']['xlabel']
    ylabel = rule_params['boxplot_abundances']['ylabel']
    palette = rule_params['boxplot_abundances']['palette']
    plot_boxplots(data_df, rule_params, xlabel, ylabel, palette)

    # check data scaling
    # print(data_df.head())
    # print(data_df.std(axis=1))
    # print(data_df.mean(axis=1))
    # print(data_df.iloc[1].values[1:])
    # print(np.std(data_df.iloc[1].values[1:]))
    # print(data_df.iloc[1].values[1:].mean())