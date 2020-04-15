#!/usr/bin/env python

import warnings
import pandas as pd
import numpy as np
import os
import matplotlib_venn as mv
import sys
import logging
import pandas.errors as err
from collections import defaultdict
import argparse
import xlrd
import statsmodels.stats.multitest as smm
from scipy import stats
from scipy.stats.distributions import norm
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn import preprocessing
import math
import interval
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import ks_2samp
from scipy.stats import mannwhitneyu
import itertools
import re
import json
from matplotlib_venn import venn2
from scipy.stats.mstats import gmean
import scipy.stats as st
from matplotlib.colors import Normalize
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from functools import reduce
import subprocess
import pandas.errors as err
from locale import atof
from collections import defaultdict
import argparse
import xlrd
import matplotlib
import matplotlib.ticker as ticker
import gseapy as gp
from gseapy.plot import barplot, dotplot
import csv
import six
from numpy import genfromtxt
from collections import defaultdict
from collections import Counter
import argparse
import itertools
import scipy.stats as stats
import seaborn as sns
import locale
from locale import atof
import math
import matplotlib.ticker as ticker
import plotly
from plotly.graph_objs import *
import plotly.tools as tls
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import pdist,squareform
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
import logging, sys, operator

from matplotlib.colors import Normalize
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from gseapy.parser import unique
from matplotlib.ticker import FormatStrFormatter
from collections import Counter
import fnmatch





class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


def check_dir(output_dir):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)


def get_filename(input_file):
    filename, file_extension = os.path.splitext(input_file)
    filename = filename.split("/")[len(filename.split("/")) - 1]
    return filename


def get_filepath(input_file):
    file_name, file_extension = os.path.splitext(input_file)
    filename = file_name.split("/")[len(file_name.split("/")) - 1]
    file_path=file_name.split("/"+filename)[0]
    return file_path

def get_logpath(input_file):
    file_name, file_extension = os.path.splitext(input_file)
    logpath= file_name.split("/")[0]+'/'+file_name.split("/")[1]+'/log'
    return logpath

def get_duplicated_path(input_file):
    file_name, file_extension = os.path.splitext(input_file)
    duppath= file_name.split("/")[0]+'/'+file_name.split("/")[1]+'/duplicated/'
    return duppath


def listpath_nohidden(path):
    return glob.glob(os.path.join(path, '*'))

def listdir_nohidden(path):
    list_files = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            list_files.append(f)
    return(list_files)


def read_csv_file(csv_file,filetype,sep=",",index_col=None,header=0):
    # type: (object, object, object, object, object) -> object
    try:
        df = pd.read_csv(csv_file, sep=sep,index_col=index_col,header=header, engine='python')
        logging.info(' Reading ' + csv_file + '...')
        return df
    except (ValueError, IOError, err.ParserError, err.EmptyDataError) as e:
        print(filetype, " error: ", e)
        exit(1)


def read_excel_file(excel_file,filetype, skiprows=0, index_col=None):
    try:
        df = pd.read_excel(excel_file, skiprows=skiprows,index_col=index_col)
        logging.info(' Reading ' + excel_file + '...')

        return df
    except (ValueError, IOError, err.ParserError, err.EmptyDataError,xlrd.biffh.XLRDError) as e:
        print(filetype, " error: ", e)
        exit(1)


def autovivify(levels=1, final=dict):
    return (defaultdict(final) if levels < 2 else
    defaultdict(lambda: autovivify(levels - 1, final)))


def build_meta_mapping_dict(mapping_df):
    column_groups = autovivify(3, list)
    for i in mapping_df.index.values:
        group = mapping_df.loc[i][0]
        replicates = mapping_df.loc[i][1]
        sample = mapping_df.loc[i][2]
        meta = mapping_df.loc[i][3]
        column_groups[group][replicates][meta].append(sample)
    return column_groups


def build_mapping_dict(mapping_df):
    column_groups = autovivify(2, list)
    for i in mapping_df.index.values:
        group = mapping_df.loc[i][0]
        replicates = mapping_df.loc[i][1]
        sample = mapping_df.loc[i][2]
        column_groups[group][replicates].append(sample)
    return column_groups


def build_header_mapping_dict(mapping_df, columns):
    column_groups = autovivify(3, list)
    for i in mapping_df.index.values:
        if  mapping_df.loc[i][5] in columns:
            group = mapping_df.loc[i][0]
            sample = mapping_df.loc[i][1]
            replicate = mapping_df.loc[i][3]
            original_label = mapping_df.loc[i][5]
            column_groups[group][sample][replicate].append(original_label)
    return column_groups


#chiné sur https://stackoverflow.com/questions/12734517/json-dumping-a-dict-throws-typeerror-keys-must-be-a-string
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

#######################################
def build_mapping(mapping_df, input_df, filename):
    column_groups = autovivify(3, list)
    id_columns_dict = defaultdict(list)
    print(mapping_df)
    for i in mapping_df.index.values:
        #create a dictionnary with the mapping info
        #... = ....['sample'] throw error e1
        group = mapping_df.loc[i][0]
        sample = mapping_df.loc[i][1]
        replicate = mapping_df.loc[i][2]
        condition = mapping_df.loc[i][4]
        column_groups[group][sample][replicate].append(condition)

        #create a dictionnary with unique id for each abundance column
        unique_id = 'GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)
        label = mapping_df.loc[i][5]

        id_columns_dict.update({label: unique_id})
    print(column_groups)
    #save dictionnary for further use
    column_groups = stringify_keys(column_groups)
    with open('./dict_files/dict_file_{}.txt'.format(filename), 'w+') as dict_file:
        json.dump(column_groups, dict_file)
    return input_df.rename(columns=id_columns_dict)



def build_group_sample_mapping_dict(mapping_df, columns):
    column_groups = autovivify(2, list)
    for i in mapping_df.index.values:
        if  mapping_df.loc[i][5] in columns:
            condition = mapping_df.loc[i][0]
            replicates = mapping_df.loc[i][1]
            sample = mapping_df.loc[i][5]
            column_groups[condition][replicates].append(sample)
    return column_groups


def build_sample_mapping_dict(mapping_df, columns):
    column_groups = autovivify(2, list)
    for i in mapping_df.index.values:
        if  mapping_df.loc[i][5] in columns:
            condition = mapping_df.loc[i][1]
            replicates = mapping_df.loc[i][2]
            sample = mapping_df.loc[i][5]
            column_groups[condition][replicates].append(sample)
    return column_groups

def build_sample_label_mapping_dict(mapping_df, columns):
    column_groups = autovivify(2, list)
    for i in mapping_df.index.values:
        if  mapping_df.loc[i][5] in columns:
            condition = mapping_df.loc[i][6]
            replicates = mapping_df.loc[i][2]
            sample = mapping_df.loc[i][5]
            column_groups[condition][replicates].append(sample)
    return column_groups


def build_condition_mapping_dict(mapping_df, columns):
    column_groups = autovivify(2, list)
    for i in mapping_df.index.values:
        if  mapping_df.loc[i][5] in columns:
            condition = mapping_df.loc[i][4]
            replicates = mapping_df.loc[i][3]
            sample = mapping_df.loc[i][5]
            column_groups[condition][replicates].append(sample)
    return column_groups

def build_not_paired_condition_mapping_dict(mapping_df, columns):
    column_groups = autovivify(2, list)
    for i in mapping_df.index.values:
        if  mapping_df.loc[i][5] in columns:
            condition = mapping_df.loc[i][4]
            replicates = mapping_df.loc[i][2]
            sample = mapping_df.loc[i][5]
            column_groups[condition][replicates].append(sample)
    return column_groups


def build_group_mapping_dict(mapping_df, columns):
    column_groups = autovivify(2, list)
    for i in mapping_df.index.values:
        if  mapping_df.loc[i][5] in columns:
            group = mapping_df.loc[i][0]
            replicates = mapping_df.loc[i][2]
            sample = mapping_df.loc[i][5]
            column_groups[group][replicates].append(sample)
    return column_groups


def get_group_col_index(group_dict):
    col = []
    for replicate in list(group_dict.keys()):
        col.append(group_dict[replicate][0])
    idx = [x for x in col]
    return idx


def compute_reduce_df(input_df, mapping_df, ignored_columns=2):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_mapping_dict(mapping_df)
    reduced_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    for protein in all_abundances.index.values:
        for group in all_groups:
            col_idx = get_group_col_index(column_groups[group])
            #print(protein, np.array(all_abundances.loc[protein][col_idx]))
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            # here reduce abundancies by std for given group
            # if np.nanstd(abundancies)==0:
            #     print(abundancies)
            reduced_abundancies = abundancies / np.nanstd(abundancies)
            reduced_df.loc[protein][col_idx] = reduced_abundancies

    return reduced_df


def compute_all_condition_reduce_df(input_df, mapping_df, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    #print(all_abundances)
    column_groups = build_condition_mapping_dict(mapping_df,abundancies_cols)
    print(column_groups)
    reduced_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    print(all_groups)
    #sys.exit()
    for protein in all_abundances.index.values:
        col_idx=[]
        for group in all_groups:
            col_idx += get_group_col_index(column_groups[group])
        print(col_idx)
        abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        print(abundancies)
            # here reduce abundancies by std for given group
        reduced_abundancies = abundancies / np.nanstd(abundancies)
        reduced_df.loc[protein][col_idx] = reduced_abundancies
    #print(reduced_df)
    return reduced_df

def compute_all_group_center_reduce_df(input_df, mapping_df, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)
    reduced_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    for protein in all_abundances.index.values:
        col_idx=[]
        for group in all_groups:
            col_idx += get_group_col_index(column_groups[group])

        abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            # here reduce abundancies by std for given group
        reduced_abundancies = (abundancies - np.nanmean(abundancies))/ np.nanstd(abundancies)

        reduced_df.loc[protein][col_idx] = reduced_abundancies
    return reduced_df


def compute_all_group_reduce_df(input_df, mapping_df, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)
    reduced_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    for protein in all_abundances.index.values:
        print(protein)
        col_idx=[]
        for group in all_groups:
            col_idx += get_group_col_index(column_groups[group])

        abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            # here reduce abundancies by std for given group
        reduced_abundancies = abundancies / np.nanstd(abundancies)

        reduced_df.loc[protein][col_idx] = reduced_abundancies
    return reduced_df





def compute_all_group_scale_df(input_df, mapping_df, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    reduced_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)

    X_train = np.array(all_abundances)
    #X_scaled = preprocessing.scale(X_train)
    #reduced_df[:][abundancies_cols] = X_scaled

    min_max_scaler = preprocessing.MinMaxScaler()
    X_train_minmax = min_max_scaler.fit_transform(X_train)
    reduced_df[:][abundancies_cols]=X_train_minmax


    print(reduced_df)
    return reduced_df


def compute_all_sample_reduce_df(input_df, mapping_df, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_sample_mapping_dict(mapping_df,abundancies_cols)
    print(column_groups)

    reduced_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    print(all_groups)
    for protein in all_abundances.index.values:
        #print(protein)
        col_idx=[]
        ratios=[]
        for group in all_groups:
            #print(group)

            col_idx += get_group_col_index(column_groups[group])
            ratios.append(np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x)))
        # plt.figure()
        # plt.boxplot([ratios[0], ratios[1]])
        # plt.scatter([1 for x in ratios[0]], ratios[0])
        # plt.scatter([2 for x in ratios[1]], ratios[1])
        # plt.xticks(np.arange(1, 3, step=1))
        # plt.xticks(np.arange(1, 3), ("Mutated", "Non mutated"))
        # plt.ylabel("normalized expression")
        # plt.scatter(1, np.median(ratios[0]), color="black")
        # plt.scatter(2, np.median(ratios[1]), color="black")
        # plt.savefig("test.png")
            #print(column_groups[group])
        #print(col_idx)

        abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            # here reduce abundancies by std for given group
        #reduced_abundancies = (abundancies - np.nanmean(abundancies))/ np.nanstd(abundancies)
        reduced_abundancies = abundancies / np.nanstd(abundancies)

        reduced_df.loc[protein][col_idx] = reduced_abundancies
    return reduced_df


def compute_group_reduce_df(input_df, mapping_df, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)
    reduced_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    for protein in all_abundances.index.values:
        col_idx=[]
        for group in all_groups:
            col_idx += get_group_col_index(column_groups[group])
        abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            # here reduce abundancies by std for given group
        reduced_abundancies = abundancies / np.nanstd(abundancies)
        reduced_df.loc[protein][col_idx] = reduced_abundancies

    return reduced_df


def annotate_using_existing(input_df,annot_col,species=None):
    for i, row in input_df.iterrows():
        if species != None:

            if str(row[annot_col]) != "nan" and "GN" in str(row[annot_col]) and "Fragment" not in str(row[annot_col]) and species in str(row[annot_col]): # and "Uncharacterized" not in str(row[annot_col]):
                try:
                    input_df.loc[i, 'gene_name'] = str(row[annot_col].split("GN=")[1].split(" ")[0])
                except KeyError as e:
                    print(e)
        else:
            if str(row[annot_col]) != "nan" and "GN" in str(row[annot_col]) and "Fragment" not in str(row[annot_col]):
                try:
                    input_df.loc[i, 'gene_name'] = str(row[annot_col].split("GN=")[1].split(" ")[0])
                except KeyError as e:
                    print(e)
    return input_df


def annotate_using_annotation_files(input_df, swiss_annot_file,trembl_annot_file,annot_col,species=None):
    s_annot_df = read_csv_file(swiss_annot_file, "swiss prot annotation file", index_col=0, header=0)
    #print(s_annot_df)
    t_annot_df = read_csv_file(trembl_annot_file, "Trembl annotation file", index_col=0, header=0)
    t_annot_df=t_annot_df.dropna()
    s_annot_df=s_annot_df.dropna()
    gene_names=[]
    for i, row in input_df.iterrows():
        accession_ids = row['Accession'].split(";")
        if species != None:
            if "Fragment" not in str(row[annot_col]) and species in str(row[annot_col]):
                #print(i)
                if accession_ids[0] in s_annot_df.index.values:
                    gn = s_annot_df.ix[accession_ids[0]]["Gene name"]
                    if not type(gn) is str:
                        for g in gn:
                            gn = g
                            break
                    input_df.loc[i, 'gene_name'] = gn
                    input_df.loc[i, 'uniprot bank'] = 'swissprot'
                    #print("uniprot id: ", accession_ids)
                    #print("gene name: ", gn)

                else:
                    if accession_ids[0] in t_annot_df.index.values:
                        gn = t_annot_df.ix[accession_ids[0]]["Gene name"]
                        if not type(gn) is str:
                            for g in gn:
                                gn = g
                                break
                        #print("uniprot id: ", accession_ids)
                        #print("gene name: ", gn)

                        input_df.loc[i, 'gene_name'] = gn
                        input_df.loc[i, 'uniprot bank'] = 'TRemBL'
        else:
            if "Fragment" not in str(row[annot_col]):
                #print(i)
                if accession_ids[0] in s_annot_df.index.values:
                    gn = s_annot_df.ix[accession_ids[0]]["Gene name"]
                    if not type(gn) is str:
                        for g in gn:
                            gn = g
                            break
                    input_df.loc[i, 'gene_name'] = gn
                    input_df.loc[i, 'uniprot bank'] = 'swissprot'
                    #print("uniprot id: ", accession_ids)
                    #print("gene name: ", gn)

                else:
                    if accession_ids[0] in t_annot_df.index.values:
                        gn = t_annot_df.ix[accession_ids[0]]["Gene name"]
                        if not type(gn) is str:
                            for g in gn:
                                gn = g
                                break
                        #print("uniprot id: ", accession_ids)
                        #print("gene name: ", gn)

                        input_df.loc[i, 'gene_name'] = gn
                        input_df.loc[i, 'uniprot bank'] = 'TRemBL'
                # try:
                #     gn = s_annot_df.ix[accession_ids[0]]["Gene name"]
                #     print("gene name: ",gn)
                #     input_df.loc[i, 'gene name'] = gn
                #     print(input_df.loc[i, 'gene name'])
                #
                # except KeyError as e:
                #     print(e)
                #     print("error in swiss")
                #     try:
                #         gn = t_annot_df.ix[accession_ids[0]]["Gene name"]
                #         input_df.loc[i, 'gene name'] = gn
                #     except KeyError as e:
                #         print(e)
                #         print("error in trembl")
            #print(input_df)
            #sys.exit()
    return input_df

def annotate_using_own_annotation_files(input_df, annot_file,annot_col):
    annot_df = read_csv_file(annot_file, "swiss prot annotation file", index_col=0, header=0,sep='\t')
    for i, row in input_df.iterrows():
        accession_ids = row['accession'].split(";")
        try:
            genename = annot_df.ix[accession_ids[0]]["Gene Name"]
            if not type(genename) is str:
                for g in genename:
                    genename=g
                    break
            input_df.loc[i, 'Gene Name'] = genename
        except (ValueError, KeyError) as e:
            print(e)

    return input_df




def compute_cv(abundancies):
    return np.nanstd(abundancies) / np.nanmean(abundancies)



def plot_cvs_for_all_sample(filename, output_dir, input_df, mapping_df, group_compare):

    abundancies_cols = input_df.columns.values[:]
    all_abundances = input_df[:][abundancies_cols]
    if group_compare:
        column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)
    else:
        column_groups = build_sample_mapping_dict(mapping_df,abundancies_cols)
    print(column_groups)
    all_groups = [x for x in list(column_groups.keys())]

    for group in all_groups:
        print(group)
        cv_list=[]
        for protein in all_abundances.index.values:
            col_idx = get_group_col_index(column_groups[group])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))

            if np.isfinite(compute_cv(abundancies)):
                cv_list.append(compute_cv(abundancies))
        if group == 'Control':
            print(cv_list)
        plot_histogram_distribution(cv_list,group,filename,output_dir)
        show_box_plot_distribution(cv_list,group,filename,output_dir)



def plot_cvs_by_sample(filename, output_dir, input_df, mapping_df, args,ignored_cols):

    abundancies_cols = input_df.columns.values[ignored_cols:]
    all_abundances = input_df[:][abundancies_cols]
    if args['group_compare']:
        column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)
    elif args['condition_compare']:
        column_groups = build_condition_mapping_dict(mapping_df,abundancies_cols)
    else:
        column_groups = build_sample_label_mapping_dict(mapping_df,abundancies_cols)

    all_groups = [x for x in list(column_groups.keys())]

    for group in all_groups:
        cv_list=[]
        for protein in all_abundances.index.values:
            col_idx = get_group_col_index(column_groups[group])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))

            if np.isfinite(compute_cv(abundancies)):
                cv_list.append(compute_cv(abundancies))
        plot_histogram_distribution_by_group(cv_list,group,filename,output_dir,'CV', 'proteins #',100)
        show_box_plot_distribution(cv_list,group,filename,output_dir)

def plot_cvs(filename, output_dir, input_df, mapping_df, group_compare):

    abundancies_cols = input_df.columns.values[:]
    all_abundances = input_df[:][abundancies_cols]
    if group_compare:
        column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)
    else:
        column_groups = build_condition_mapping_dict(mapping_df,abundancies_cols)
    print(column_groups)
    all_groups = [x for x in list(column_groups.keys())]

    for group in all_groups:
        print(group)
        cv_list=[]
        for protein in all_abundances.index.values:
            col_idx = get_group_col_index(column_groups[group])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))

            if np.isfinite(compute_cv(abundancies)):
                cv_list.append(compute_cv(abundancies))
        if group == 'Control':
            print(cv_list)
        plot_histogram_distribution(cv_list,group,filename,output_dir)
        show_box_plot_distribution(cv_list,group,filename,output_dir)

def filtering_by_sample(input_df, mapping_df, cv_threshold, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_samples = build_sample_label_mapping_dict(mapping_df, abundancies_cols)
    filtered_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_samples = [x for x in list(column_samples.keys())]
    prot_to_drop= []

    for protein in all_abundances.index.values:
        count_rejected=0
        cv_list=[]
        for sample in all_samples:
            col_idx = get_group_col_index(column_samples[sample])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))


            if np.count_nonzero(~np.isnan(abundancies)) < int(np.ceil((len(abundancies) / 100.0) * 66)):
                prot_to_drop.append(protein)
                logging.info(' protein: ' + protein + " sample: " + sample + " cv: " + str(
                    compute_cv(abundancies)) + " abundancies: " + str(abundancies) + "rejected for nan values")
            else:
                cv_list.append(compute_cv(abundancies))

                if check_cv(abundancies,cv_threshold):
                    filtered_df.loc[protein][col_idx] = abundancies
                else:
                    count_rejected+=1
                    #prot_to_drop.append(protein)
                    logging.info(' protein: ' + protein + " sample: " + sample + " cv: " + str(compute_cv(abundancies)) + " abundancies: " + str(abundancies))
        # if protein == "P56279":
        #     print(count_rejected)
        if count_rejected > (len(all_samples)/100)*20 :
            logging.info(' protein rejected: ' + protein + " sample: " + sample + " count bad cv: " + str(
                count_rejected) + " abundancies: " + str(abundancies))

            #print(len(all_samples))
            #print(count_rejected)
            #print((len(all_samples)/100)*10)
            prot_to_drop.append(protein)

    input_df=input_df[~input_df.index.isin(prot_to_drop)]
    logging.info(' Keeping ' + str(len(input_df)) + ' proteins that have passed CV by sample filtering step')

    if ignored_columns ==2:
        input_df = input_df.drop(['accession', 'description'], axis=1)
    elif ignored_columns ==1:
        input_df = input_df.drop(['description'], axis=1)
    #filtered_df = filtered_df.dropna()
    return input_df
    #return filtered_df

def filtering_sample_by_nan(input_df, mapping_df, nan_threshold, ignored_columns, max_bad_sample,statistic_df,stat_dir):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_samples = build_sample_label_mapping_dict(mapping_df, abundancies_cols)
    #filtered_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_samples = [x for x in list(column_samples.keys())]
    prot_to_drop= []

    for protein in all_abundances.index.values:
        print(protein)
        count_rejected = 0
        count_nan = 0
        dict = {}
        dict_total_count = {}
        groups = get_group(mapping_df)
        for gr in groups:
            dict[gr]=[]
            dict_total_count[gr]=[]
        for sample in all_samples:
            #print(sample)
            group=get_group_with_sample(sample,mapping_df)
            col_idx = get_group_col_index(column_samples[sample])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            dict_total_count[group].append(np.count_nonzero(np.isnan(abundancies)))
            # print("protein",str(protein))
            # print("len abundancies", str(len(abundancies)))
            # print(abundancies)0.
            # print("non nan")
            # print(np.count_nonzero(~np.isnan(abundancies)))
            # print("nan_threshold")
            #print(int(np.ceil((len(abundancies) / 100.0) * nan_threshold)))
            if np.count_nonzero(~np.isnan(abundancies)) < int(np.ceil((len(abundancies) / 100.0) * nan_threshold)):
                dict[group].append(1)
                count_rejected+=1
                count_nan+=np.count_nonzero(np.isnan(abundancies))
                logging.info(' protein: ' + protein + " sample: " + sample + " cv: " + str(compute_cv(abundancies)) + " abundancies: " + str(abundancies) + "rejected for nan values")
            else:
                dict[group].append(0)

        NaN_count=[]
        for gr in groups:
            NaN_count.append(np.sum(dict[gr]))

        if (np.abs(NaN_count[0]-NaN_count[1])> 3):
            #print(dict)
            #print(dict_total_count)
            continue
        print(count_rejected)
        print(count_nan)
        print(dict)
        print(dict_total_count)
        statistic_df.loc[protein]['sample with >50% NaN'] = count_rejected
        statistic_df.loc[protein]['count NaN'] = count_nan

        if count_rejected > max_bad_sample:
            prot_to_drop.append(protein)
    input_df=input_df[~input_df.index.isin(prot_to_drop)]
    logging.info(' Keeping ' + str(len(input_df)) + ' proteins that have passed CV by sample filtering step')

    if ignored_columns ==2:
        input_df = input_df.drop(['accession', 'description'], axis=1)
    elif ignored_columns ==1:
        input_df = input_df.drop(['description'], axis=1)
    #filtered_df = filtered_df.dropna()
    statistic_df.to_csv(stat_dir+'/stat.csv')
    return input_df
    #return filtered_df





def filtering_by_condition(input_df, mapping_df, cv_threshold, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_condition_mapping_dict(mapping_df, abundancies_cols)
    filtered_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    #input_df['check_CV'] = ["No" for i in range(len(input_df))]
    #print(all_abundances.columns.values)
    all_groups = [x for x in list(column_groups.keys())]
    prot_to_drop= []
    for protein in all_abundances.index.values:
        for group in all_groups:
            #print(group)
            col_idx = get_group_col_index(column_groups[group])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            #print(protein)
            # if protein == 'PLP1':
            #     print(' protein: ' + protein + " group: " + group + " cv: " + str(compute_cv(abundancies)) + " abundancies: " + str(abundancies))

            if check_cv(abundancies,cv_threshold):

                #filtered_df.loc[protein][col_idx] = abundancies
                logging.info('Validated protein: ' + protein + " group: " + group + " cv: " + str(compute_cv(abundancies)) + " abundancies: " + str(abundancies))

            else:
                logging.info('rejected protein: ' + protein + " group: " + group + " cv: " + str(compute_cv(abundancies)) + " abundancies: " + str(abundancies))
                prot_to_drop.append(protein)
    input_df=input_df[~input_df.index.isin(prot_to_drop)]
    if ignored_columns ==2:
        input_df = input_df.drop(['accession', 'description'], axis=1)
    elif ignored_columns ==1:
        input_df = input_df.drop(['description'], axis=1)
    #filtered_df = filtered_df.dropna()
    return input_df
    #return filtered_df

def filtering_by_condition_not_paired(input_df, mapping_df, cv_threshold, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_not_paired_condition_mapping_dict(mapping_df, abundancies_cols)
    filtered_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    for protein in all_abundances.index.values:
        for group in all_groups:
            col_idx = get_group_col_index(column_groups[group])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            if check_cv(abundancies,cv_threshold):

                filtered_df.loc[protein][col_idx] = abundancies
            else:
                cv=compute_cv(abundancies)
                logging.info(' protein: ' + protein + " group: " + group + " cv: " + str(cv) + " abundancies: " + str(abundancies))

    filtered_df = filtered_df.dropna()
    return filtered_df


def filtering_by_group(input_df, mapping_df, cv_threshold, ignored_columns=0):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_group_mapping_dict(mapping_df, abundancies_cols)
    filtered_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    prot_to_drop= []

    for protein in all_abundances.index.values:
        for group in all_groups:
            col_idx = get_group_col_index(column_groups[group])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            if check_cv(abundancies, cv_threshold):

                filtered_df.loc[protein][col_idx] = abundancies
            else:
                cv = compute_cv(abundancies)
                prot_to_drop.append(protein)
                #print(' protein: ' + protein + " group: " + group + " cv: " + str(cv) + " abundancies: " + str(abundancies))
                #logging.info(' protein: ' + protein + " group: " + group + " cv: " + str(cv) + " abundancies: " + str(abundancies))


            # #print(group)
            # col_idx = get_group_col_index(column_groups[group])
            # abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            # if check_cv(abundancies,cv_threshold):
            #     filtered_df.loc[protein][col_idx] = abundancies
            # else:
            #     cv=compute_cv(abundancies)
            #     #print(cv)
            #     logging.info(' protein: ' + protein + " group: " + group + " cv: " + str(cv) + " abundancies: " + str(abundancies))
    #print(filtered_df)
    #filtered_df = filtered_df.dropna()
    input_df=input_df[~input_df.index.isin(prot_to_drop)]

    return input_df


def filtering_by_group_control(input_df, mapping_df, control_group, cv_threshold,ignored_cols):
    abundancies_cols = input_df.columns.values[ignored_cols:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)
    #print(column_groups)
    filtered_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys()) if x != control_group]
    for protein in all_abundances.index.values:
        col_idx = get_group_col_index(column_groups[control_group])
        filter_group_abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        #print(filter_group_abundancies)
        #cv = np.nanstd(filter_group_abundancies) / np.nanmean(filter_group_abundancies)
        #if cv < cv_threshold:
        if check_cv(filter_group_abundancies,cv_threshold):
            filtered_df.loc[protein][col_idx] = filter_group_abundancies
            for group in all_groups:
                col_idx = get_group_col_index(column_groups[group])
                abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
                filtered_df.loc[protein][col_idx] = abundancies
        else:
            logging.info(' protein: ' + protein+ " group: "+control_group+" cv: "+str(compute_cv(filter_group_abundancies)) + " abundancies: " + str(filter_group_abundancies))
    print(filtered_df)
    filtered_df = filtered_df.dropna()
    return filtered_df

def build_mean_paired_columns_headers(column_groups):
    dicts = []
    headers=[]
    for group in list(column_groups.keys()):
        for sample in list(column_groups[group].keys()):
            headers.append(str(group) + '_' + str(sample))
    return headers


def build_paired_columns_headers(column_groups):
    dicts = []
    headers=[]
    for group in list(column_groups.keys()):
        for sample in list(column_groups[group].keys()):
            for replicate in column_groups[group][sample].keys():
                if len(column_groups[group][sample][replicate]) == 2:
                    headers.append(str(group) + '_' + str(sample) + '_' + str(replicate))
    return headers


def build_mean_columns_headers(column_groups,filename):
    dicts = []
    headers=[]
    for group in list(column_groups.keys()):
        for sample in list(column_groups[group].keys()):
            headers.append(str(group) + '_' + str(sample))
    return headers


def build_columns_headers(column_groups,filename):
    dicts = []
    headers=[]
    for group in list(column_groups.keys()):
        dicts.append(column_groups[group])
    for key in dicts[0]:
        if key in dicts[1]:
            #header = '/'.join(list(column_groups.keys()))
            headers.append(filename +'_ratio replicate '+str(key))
    return headers


def get_common_replicates(column_groups):
    dicts = []
    keys = []
    for group in list(column_groups.keys()):
        dicts.append(column_groups[group])
    for key in dicts[0]:
        if key in dicts[1]:
            keys.append(key)
    return keys


#improve ratio computation for arrays of different size
def compute_mean_paired_ratio_df(filename, input_df, mapping_df, reference):

    abundancies_cols = input_df.columns.values
    all_abundances = input_df[:][abundancies_cols]
    column_conditions = build_condition_mapping_dict(mapping_df,abundancies_cols)
    columns_headers = build_mean_paired_columns_headers(build_header_mapping_dict(mapping_df,abundancies_cols))
    #print(columns_headers)
    ratio_df = pd.DataFrame(columns=columns_headers, index=all_abundances.index)
    for protein in all_abundances.index.values:
        ratios = []
        for key in get_common_replicates(column_conditions):
            values=[]
            for group in list(column_conditions.keys()):
                if group == reference:
                    values.append(all_abundances.loc[protein][column_conditions[group][key]].values[0])
            for group in list(column_conditions.keys()):
                if group != reference:
                    values.append(all_abundances.loc[protein][column_conditions[group][key]].values[0])
            ratios.append(values[0]/values[1])
        for i in range(len(columns_headers)):
            ratio_df.loc[protein][columns_headers[i]] = np.mean(ratios)

    return ratio_df


#improve ratio computation for arrays of different size
def compute_paired_ratio_df(filename, input_df, mapping_df, reference):

    abundancies_cols = input_df.columns.values
    all_abundances = input_df[:][abundancies_cols]
    column_conditions = build_condition_mapping_dict(mapping_df,abundancies_cols)
    columns_headers = build_paired_columns_headers(build_header_mapping_dict(mapping_df,abundancies_cols))
    ratio_df = pd.DataFrame(columns=columns_headers, index=all_abundances.index)
    for protein in all_abundances.index.values:
        ratios = []
        for key in get_common_replicates(column_conditions):
            values=[]
            for group in list(column_conditions.keys()):
                if group == reference:
                    values.append(all_abundances.loc[protein][column_conditions[group][key]].values[0])
            for group in list(column_conditions.keys()):
                if group != reference:
                    values.append(all_abundances.loc[protein][column_conditions[group][key]].values[0])
            ratios.append(values[0]/values[1])

        #print(ratios)
        #print(len(columns_headers))
        for i in range(len(columns_headers)):
            ratio_df.loc[protein][columns_headers[i]] = ratios[i]

    return ratio_df


def compute_mean_ratio_df(filename, input_df, mapping_df, reference):
    abundancies_cols = input_df.columns.values[:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)

    ratio_df = pd.DataFrame(columns=[filename], index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys()) if x != reference]
    for protein in all_abundances.index.values:
        ratio = []
        col_idx = get_group_col_index(column_groups[reference])
        control_group_abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        ratio.append(control_group_abundancies)
        for group in all_groups:
            col_idx = get_group_col_index(column_groups[group])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            ratio.append(abundancies)

        ratio = np.mean(np.array(ratio[1])) / np.mean(np.array(ratio[0]))
        ratio_df.loc[protein][filename] = ratio
    return ratio_df


def compute_control_ratio_df(input_df, mapping_df, control_group,ignored_cols):
    abundancies_cols = input_df.columns.values[ignored_cols:]
    all_abundances = input_df[:][abundancies_cols]
    column_groups = build_group_mapping_dict(mapping_df,abundancies_cols)

    ratio_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys()) if x != control_group]
    for protein in all_abundances.index.values:
        col_idx = get_group_col_index(column_groups[control_group])
        control_group_abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        ratio_df.loc[protein][col_idx] = np.array(control_group_abundancies) / np.mean(control_group_abundancies)
        for group in all_groups:
            col_idx = get_group_col_index(column_groups[group])
            abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            ratio = np.array(abundancies) / np.mean(control_group_abundancies)
            ratio_df.loc[protein][col_idx] = ratio
    return ratio_df


def merge_directory_files(input_dir,ignored_cols=0):
    frames = []
    for input_file in os.listdir(input_dir):
        input_df = read_csv_file(input_dir + input_file, "input file", index_col=0)
        abundancies_cols = input_df.columns.values[ignored_cols:]
        all_abundances = input_df[:][abundancies_cols]
        frames.append(all_abundances)
    merged_df = pd.concat(frames, axis=1)
    return merged_df


def build_correlation(data):
    return data.corr(method='pearson', min_periods=1)


def qualitative3(x):
    if x > 1.2:
        return 2
    elif x > 1 and x <= 1.2:
        return 1
    elif x <= 1 and x >= 0.8:
        return 0
    elif x <= 0.8:
        return -1
    else:
        return -2

def qualitative2(x):
    if x > 1.2:
        return 2
    elif x > 1 and x <= 1.2:
        return 1
    elif x <= 1 and x >= 0.8:
        return -1
    elif x <= 0.8:
        return -2
    else:
        return 0

def qualitative(x):
    if x > 1.5:
        return 2
    elif x > 1.1 and x <= 1.5:
        return 1
    elif x <= 1.1 and x >= 0.9:
        return 0
    elif x < 0.9 and x > 0.6:
        return -1
    elif x <= 0.6:
        return -2
    else:
        return 0

def qualitative4(x):
    if x > 2:
        return 2
    elif x > 1.5 and x < 2:
        return 1
    elif x <= 1.5 and x >= 1:
        return 0.5
    elif x <= 1 and x >= 0.9:
        return 0.1
    elif x < 0.9 and x > 0.6:
        return -1
    elif x <= 0.6:
        return -2
    else:
        return 0


def qualitative_ab(x):
    if x > 20:
        return 2
    elif x > 15 and x < 20:
        return 1
    elif x <= 10 and x >= 5:
        return 0.5
    elif x <= 5 and x >= 2:
        return 0.1
    elif x < 2 and x > 1:
        return -1
    elif x <= 1:
        return -2
    else:
        return 0

def qualitative_log(x):
    if x > 0.5:
        return 2
    elif x > 0 and x <= 0.5:
        return 1
    elif x < 0 and x >= -0.5:
        return -1
    elif x <= -0.5:
        return -2
    else:
        return 0

def qualitative_log2(x):
    if x > 1:
        return 3
    elif x > 0 and x <= 1:
        return 2
    elif x <= 0 and x >= -1:
        return -2
    elif x <= -1:
        return -3
    else:
        return 0

def qualitative_log3(x):
    if x > 2:
        return 4
    elif x > 1 and x <= 2:
        return 2
    elif x <= 1 and x > 0:
        return 1
    elif x < 0 and x >= -1:
        return -1
    elif x < -1 and x >= -2:
        return -2
    elif x < -2 and x >= -3:
        return -4
    else:
        return 0

def build_classes(input_df,mapping_df,mapping_col_idx):
    classes = []
    cols = input_df.columns.values
    for col in cols:
        for i in mapping_df.index.values:
            if mapping_df.loc[i][mapping_col_idx] in col:
                classes.append(mapping_df.loc[i][0])
                break
    return classes

def build_data(input_df,mapping_df,mapping_col_idx):
    data = []
    cols = input_df.columns.values
    for col in cols:
        for i in mapping_df.index.values:
            if mapping_df.loc[i][mapping_col_idx] in col:
                data.append(input_df[col].values)
                break
    return np.array(data,dtype='float64')


def run_ttest_and_annotate(input_df, ratio_df, annot_df,abundancies_cols, abundancies_control_cols,max_nan_by_group):
    ttest_df = pd.DataFrame(columns=['description','pvalue', 'padj', 'Log2FoldChange'], index=input_df.index)
    for protein in input_df.index.values:
        #print(protein)
        non_control_group_abundancies = np.array(input_df.loc[protein][abundancies_cols].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))

        #print(non_control_group_abundancies)
        control_group_abundancies = np.array(input_df.loc[protein][abundancies_control_cols].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        #print(control_group_abundancies)
        if (np.count_nonzero(pd.isnull(control_group_abundancies)) < (len(control_group_abundancies) / 100) * max_nan_by_group) and (np.count_nonzero(pd.isnull(non_control_group_abundancies)) < (len(non_control_group_abundancies) / 100) * max_nan_by_group):


            stat, p_value = stats.ttest_ind(non_control_group_abundancies, control_group_abundancies, nan_policy='omit')
            #print(p_value)
            ttest_df.loc[protein]['pvalue'] = p_value
            ttest_df.loc[protein]['Log2FoldChange'] = np.log2(ratio_df.ix[protein].mean(skipna=True))
            ttest_df.loc[protein]['description'] = annot_df.ix[protein]["description"]

    rej, pval_corr = smm.multipletests(ttest_df['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    ttest_df['padj'] = pval_corr
    #print(ttest_df)
    return ttest_df

def run_ttest(input_df, ratio_df, abundancies_cols, abundancies_control_cols,max_nan_by_group):
    ttest_df = pd.DataFrame(columns=['pvalue', 'padj', 'Log2FoldChange'], index=input_df.index)

    for protein in input_df.index.values:
        print(protein)
        print(abundancies_cols)
        print(abundancies_control_cols)

        non_control_group_abundancies = np.array(input_df.loc[protein][abundancies_cols].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))

        print(non_control_group_abundancies)
        control_group_abundancies = np.array(input_df.loc[protein][abundancies_control_cols].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        print(control_group_abundancies)
        if (np.count_nonzero(pd.isnull(control_group_abundancies)) < (len(control_group_abundancies) / 100) * max_nan_by_group) and (np.count_nonzero(pd.isnull(non_control_group_abundancies)) < (len(non_control_group_abundancies) / 100) * max_nan_by_group):


            stat, p_value = stats.ttest_ind(non_control_group_abundancies, control_group_abundancies, nan_policy='omit')
            #print(p_value)
            ttest_df.loc[protein]['pvalue'] = p_value
            ttest_df.loc[protein]['Log2FoldChange'] = np.log2(ratio_df.ix[protein].mean(skipna=True))
            #non_control_group_mean_ratio=np.mean(np.array(input_df.loc[protein][abundancies_cols].map(lambda x: atof(x) if type(x) == str else x)))
            #control_group_mean_ratio = np.mean(np.array(input_df.loc[protein][abundancies_control_cols].map(lambda x: atof(x) if type(x) == str else x)))
            #ttest_df.loc[protein]['Log2FoldChange'] = non_control_group_mean_ratio/control_group_mean_ratio
            #print(non_control_group_mean_ratio/control_group_mean_ratio)


    rej, pval_corr = smm.multipletests(ttest_df['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    ttest_df['padj'] = pval_corr
    #print(ttest_df)
    return ttest_df



def merge_replicates(data,mapping_df,column_key,reference,include_reference):
    #print(data)
    #print(reference)

    sample=[]
    for i in mapping_df.index.values:
        if not include_reference:

            if mapping_df.loc[i][column_key] != reference:
                print(mapping_df.loc[i][column_key])
                #sample.append(mapping_df.loc[i][column_key] + "_" + str(mapping_df.loc[i][1]) + '_' + str(mapping_df.loc[i][0] + '_' + str(mapping_df.loc[i][6])))
                sample.append(mapping_df.loc[i][column_key] + "_" + str(mapping_df.loc[i][1]) + '_' + str(mapping_df.loc[i][6]))# + '_' + str(mapping_df.loc[i][6]))


        else:
            #print(mapping_df.loc[i][2])
            #sample.append(mapping_df.loc[i][column_key]+"_"+str(mapping_df.loc[i][1])+ '_' + str(mapping_df.loc[i][0]+ '_' + str(mapping_df.loc[i][6])))
            sample.append(mapping_df.loc[i][column_key] + "_" + str(mapping_df.loc[i][1]) + '_' + str(mapping_df.loc[i][6]))# + '_' + str(mapping_df.loc[i][6]))

    #print(sample)
    sample = set(sample)
    sample = list(sample)
    #print(sample)

    df = pd.DataFrame(columns=sample, index=data.index)
    print(data)
    for s in sample:
        #print(s)
        tag=s.split("_")[0]+"_"+s.split("_")[1]
        #print(tag)
        df[s] = data.filter(regex=tag).mean(axis=1,skipna=True)
    #sys.exit()
    #print(df)
    return df

def build_values_list(input_df,scored,biomarked_type,protein,reference,include_reference,log):
    if not include_reference:
        type_cols = [col for col in input_df.columns.values if biomarked_type in col and reference not in col]
        other_cols = [col for col in input_df.columns.values if biomarked_type not in col and reference not in col]
        # type_cols = list(itertools.chain(*column_groups[biomarked_type].values()))
        # other_types = [x for x in list(column_groups.keys()) if (x != reference and x != biomarked_type)]
        # other_cols = []
        # for other_type in other_types:
        #     other_cols.extend(list(itertools.chain(*column_groups[other_type].values())))
    else:
        type_cols = [col for col in input_df.columns.values if biomarked_type in col]
        other_cols = [col for col in input_df.columns.values if biomarked_type not in col]
    if log:
        type_values = np.array([np.log2(x) for x in list(scored.loc[protein][type_cols]) if str(x) != 'nan'])
        other_values = np.array([np.log2(x) for x in list(scored.loc[protein][other_cols]) if str(x) != 'nan'])
    else:
        type_values = np.array([x for x in list(scored.loc[protein][type_cols]) if str(x) != 'nan'])
        other_values = np.array([x for x in list(scored.loc[protein][other_cols]) if str(x) != 'nan'])


    return type_values,other_values,type_cols,other_cols


def run_pnorm_test(ratio_df,annot_df):
    values = ratio_df[ratio_df.columns[0]]
    #print(values)
    list_z = stats.zscore([np.log2(x) for x in values.values])
    #print(list_z)

    df_z = pd.DataFrame(columns=['description','z-score', 'Log2FoldChange', 'pvalue', 'padj'], index=ratio_df.index)
    df_z.index.name = "gene name"
    df_z['z-score'] = list_z
    df_z['Log2FoldChange'] = [np.log2(x) for x in values.values]
    #print(df_z)
    #print(ratio_df.index.values)
    for protein in ratio_df.index.values:
        #print(protein)
        df_z.loc[protein,'description'] = annot_df.ix[protein]["description"]
        df_z.loc[protein,'pvalue']= norm.pdf(df_z.ix[protein]['z-score'])
        #print(norm.pdf(df_z.ix[protein]['z-score']))
    df_z = df_z.sort_values(by='pvalue')
    rej, pval_corr = smm.multipletests(df_z['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    df_z['padj'] = pval_corr
    return df_z


def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)


def convert_uniprot_to_symbol_raw(list_ids):
    records = []
    filename="data/annotation_data/uniprot_to_symbol.tsv"
    annot_df=pd.read_csv(filename,sep='\t',index_col=0)
    #print(annot_df)
    for acc in list_ids:
        try:
            genename = annot_df.ix[acc]["Gene Name"]
            if not type(genename) is str:
                for g in genename:
                    genename=g
                    break
            records.append(genename)
            #records.append(genename+" ("+acc+")")
        except (ValueError, KeyError) as e:
            print(e)
            records.append(acc)


    return records

def convert_uniprot_to_symbol_acc_raw(list_ids):
    records = []
    filename="data/annotation_data/uniprot_to_symbol.tsv"
    annot_df=pd.read_csv(filename,sep='\t',index_col=0)
    #print(annot_df)
    for acc in list_ids:
        try:
            genename = annot_df.ix[acc]["Gene Name"]
            if not type(genename) is str:
                for g in genename:
                    genename=g
                    break
            #records.append(genename)
            records.append(genename+" ("+acc+")")
        except (ValueError, KeyError) as e:
            print(e)
            records.append(acc)


    return records


def build_profile(input_df,ttest_df,control_group,output_file):
    abundancies_control_cols = [x for x in input_df.columns.values if control_group in x]
    abundancies_cols = [x for x in input_df.columns.values if control_group not in x]
    with PdfPages(get_filepath(output_file) + '/' + control_group + '_multipage_pdf_last.pdf') as pdf:
        for protein in ttest_df.index.values:
            #print(protein)

            type_values = np.array(
                input_df.loc[protein][abundancies_cols].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
            other_values = np.array(input_df.loc[protein][abundancies_control_cols].map(
                lambda x: atof(x) if type(x) == str else x))  # apply(atof))

            # log_type_values = np.array([np.log2(x) for x in list(scored.loc[protein][type_cols]) if str(x) != 'nan'])
            # type_values = np.array([x for x in list(ttest_df.loc[protein][type_cols]) if str(x) != 'nan'])
            # log_other_values = np.array([np.log2(x) for x in list(scored.loc[protein][other_cols]) if str(x) != 'nan'])
            # other_values = np.array([x for x in list(ttest_df.loc[protein][other_cols]) if str(x) != 'nan'])
            # print(type_values)
            # print(other_values)
            # scored.ix[protein, 'score'] = 1

            plt.figure()
            plt.boxplot([type_values, other_values])
            plt.scatter([1 for x in type_values], type_values)
            plt.scatter([2 for x in other_values], other_values)
            plt.xticks(np.arange(1, 3, step=1))
            plt.xticks(np.arange(1, 3), (control_group, 'GR'))
            plt.ylabel("normalized expression")
            plt.scatter(1, np.median(type_values), color="black")
            plt.scatter(2, np.median(other_values), color="black")
            # plt.plot([np.median(type_values), np.median(other_values)])
            # plt.plot([1,np.median(type_values)],[3, np.median(other_values)])

            plt.title(protein)
            pdf.savefig()
            plt.close()

def get_group_with_sample(sample,mapping_df):
    return list(mapping_df[mapping_df["aGRr"]==sample]["Group"])[0]

def get_group(mapping_df):
    return set(mapping_df["Group"])



def get_specific_prot(prot_list,input_df):
    return input_df[input_df.index.isin(prot_list)]




def compute_mean_quartile(type_values,other_values):
    mean_type = np.mean(np.percentile(type_values, [25, 50, 75]))
    mean_other = np.mean(np.percentile(other_values, [25, 50, 75]))
    #print(mean_type)
    #print(mean_other)
    my_score=mean_type-mean_other
    total_score = mean_type - mean_other
    return np.abs(my_score),total_score

def compute_score_interquartile(type_values,other_values):
    my_score=0
    total_score=0

    min_type = np.percentile(type_values,25)
    max_type = np.percentile(type_values, 75)
    min_other = np.percentile(other_values, 25)
    max_other = np.percentile(other_values, 75)

    #print(type_values)
    #print(other_values)
    #print(mean_type)
    #print(mean_other)



    if max_type > max_other and min_type > min_other:
        # total_score += np.max(other_values) - np.min(type_values) # / (np.max(type_values)-np.min(other_values))
        count_type_values_overlap = 0
        for val in type_values:
            if min_other < val < max_other:
                total_score += (max_other - val)  # / (np.max(type_values)-np.min(other_values))

                count_type_values_overlap += 1
        count_other_values_overlap = 0
        for val in other_values:
            if min_type < val < max_type:
                total_score += (val - min_type)  # / (np.max(type_values)-np.min(other_values))
                count_other_values_overlap += 1

        my_score += (count_type_values_overlap / len(type_values) + count_other_values_overlap / len(other_values)) * (
                (max_other - min_type) / (max_type - np.min(other_values)))


    elif max_type < max_other and min_type < min_other:
        # total_score += np.max(type_values) - np.min(other_values)  # / (np.max(type_values)-np.min(other_values))
        count_type_values_overlap = 0
        for val in type_values:
            if min_other < val < max_other:
                total_score += (val - min_other)  # / (np.max(other_values)-np.min(type_values))
                count_type_values_overlap += 1

        count_other_values_overlap = 0
        for val in other_values:
            if min_type < val < max_type:
                total_score += (val - min_type)  # / (np.max(type_values)-np.min(other_values))
                count_other_values_overlap += 1
        my_score += (count_type_values_overlap / len(type_values) + count_other_values_overlap / len(other_values)) * (
                (max_type - min_other) / (max_other - min_type))

        # my_score += (count_type_values_overlap / len(type_values)*(np.max(type_values)-np.min(other_values)) + count_other_values_overlap) / len(other_values)*(np.max(type_values)-np.min(other_values))

    else:
        total_score = -100
        my_score = -100

    return my_score, total_score


def compute_score_ranking_overlap(type_values,other_values):
    my_score=0
    total_score=0


    max_type = np.max(type_values)
    max_other = np.max(other_values)
    min_type = np.min(type_values)
    min_other = np.min(other_values)

    if max_type > max_other and min_type > min_other:
        # total_score += np.max(other_values) - np.min(type_values) # / (np.max(type_values)-np.min(other_values))
        count_type_values_overlap = 0
        for val in type_values:
            if min_other < val < max_other:
                total_score += (max_other - val)  # / (np.max(type_values)-np.min(other_values))
                count_type_values_overlap += 1
        count_other_values_overlap = 0
        for val in other_values:
            if min_type < val < max_type:
                total_score += (val - min_type)  # / (np.max(type_values)-np.min(other_values))
                count_other_values_overlap += 1

        my_score += (count_type_values_overlap / len(type_values) + count_other_values_overlap / len(other_values)) \
                    * ((max_other - min_type) / (max_type - min_other))


    elif max_type < max_other and min_type < min_other:
        # total_score += np.max(type_values) - np.min(other_values)  # / (np.max(type_values)-np.min(other_values))
        count_type_values_overlap = 0
        for val in type_values:
            if min_other < val < max_other:
                total_score += (val - min_other)  # / (np.max(other_values)-np.min(type_values))
                count_type_values_overlap += 1

        count_other_values_overlap = 0
        for val in other_values:
            if min_type < val < max_type:
                total_score += (val - min_type)  # / (np.max(type_values)-np.min(other_values))
                count_other_values_overlap += 1
        my_score += (count_type_values_overlap / len(type_values) + count_other_values_overlap / len(other_values)) \
                   * ((max_type - min_other) / (max_other - min_type))

        #my_score += (count_type_values_overlap / len(type_values)*(np.max(type_values)-np.min(other_values)) + count_other_values_overlap) / len(other_values)*(np.max(type_values)-np.min(other_values))

    else:
        total_score = -100
        my_score = -100


    return my_score,total_score



#Module : importation des fichiers, remplace espaces par underscore
#Rajouter modifiers et type de fichier en entrée
def make_names(input_df):
    for i in input_df.index.value:
        header = input_df.loc[0][i]
        input_df = replace(header=lambda x: re.sub(r'[ ]', '_', x))
    return(input_df)


#Filtration selon nombre de peptides uniques
#!!!!!!!!! nom de colonne
def filtration_unique_peptides(input_df, name_col, threshold):
    todrop = np.where(input_df[name_col] < threshold)
    df = input_df.drop(todrop[0])
    return(df)

#Contaminant
def filtration_contaminant(input_df):
    output_df = input_df[input_df['Contaminant'] == 0]
    return(output_df)

# def filtration_contaminant(input_df, goal = 'keep'):
#     if goal == 'keep':
#         input_df_cont_index = input_df.index[input_df['Contaminant'] == 0].tolist()
#         input_df = input_df.loc[input_df_cont_index]
#     if goal == 'discard':
#         input_df_cont_index = input_df.index[input_df['Contaminant'] == 1].tolist()
#         input_df = input_df.loc[input_df_cont_index]
#
#     return(input_df)

#master protein
def filtration_master_protein(input_df):
    output_df = input_df[input_df['Master'] == "Master Protein"]
    return(output_df)

def filtration_row_na(input_df, metadata_col):
    output_df_data = input_df.filter(regex='GR_')
    output_df_info = input_df.filter(items=metadata_col)

    null_row = output_df_data.isnull().all(axis=1)
    output_df_all = pd.concat([output_df_info, output_df_data], axis=1)
    output_df_all = output_df_all[~null_row]

    return(output_df_all)

def keyfunc(x):
    return x['cell']


def compute_ratio_minmax(input_df, dict_name):
    with open("dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_col = json.load(dict_file)
        for group in dict_col:
            for sample in dict_col[group]:
                if sample != 'Control':
                    col = []
                    col_control = []
                    for replicate in dict_col[group][sample]:
                        col.append(input_df['Reduced_GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)])
                        col_control.append(input_df['Reduced_GR_{}_SA_Control_REP_{}'.format(group, replicate)])
                    col = pd.concat(col, axis=1)
                    col_control = pd.concat(col_control, axis=1)

                    for i in input_df.index.values:
                        if ~col.iloc[i].isnull().all() & ~col_control.iloc[i].isnull().all():
                            input_df.ix[i, 'ratio_{}_{}_control'.format(group, sample)] = col.iloc[i].min() / col_control.iloc[i].max()

                if sample == 'NotaControl1':
                    col = []
                    col_control = []
                    for replicate in dict_col[group][sample]:
                        col.append(input_df['Reduced_GR_{}_SA_Resveratrol_REP_{}'.format(group, replicate)])
                        col_control.append(input_df['Reduced_GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)])
                    col = pd.concat(col, axis=1)
                    col_control = pd.concat(col_control, axis=1)

                    for i in input_df.index.values:
                        if ~col.iloc[i].isnull().all() & ~col_control.iloc[i].isnull().all():
                            input_df.ix[i, 'ratio_{}_{}_resveratrol'.format(group, sample)] = col.iloc[i].min() / \
                                                                                          col_control.iloc[i].max()
    return(input_df)



def compute_ratio_amean(input_df, dict_name):
    #compute ratio with arithmetic mean
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_col = json.load(dict_file)
        for group in dict_col:
            for sample in dict_col[group]:
                if sample != 'Control':
                    col = []
                    col_control = []
                    for replicate in dict_col[group][sample]:
                        col.append(input_df['Reduced_GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)])
                        col_control.append(input_df['Reduced_GR_{}_SA_Control_REP_{}'.format(group, replicate)])
                    col = pd.concat(col, axis=1)
                    col_control = pd.concat(col_control, axis=1)

                    for i in input_df.index.values:
                        if ~col.iloc[i].isnull().all() & ~col_control.iloc[i].isnull().all():
                            input_df.ix[i, 'ratio_{}_{}_control'.format(group, sample)] = col.iloc[i].mean() / col_control.iloc[i].mean()
    return(input_df)


def compute_ratio_gmean(input_df, dict_name):
    #compute ratio with geometric mean
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_col = json.load(dict_file)
        for group in dict_col:
            for sample in dict_col[group]:
                if sample == 'Control':
                    continue
                abundance_col = 'VAL_'+ group
                group_col = [ x for x in input_df.columns.values if abundance_col in x ]
                sample_col  = [ x for x in group_col if sample in x ]
                ctrl_col = [ x for x in group_col if 'Control' in x ]
                if len(sample_col) == 0:
                    continue
                for protein in input_df.index.values:
                    sample_abundancies = np.array(input_df.loc[protein][sample_col].map(lambda x: atof(x) if type(x) == str else x))
                    ctrl_abundancies = np.array(input_df.loc[protein][ctrl_col].map(lambda x: atof(x) if type(x) == str else x))

                    gmean_sample = stats.gmean(sample_abundancies[~np.isnan(sample_abundancies)])
                    gmean_ctrl = stats.gmean(ctrl_abundancies[~np.isnan(ctrl_abundancies)])

                    input_df.ix[protein, 'ratio_{}_{}_control'.format(group, sample)] = gmean_sample / gmean_ctrl

    return(input_df)


def compute_ratio_gmean_nocontrol(input_df):
    abundance_col = input_df.filter(regex = 'GR')

    ### Get id of group and sample in file
    name_ab = []
    for col in abundance_col:
        col_red = '_'.join(col.split('_')[:-2])
        name_ab.append(col_red)
    unique_name_abundance = list(set(name_ab))

    ### Get ratio column name
    cond1_name = '_'.join(unique_name_abundance[0].split('_')[4:])
    cond2_name = '_'.join(unique_name_abundance[1].split('_')[4:])

    ### Compute gmean
    cond1  = [ x for x in abundance_col if unique_name_abundance[0] in x ]
    cond2 = [x for x in abundance_col if unique_name_abundance[1] in x]
    for protein in input_df.index.values:
        cond1_abundancies = np.array(input_df.loc[protein][cond1].map(lambda x: atof(x) if type(x) == str else x))
        cond2_abundancies = np.array(input_df.loc[protein][cond2].map(lambda x: atof(x) if type(x) == str else x))
        print(cond1_abundancies)
        print(cond2_abundancies)
        cond1_abundancies = cond1_abundancies + 0.001
        cond2_abundancies = cond2_abundancies + 0.001
        gmean_sample = stats.gmean(cond1_abundancies[~np.isnan(cond1_abundancies)])
        gmean_ctrl = stats.gmean(cond2_abundancies[~np.isnan(cond2_abundancies)])
        print(gmean_sample)
        print(gmean_ctrl)
        input_df.ix[protein, 'ratio_{}_{}'.format(cond1_name, cond2_name)] = gmean_sample / gmean_ctrl
        print(input_df.ix[protein, 'ratio_{}_{}'.format(cond1_name, cond2_name)])
        print('---')
    return(input_df)

def compute_ratio_gmean_nocontrol_zero(input_df):
    abundance_col = input_df.filter(regex = 'Reduced')

    ### Get id of group and sample in file
    name_ab = []
    for col in abundance_col:
        col_red = '_'.join(col.split('_')[:-2])
        name_ab.append(col_red)
    unique_name_abundance = list(set(name_ab))

    ### Get ratio column name
    cond1_name = '_'.join(unique_name_abundance[0].split('_')[4:])
    cond2_name = '_'.join(unique_name_abundance[1].split('_')[4:])

    ### Compute gmean
    cond1  = [ x for x in abundance_col if unique_name_abundance[0] in x ]
    cond2 = [x for x in abundance_col if unique_name_abundance[1] in x]
    for protein in input_df.index.values:
        cond1_abundancies = np.array(input_df.loc[protein][cond1].map(lambda x: atof(x) if type(x) == str else x))

        cond2_abundancies = np.array(input_df.loc[protein][cond2].map(lambda x: atof(x) if type(x) == str else x))
        cond2_abundancies_noz = [x for x in cond1_abundancies if x != 0]
        cond1_abundancies_noz = [x for x in cond1_abundancies if x != 0]
        print(cond1_abundancies)
        print(cond2_abundancies)
        gmean_sample = gmean_robust(cond1_abundancies[~np.isnan(cond1_abundancies)])
        gmean_ctrl = gmean_robust(cond2_abundancies[~np.isnan(cond2_abundancies)])
        print(gmean_sample)
        print(gmean_ctrl)
        input_df.ix[protein, 'ratio_{}_{}'.format(cond1_name, cond2_name)] = gmean_sample / gmean_ctrl
        print(input_df.ix[protein, 'ratio_{}_{}'.format(cond1_name, cond2_name)])
        print('---')
    return(input_df)


def gmean_reference(input_df):
    abundance_df = input_df.filter(regex='GR')
    reference = [x for x in abundance_df.columns.values if 'reference' in x]
    condition = [x for x in abundance_df.columns.values if 'reference' not in x]

    reference_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in reference]))[0]
    condition_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in condition]))[0]

    for protein in input_df.index.values:
        reference_abundancies = np.array(input_df.loc[protein][reference].map(lambda x: atof(x) if type(x) == str else x))
        condition_abundancies = np.array(input_df.loc[protein][condition].map(lambda x: atof(x) if type(x) == str else x))

        gmean_reference = stats.gmean(reference_abundancies[~np.isnan(reference_abundancies)])
        gmean_condition = stats.gmean(condition_abundancies[~np.isnan(condition_abundancies)])

        input_df.loc[protein, 'ratio_{}_{}'.format(condition_name, reference_name)] = gmean_condition / gmean_reference
        input_df.loc[protein, 'Log2FoldChange'] = np.log2(input_df.loc[protein, 'ratio_{}_{}'.format(condition_name, reference_name)].mean())

    return(input_df)


def gmean_robust(data_array):
    nb_items = len(data_array)
    no_zero = [x for x in data_array if x != 0]
    #gmean =
    return(gmean)

def compute_ratio_moy_temp(input_df, dict_name):
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_col = json.load(dict_file)
        for group in dict_col:
            for sample in dict_col[group]:
                if sample != 'Control':
                    col = []
                    col_control = []
                    for replicate in dict_col[group][sample]:
                        col.append(input_df['Reduced_GR_{}_SA_Resveratrol_REP_{}'.format(group, replicate)])
                        col_control.append(input_df['Reduced_GR_{}_SA_NotaControl1_REP_{}'.format(group, replicate)])
                    col = pd.concat(col, axis=1)
                    col_control = pd.concat(col_control, axis=1)

                    for i in input_df.index.values:
                        if ~col.iloc[i].isnull().all() & ~col_control.iloc[i].isnull().all():
                            input_df.ix[i, 'ratio_{}_{}_control'.format(group, sample)] = col.iloc[i].mean() / col_control.iloc[i].mean()
    return(input_df)

def update_ratio_reference(input_df):
    if 'level_0' in input_df.columns.values:
        input_df = input_df.drop('level_0', axis=1)
    input_df = input_df.reset_index()

    venn_col = input_df.filter(regex='Venn_')
    ratio = input_df.filter(regex='ratio').columns.values[0]
    for i in input_df.index.values:
        if venn_col.loc[i].values[0] == -1:
            input_df.loc[i, ratio] = 0.001
        elif venn_col.loc[i].values[0] == 1:
            input_df.loc[i, ratio] = 1000
        input_df.loc[i, 'Log2FoldChange'] = np.log2(input_df.loc[i, ratio].mean())
    return(input_df)

def update_ratio_dict(input_df, dict_name):
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        venn_col_all = input_df.filter(regex='Venn_')
        #print(venn_col_all.columns.values)
        for group in dict_mapping:
            #print(group)
            venn_col_group = [col for col in venn_col_all.columns.values if group in col]
            if len(venn_col_group) == 0:
                continue
            for sample in dict_mapping[group]:
                #print(sample)
                venn_col_sample = [col for col in venn_col_group if sample in col]
                if sample == 'Control':
                    continue
                if len(venn_col_sample) == 0:
                    continue
                print(group, sample)
                for i, row in input_df.iterrows():
                    if row['Venn_{}_{}'.format(group, sample)] == -1:
                        input_df.ix[i, 'ratio_{}_{}_control'.format(group, sample)] = 0.001
                    elif row['Venn_{}_{}'.format(group, sample)] == 1:
                        input_df.ix[i, 'ratio_{}_{}_control'.format(group, sample)] = 1000
                        #print(input_df.ix[i, 'Accession'])
                        #print(input_df.ix[i, 'ratio_{}_{}_control'.format(group, sample)])
    return(input_df)


def selection_proteins(input_df, stringency):
    input_red_data = input_df.filter(regex='ratio_*')
    input_red_metadata = input_df.filter(items=['Accession', 'Description'])
    rows_list = list()
    for i in input_red_data.index.values:
        for col in input_red_data.columns:
            if input_red_data.iloc[i][col] >= int(stringency):
                dict1 = {'Column' : '{}'.format(col), 'Ratio value' : input_red_data.iloc[i][col], 'Accession' : input_red_metadata.iloc[i]['Accession'], 'Description': input_red_metadata.iloc[i]['Description']}
                rows_list.append(dict1)
    output_df = pd.DataFrame(rows_list)
    return (output_df)

def selection_proteins_results(input_df, stringency):
    input_red_data = input_df.filter(regex='ratio_*')
    input_red_metadata = input_df.filter(items=['Accession', 'Description'])
    input_df_abundance = input_df.filter(regex='Rank_*')
    rows_list = list()
    for i in input_red_data.index.values:
        for col in input_red_data.columns:
            if input_red_data.iloc[i][col] >= stringency:
                id = col.split('_')
                dict1 = {'Column': '{}'.format(col), 'Ratio value': input_red_data.iloc[i][col], 'Accession': input_red_metadata.iloc[i]['Accession'], 'Description': input_red_metadata.iloc[i]['Description'],
                                     'Group': id[1], 'Sample': id[2]}#, 'Abundance_rank_in_sample': input_df_abundance.iloc[i]['Rank_abundance_{}_{}'.format(id[1], id[2])], 'Abundance rank in control' : input_df_abundance.iloc[i]['Rank_abundance_{}_Control'.format(id[1])]}
                rows_list.append(dict1)
    output_df = pd.DataFrame(rows_list)
    #output_df['Abundance ratio sample/contol'] = output_df['Abundance_rank_in_sample'] / output_df['Abundance rank in control']
    #suppression des proteines présentant NaN pour les trois réplicats techniques
    #output_df = output_df.query('Abundance_rank_in_sample == Abundance_rank_in_sample')
    return (output_df)


def update_stringency_avecdict(input_df, stringency):
    with open("./dict_files/dict_file.txt") as dict_file:
        dict = json.load(dict_file)
        for group in dict:
            for sample in dict[group]:
                for i in input_df.index.values:
                    value = input_df.iloc[i]['ratio_{}_{}_control'.format(group, sample)]
                    if math.isnan(value) and value >= stringency:
                        input_df.iloc[i]['Stringency_{}_{}'.format(group, sample)] == stringency
    return(input_df)

def update_stringency(input_df, stringency):
    input_red_data = input_df.filter(regex='ratio_*')
    for col in input_red_data.columns:
        id = col.split('_')
        for i in input_df.index.values:
            value = input_red_data.iloc[i][col]
            if math.isnan(value) == False and value >= stringency:
                input_df.loc[i, 'Stringency_{}_{}'.format(id[1], id[2])] = stringency
    return(input_df)

def select_result(input_df, stringency):
    input_df_data = input_df.filter(regex='^Stringency_*')
    rows_list = []
    for i, row in input_df.iterrows():
        if input_df_data.iloc[i].any() >= stringency:
            #print(input_df_data.iloc[i])
            rows_list = rows_list.append(row)
            #print('row_list', rows_list)

    output_df = pd.concat([rows_list], axis = 0)
    #input_df_data = input_df_data[input_df_data >= stringency]
    #input_df = input_df[]
    return(output_df)


def select_result2(input_df, stringency):
    input_df_data = input_df.filter(regex='^Stringency_*')
    rows_list = []
    for i, row in input_df.iterrows():
        if input_df_data.iloc[i].any() >= stringency:
            #print(input_df_data.iloc[i])
            rows_list = rows_list.append(row)
            #print('row_list', rows_list)

    output_df = pd.concat([rows_list], axis = 0)
    #input_df_data = input_df_data[input_df_data >= stringency]
    #input_df = input_df[]
    return(output_df)



def comparaison_ensembliste(input_df, dict_name):
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        for group in dict_mapping:
            for sample in dict_mapping[group]:
                #compute number of NAs per condition
                abundance_col = input_df.filter(regex = 'Reduced_')

                abundance_col = [col for col in abundance_col.columns.values if group in col]
                abundance_col = [col for col in abundance_col if sample in col]

                if len(abundance_col) > 0:
                    for i in input_df.index.values :
                        values = np.array([x for x in list(input_df.loc[i][abundance_col]) if str(x) != 'nan'])
                        #column = input_df.loc[i, ['Reduced_GR_{}_SA_{}_REP_1'.format(group, sample), 'Reduced_GR_{}_SA_{}_REP_2'.format(group, sample), 'Reduced_GR_{}_SA_{}_REP_3'.format(group, sample)]]
                        input_df.ix[i, 'nb_na_{}_{}'.format(group, sample)] = len(abundance_col)-len(values)

                    dict_sample = {0: 1, 1: 1, 2: 1, 3: 0}
                    dict_ctrl = {0: -1, 1: -1, 2: -1, 3: 0}
                    input_df['Capture_{}_{}'.format(group, sample)] = np.nan

                    if sample == 'Control':
                        #input_df['Capture_{}_Control'.format(group)] = np.nan
                        input_df['Capture_{}_Control'.format(group, sample)] = input_df['nb_na_{}_{}'.format(group, sample)].replace(dict_ctrl)
                    if sample == 'NotaControl1':
                        input_df['Capture_{}_{}'.format(group, sample)] = input_df['nb_na_{}_{}'.format(group, sample)].replace(dict_sample)
                        input_df['Capture_MDA_Control1'] = input_df['nb_na_{}_{}'.format(group, sample)].replace(dict_ctrl)
                    if sample != 'Control':
                        input_df['Capture_{}_{}'.format(group, sample)] = input_df['nb_na_{}_{}'.format(group, sample)].replace(dict_sample)

        for group in dict_mapping:
            for sample in dict_mapping[group]:
                capture_col = input_df.filter(regex='Capture_')
                capture_col = [col for col in capture_col.columns.values if group in col]
                capture_col = [col for col in capture_col if sample in col]
                if len(capture_col) > 0:
                    for i in input_df.index.values:
                        if sample != 'Control':
                            input_df.ix[i, 'Venn_{}_{}'.format(group, sample)] = input_df.iloc[i]['Capture_{}_{}'.format(group, sample)] + input_df.iloc[i]['Capture_{}_Control'.format(group)]
    return (input_df)

def set_comparison(input_df):
    abundance_df = input_df.filter(regex = 'GR')

    reference = [x for x in abundance_df.columns.values if 'reference' in x]
    condition = [x for x in abundance_df.columns.values if 'reference' not in x]

    reference_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in reference]))[0]
    condition_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in condition]))[0]

    for protein in input_df.index.values:
        reference_abundancies = np.array(input_df.loc[protein][reference].map(lambda x: atof(x) if type(x) == str else x))
        condition_abundancies = np.array(input_df.loc[protein][condition].map(lambda x: atof(x) if type(x) == str else x))

        n_NA_ref = np.count_nonzero(np.isnan(reference_abundancies))
        n_NA_cond = np.count_nonzero(np.isnan(condition_abundancies))

        # Proteine spécifique à la capture
        if n_NA_ref == 3:
            if n_NA_cond < 2:
                input_df.loc[protein, 'Venn_{}_{}'.format(condition_name, reference_name)] = 1
                print('hey')
        # Protééine spécifique au controle
        elif n_NA_cond == 3:
            if n_NA_ref < 2:
                input_df.loc[protein, 'Venn_{}_{}'.format(condition_name, reference_name)] = -1
                print('ho')
        # Protéine présente dans les deux conditions
        else:
            input_df.loc[protein, 'Venn_{}_{}'.format(condition_name, reference_name)] = 0

    return(input_df)

def calcul_na(input_df):
    #calculate nb of Nan per condition
    with open("dict_file.txt") as dict_file:
        dict = json.load(dict_file)
        for group in dict:
            for sample in dict[group]:
                for i in input_df.index.values:
                    input_df.ix[i, 'nb_na_{}_{}'.format(group, sample)] = input_df.loc[i, ['GR_{}_SA_{}_REP_1'.format(group, sample), 'GR_{}_SA_{}_REP_2'.format(group, sample),'GR_{}_SA_{}_REP_3'.format(group, sample)]].isna().sum().sum()
    return(input_df)

def convert_na_presence(input_df):
#convert number of NA to presence (1) or absence (0) of proteins
    with open("dict_file.txt") as dict_file:
        dict = json.load(dict_file)
        for group in dict:
            for sample in dict[group]:
                if sample != 'Control':
                    dict = {0 : 1, 1 : 1, 2 : 1, 3 : 0}
                    input_df['capture_{}_{}'.format(group, sample)] = input_df['nb_na_{}_{}'.format(group, sample)].replace(dict)
                elif sample == 'Control':
                    dict_ctrl = {0 : -1, 1 : -1, 2 : -1, 3 : 0}
                            #try :
                    input_df['capture_control_{}'.format(group)] = input_df['nb_na_{}_Control'.format(group)].replace(dict_ctrl)
                            #except AttributeError:
                            #    return input_df.ix[i, 'capture_control_{}'.format(group)] = np.NaN
    return(input_df)

def data_venn_diagram(input_df):
    #create result : -1 for protein in control, 1 for protein in sample and 0 for proteins in both conditions
    print(len(input_df))
    print(input_df.iloc[2]['capture_Vescalin_OB'])
    for i in input_df.index.values:
        input_df.ix[i, 'Venn_OB_Vescalin'] = input_df.iloc[i]['capture_Vescalin_OB'] + input_df.iloc[i]['capture_control_OB']
        input_df.ix[i, 'Venn_OC_Vescalin'] = input_df.iloc[i]['capture_Vescalin_OC'] + input_df.iloc[i]['capture_control_OC']
        input_df.ix[i, 'Venn_OB_Vescalagin'] = input_df.iloc[i]['capture_Vescalagin_OB'] + input_df.iloc[i]['capture_control_OB']
        input_df.ix[i, 'Venn_OC_Vescalgin'] = input_df.iloc[i]['capture_Vescalagin_OC'] + input_df.iloc[i]['capture_control_OC']
    return(input_df)

def venn_diagram(input_df, column, cond, cell):
    set_ctrl = input_df[column].value_counts()
    print(set_ctrl)
    set_ctrl = pd.Series(set_ctrl).values
    venn2(subsets = (set_ctrl[1], set_ctrl[2], set_ctrl[0]), set_labels = ('Control', 'Polyphénol'))
    #venn2([set(input_df['capture_vescalin_OC']), set(input_df['capture_control_OC'])])
    plt.title("Protein overlap between {} probe and control on {}".format(cond, cell))
    plt.savefig('/home/claire/Documents/ProteomX_Benjamin/data/PolyphenolProt/Plots/test_{}_{}.png'.format(cond, cell))


def compute_intern_rank(input_df, dict_name):
    #sort protein according to abundance for each group/sample
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        for group in dict_mapping:
            for sample in dict_mapping[group]:

                for i in input_df.index.values:
                    mean = input_df.loc[i, ['GR_{}_SA_{}_REP_1'.format(group, sample), 'GR_{}_SA_{}_REP_2'.format(group, sample),
                                            'GR_{}_SA_{}_REP_3'.format(group, sample)]].mean()
                    #gmean = input_df.loc[i, ['GR_{}_SA_{}_REP_1'.format(group, sample), 'GR_{}_SA_{}_REP_2'.format(group, sample),
                    #        'GR_{}_SA_{}_REP_3'.format(group, sample)]].mean()
                    input_df.loc[i, 'mean_{}_{}'.format(group, sample)] = mean
        for group in dict_mapping:
            for sample in dict_mapping[group]:
                input_df['Rank_abundance_{}_{}'.format(group, sample)] = input_df['mean_{}_{}'.format(group, sample)].rank()
    print('done')
    return(input_df)

def compute_abundance_rank_gmean(input_df, dict_name):
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_col = json.load(dict_file)
        input_df.reset_index(drop=True, inplace=True)
        for group in dict_col:
            for sample in dict_col[group]:
                abundance_col = 'GR_' + group
                group_col = [ x for x in input_df.columns.values if abundance_col in x ]
                sample_col  = [ x for x in group_col if sample in x ]
                print(group, sample)
                for protein in input_df.index.values:
                    sample_abundancies = np.array(input_df.loc[protein][sample_col].map(lambda x: atof(x) if type(x) == str else x))
                    gmean_sample = stats.gmean(sample_abundancies[~np.isnan(sample_abundancies)])
                    input_df.ix[protein, 'gmean_{}_{}'.format(group, sample)] = gmean_sample
        for group in dict_col:
            for sample in dict_col[group]:
                input_df['Rank_abundance_{}_{}'.format(group, sample)] = input_df['gmean_{}_{}'.format(group, sample)].rank()
    return(input_df)



def abundance_rank(input_df, abundance_df):
    with open("dict_file.txt") as dict_file:
        dict = json.load(dict_file)
        for group in dict:
            for sample in dict[group]:
                input_df['Rank_{}_{]'.format(group, sample)] = input_df['mean_{}_{}'.format(group, sample)].rank()
    return(input_df)



def test_dict(dict):
    for key in dict:
        for s, value in dict[key] :
            print(s, value)

def compute_CV_all(input_df, dict_name):
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        for group in dict_mapping:
            for sample in dict_mapping[group]:
                for i in input_df.index.values:
                    ixcol = input_df.loc[i, ['Reduced_GR_{}_SA_{}_REP_1'.format(group, sample), 'Reduced_GR_{}_SA_{}_REP_2'.format(group, sample), 'Reduced_GR_{}_SA_{}_REP_3'.format(group, sample)]]
                    if ~ixcol.isna().all():
                        if np.isfinite(compute_cv(ixcol)):
                            CV = np.nanstd(ixcol) / np.nanmean(ixcol)
                            input_df.ix[i, 'CV_{}_{}'.format(group, sample)] = CV
    return(input_df)

def compute_CV_unique(input_df, dict_name):
    """ Fonction qui permet de calculer le CV sur un data frame ne contenant qu'un controle vs une ou plusieurs conditions"""
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        abundance_col = input_df.filter(regex = 'Reduced_')
        for group in dict_mapping:
            for sample in dict_mapping[group]:
                # abundance_col.columns.values pour checcker titre de la colonne et non juste abundance_col qui permet d'accéder à l'ensemble des valeurs
                ixcol = [col for col in abundance_col.columns.values if group in col]
                ixcol = [col for col in ixcol if sample in col]

                if len(ixcol) > 0:
                    for protein in input_df.index.values:
                        values_cv = np.array([x for x in list(input_df.loc[protein][ixcol]) if str(x) != 'nan'])
                        if len(values_cv) == 0:
                            continue
                        elif len(values_cv) == 1:
                            input_df.ix[protein, 'CV_{}_{}'.format(group, sample)] = 0
                        else:
                            CV = np.nanstd(values_cv) / np.nanmean(values_cv)
                            input_df.ix[protein, 'CV_{}_{}'.format(group, sample)] = CV
    return(input_df)





def plot_cvs_by_sample_claire(filename, output_dir, input_df, dict_name):
    #plot for samples / see plot_cvs_by sample (Ben)
    #filename un peu différent %Ben ccar séparation des fichiers selon sample et non fichier input
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        for group in dict_mapping:
            for sample in dict_mapping[group]:
                cv_list = []
                col_cv = input_df.filter(regex='CV_')
                col_cv = [col for col in col_cv.columns.values if group in col]
                col_cv = [col for col in col_cv if sample in col]

                if len(col_cv)>0:
                    file_origin = '_'.join(dict_name.split('_')[0:2])
                    filename = '{}_{}_{}'.format(file_origin, group, sample)
                    for protein in input_df.index.values:
                        abundancies = np.array(input_df.loc[protein][col_cv[0]])  # apply(atof))

                        if np.isfinite(abundancies):
                            cv_list.append(abundancies)
                    try:
                        plot_histogram_distribution_by_group(cv_list, group, filename, output_dir, 'CV', 'proteins #', 150, 0.5)
                    except OSError:
                        os.makedirs(output_dir)
                        plot_histogram_distribution_by_group(cv_list, group, filename, output_dir, 'CV', 'proteins #',
                                                             150, 0.5)

                    show_box_plot_distribution(cv_list, group, filename, output_dir)


def plot_abundancies_by_sample_claire(filename, output_dir, input_df, dict_name):
    #filename un peu différent %Ben ccar séparation des fichiers selon sample et non fichier input

    with open("dict_file_{}.txt".format(dict_name)) as dict_file:
        dict = json.load(dict_file)
        for group in dict:
            cv_list = []
            for sample in dict[group]:
                for replicate in dict[group][sample]:
                    for protein in input_df.index.values:
                        filename = 'Abundancies_{}_{}'.format(group, sample)
                        abundancies = np.array(input_df.loc[protein]['Reduced_GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)])  # apply(atof))
                        if np.isfinite(abundancies):
                            cv_list.append(abundancies)
                    plot_histogram_distribution_by_group(cv_list, group, filename, output_dir, 'Abundancies', 'proteins #', 100)
                    show_box_plot_distribution(cv_list, group, filename, output_dir)

def plot_abundancies_rank(filename, output_dir, input_df, dict_name):
    abundance_rank_col = input_df.filter(regex = 'Rank_abundance')
    abundance_rank_control = [col for col in abundance_rank_col if 'Control' in col]
    abundance_rank_sample = [col for col in abundance_rank_col if 'Control' not in col]
    list_rank = []
    for i in input_df.index.values:
            list_rank.append(float(input_df.ix[i, abundance_rank_sample]))
    plot_histogram_distribution(list_rank, filename, output_dir, 'Abundancies relative rank', 'proteins #', 100)

def Insert_row(row_number, df, row_value):
    # Starting value of upper half
    start_upper = 0

    # End value of upper half
    end_upper = row_number

    # Start value of lower half
    start_lower = row_number

    # End value of lower half
    end_lower = df.shape[0]

    # Create a list of upper_half index
    upper_half = [*range(start_upper, end_upper, 1)]

    # Create a list of lower_half index
    lower_half = [*range(start_lower, end_lower, 1)]

    # Increment the value of lower half by 1
    lower_half = [x.__add__(1) for x in lower_half]

    # Combine the two lists
    index_ = upper_half + lower_half

    # Update the index of the dataframe
    df.index = index_

    # Insert a row at the end
    df.loc[row_number] = row_value

    # Sort the index labels
    df = df.sort_index()

    # return the dataframe
    return df


def Insert_row_(row_number, df, row_value):
    # Slice the upper half of the dataframe
    df1 = df[0:row_number]

    # Store the result of lower half of the dataframe
    df2 = df[row_number:]

    # Inser the row in the upper half dataframe
    df1.loc[row_number] = row_value

    # Concat the two dataframes
    df_result = pd.concat([df1, df2])

    # Reassign the index labels
    df_result.index = [*range(df_result.shape[0])]

    # Return the updated dataframe
    return df_result



def compute_reduce_claire(input_df, dict_name):

    with open("dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        input_df_reduced = input_df
        input_df_reduced.reset_index(drop=True, inplace=True)

        for group in dict_mapping:
            for sample in dict_mapping[group]:
                col = []
                dict_column = {}

                for replicate in dict_mapping[group][sample]:
                    dict_column['GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)] = 'Reduced_GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)
                    col.append(input_df['GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)])
                col = pd.concat(col, axis = 1)
                abundancies = pd.DataFrame(columns=col.columns)


                for protein in input_df.index.values:
                    reduced_abundancies = col.loc[protein] / np.nanstd(col.loc[protein])
                    dict_ab = dict(zip(list(col.columns), list(reduced_abundancies.values)))
                    temp = pd.DataFrame([dict_ab])
                    abundancies = pd.concat([abundancies, temp], axis = 0, ignore_index=True)
                abundancies = abundancies.rename(dict_column, axis='columns')

                input_df_reduced = pd.concat([input_df_reduced, abundancies], axis=1)

    return (input_df_reduced)


def compute_reduce_all (input_df, dict_name, metadata_col):
    input_df.reset_index(drop=True, inplace=True)

    if metadata_col[0] == 'Proteomic': #args : nargs '+' => list
        input_df_metadata = input_df.filter(items=['Accession', 'Description'])
    else:
        input_df_metadata = pd.DataFrame(index=input_df.index)
        for i in range(len(metadata_col)):
            input_df_metadata = input_df_metadata.join(input_df[metadata_col[i]])
    input_df_abundance = input_df.filter(regex = 'Rank_*')

    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        abundancies_all = pd.DataFrame()
        for group in dict_mapping:
            for sample in dict_mapping[group]:
                col = []
                dict_column = {}
                for replicate in dict_mapping[group][sample]:
                    dict_column['GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)] = 'Reduced_GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)
                    col.append(input_df['GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)])
                col = pd.concat(col, axis=1)
                col_to_append = pd.DataFrame(col, columns=col.columns)
                abundancies_all = pd.concat([abundancies_all, col_to_append], axis = 1)
                abundancies_all = abundancies_all.rename(dict_column, axis='columns')

    for protein in abundancies_all.index.values:
        abundancies = np.array(abundancies_all.iloc[protein].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        reduced_abundancies = abundancies / np.nanstd(abundancies)
        abundancies_all.iloc[protein] = reduced_abundancies

    input_df = pd.concat([input_df_metadata, input_df_abundance, abundancies_all], axis=1)

    return input_df


def reduction_whole_row(input_df, metadata_col):
    abundancies = input_df.filter(regex='GR')
    if metadata_col[0] == 'Proteomic': #args : nargs '+' => list
        input_df_metadata = input_df.filter(items=['Accession', 'Description'])
    else:
        input_df_metadata = pd.DataFrame(index=input_df.index)
        for i in range(len(metadata_col)):
            input_df_metadata = input_df_metadata.join(input_df[metadata_col[i]])
    input_df_abundance_rank = input_df.filter(regex = 'Rank_*')

    other_col_to_keep = pd.concat([input_df_metadata, input_df_abundance_rank], axis=1)

    for protein in abundancies.index.values:
        abundancies_values = np.array(abundancies.iloc[protein].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        reduced_abundancies = abundancies_values / np.nanstd(abundancies_values)
        abundancies.iloc[protein] = reduced_abundancies

    abundancies = abundancies.add_prefix('Reduced_')

    output_df = pd.concat([other_col_to_keep, abundancies], axis=1)
    print('reduced')
    return output_df


# TODO : ne marche que pour deux groupes
def reduction_row_by_group(input_df, metadata_col):
    abundancies = input_df.filter(regex='VAL')
    if metadata_col[0] == 'Proteomic': #args : nargs '+' => list
        input_df_metadata = input_df.filter(items=['Accession', 'Description'])
    else:
        input_df_metadata = pd.DataFrame(index=input_df.index)
        for i in range(len(metadata_col)):
            input_df_metadata = input_df_metadata.join(input_df[metadata_col[i]])
    #input_df_abundance_rank = input_df.filter(regex = 'Rank_*')


    name_ab = []
    for col in abundancies:
        col_red = '_'.join(col.split('_')[:-1])
        name_ab.append(col_red)
    unique_name_abundance = list(set(name_ab))
    print(unique_name_abundance)
    #other_col_to_keep = pd.concat([input_df_metadata, input_df_abundance_rank], axis=1)
    other_col_to_keep = pd.concat([input_df_metadata], axis=1)

    cond1  = [ x for x in abundancies if unique_name_abundance[0] in x ]
    cond2 = [x for x in abundancies if unique_name_abundance[1] in x]

    abundancies_red_1 = pd.DataFrame(columns=cond1, index=abundancies.index.values)
    abundancies_red_2 = pd.DataFrame(columns=cond2, index=abundancies.index.values)
    for protein in abundancies.index.values:
        cond1_abundancies = np.array(input_df.loc[protein][cond1].map(lambda x: atof(x) if type(x) == str else x))
        reduced_abundancies_cond1 = cond1_abundancies / np.nanstd(cond1_abundancies)

        cond2_abundancies = np.array(input_df.loc[protein][cond2].map(lambda x: atof(x) if type(x) == str else x))
        reduced_abundancies_cond2 = cond2_abundancies / np.nanstd(cond2_abundancies)

        abundancies_red_1.iloc[protein] = reduced_abundancies_cond1
        abundancies_red_2.iloc[protein] = reduced_abundancies_cond2

    red_avundancies = pd.concat([abundancies_red_1, abundancies_red_2], axis=1)
    red_avundancies = red_avundancies.add_prefix('Reduced_')


    output_df = pd.concat([other_col_to_keep, red_avundancies], axis=1)
    return (output_df)


def compute_all_condition_reduce_df_brouillon(input_df, mapping_df, ignored_columns):
    abundancies_cols = input_df.columns.values[ignored_columns:]
    all_abundances = input_df[:][abundancies_cols]
    #print(all_abundances)

    column_groups = build_condition_mapping_dict(mapping_df,abundancies_cols)
    print(column_groups)
    reduced_df = pd.DataFrame(columns=all_abundances.columns.values, index=all_abundances.index)
    all_groups = [x for x in list(column_groups.keys())]
    print(all_groups)
    #sys.exit()
    for protein in all_abundances.index.values:
        col_idx=[]
        for group in all_groups:
            col_idx += get_group_col_index(column_groups[group])
        print(col_idx)
        abundancies = np.array(all_abundances.loc[protein][col_idx].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))
        print(abundancies)
            # here reduce abundancies by std for given group
        reduced_abundancies = abundancies / np.nanstd(abundancies)
        reduced_df.loc[protein][col_idx] = reduced_abundancies
    #print(reduced_df)
    return reduced_df

def run_ttest_claire(input_df, max_nan_by_group):
    ttest_df = pd.DataFrame(columns=['Description', 'Accession', 'pvalue', 'padj', 'Log2FoldChange'], index=input_df.index)
    with open("dict_file.txt") as dict_file:
        dict_mapping = json.load(dict_file)
        for group in dict_mapping:
            for sample in dict_mapping[group]:
                non_control_col = []
                control_col = []
                if sample != 'Control':
                    for replicate in dict_mapping[group][sample]:
                        non_control_col.append(input_df['Reduced_GR_{}_SA_{}_REP_{}'.format(group, sample, replicate)])
                        control_col.append(input_df['Reduced_GR_{}_SA_Control_REP_{}'.format(group, replicate)])
                    non_control_col = pd.concat(non_control_col, axis=1)
                    control_col = pd.concat(control_col, axis = 1)
                    for protein in input_df.index.values:
                        non_control_group = non_control_col.iloc[protein]
                        #print(non_control_group)
                        control_group = control_col.iloc[protein]

                        if (np.count_nonzero(pd.isnull(control_group)) < (len(control_group) / 100) * max_nan_by_group) and (np.count_nonzero(pd.isnull(non_control_group)) < (len(non_control_group) / 100) * max_nan_by_group):
                            stat, p_value = stats.ttest_ind(non_control_group, control_group, nan_policy='omit')
                            ttest_df.loc[protein]['pvalue'] = p_value
                            ttest_df.loc[protein]['Log2FoldChange'] = np.log2(input_df.ix[protein, 'ratio_{}_{}_control'.format(group, sample)].mean())
                            #ttest_df.loc[protein]['Log2FoldChange'] = np.log2(input_df.ix[protein, 'ratio_{}_{}_control'.format(group, sample)].mean(skipna=True))
                            ttest_df.loc[protein]['Description'] = input_df.ix[protein]["Description"]
                            ttest_df.loc[protein]['Accession'] = input_df.ix[protein]["Accession"]

    rej, pval_corr = smm.multipletests(ttest_df['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    ttest_df['padj'] = pval_corr
    return (ttest_df)

def run_ttest_claire_df_temp(input_df, max_nan_by_group):

    ttest_df = pd.DataFrame(columns=['Accession', 'pvalue', 'padj', 'Log2FoldChange'], index=input_df.index)
    non_control_col = input_df.filter(regex = '^Reduced_GR_(\S*)_SA_(?!Control).*')
    control_col = input_df.filter(regex='^Reduced_GR_(\S*)_SA_Control_*')
    input_df = input_df.reset_index()
    for protein in input_df.index.values:
        non_control_group = non_control_col.iloc[protein]
        control_group = control_col.iloc[protein]

        ttest_df.loc[protein]['Log2FoldChange'] = np.log2(float(input_df.iloc[protein][input_df.columns.str.contains('^ratio_*')][0]))
        if ((np.count_nonzero(pd.isnull(control_group))) / (len(control_group)) < (len(control_group) / 100) * max_nan_by_group) and ((np.count_nonzero(pd.isnull(non_control_group))) / (len(non_control_group)) < (len(non_control_group) / 100) * max_nan_by_group):
            stat, p_value = stats.ttest_ind(non_control_group, control_group, nan_policy='omit')
            ttest_df.loc[protein]['pvalue'] = p_value
            ttest_df.loc[protein]['Accession'] = input_df.ix[protein]["Accession"]
    rej, pval_corr = smm.multipletests(ttest_df['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    ttest_df['padj'] = pval_corr

    return (ttest_df)

def ttest(input_df):

    ttest_df = pd.DataFrame(columns=['Accession', 'pvalue', 'padj', 'Log2FoldChange'], index=input_df.index)

    abundancies_col = input_df.filter(regex='Reduced_')
    abundancies_control = [col for col in abundancies_col.columns.values if 'Control' in col]
    abundancies_sample = [col for col in abundancies_col.columns.values if 'Control' not in col]


    for protein in input_df.index.values:

        non_control_group = input_df.loc[protein, abundancies_sample]
        non_control_group = non_control_group.astype('float64')

        control_group = input_df.loc[protein, abundancies_control]
        control_group = control_group.astype('float64')

        if non_control_group.isnull().sum() == 3 or control_group.isnull().sum() == 3: ### avoid proteins present only in one condition
            continue
        ttest_df.loc[protein]['Log2FoldChange'] = np.log2(float(input_df.iloc[protein][input_df.columns.str.contains('^ratio_*')][0]))

        stat, p_value = stats.ttest_ind(non_control_group, control_group, nan_policy='omit')
        ttest_df.loc[protein]['pvalue'] = p_value
        ttest_df.loc[protein]['Accession'] = input_df.ix[protein]["Accession"]
    rej, pval_corr = smm.multipletests(ttest_df['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    ttest_df['padj'] = pval_corr
    return (ttest_df)

def run_ttest_claire_df_secpnotcontrool(input_df, max_nan_by_group):
    ttest_df = pd.DataFrame(columns=['Description', 'Accession', 'pvalue', 'padj', 'Log2FoldChange'], index=input_df.index)
    non_control_col = input_df.filter(regex = '^Reduced_GR_MDA_SA_Resveratrol_*')
    control_col = input_df.filter(regex='^Reduced_GR_MDA_SA_NotaControl1_*')



    for protein in input_df.index.values:
        non_control_group = non_control_col.iloc[protein]
        control_group = control_col.iloc[protein]
        if (np.count_nonzero(pd.isnull(control_group)) < (len(control_group) / 100) * max_nan_by_group) and (np.count_nonzero(pd.isnull(non_control_group)) < (len(non_control_group) / 100) * max_nan_by_group):
            stat, p_value = stats.ttest_ind(non_control_group, control_group, nan_policy='omit')
            ttest_df.loc[protein]['pvalue'] = p_value
            #print(input_df.iloc[protein][input_df.columns.str.contains('^ratio_*')])
            #print(input_df.iloc[protein][input_df.columns.str.contains('^ratio_*')][0])
            ttest_df.loc[protein]['Log2FoldChange'] = np.log2(float(input_df.iloc[protein][input_df.columns.str.contains('^ratio_*')][0]))
            ttest_df.loc[protein]['Accession'] = input_df.ix[protein]["Accession"]

    rej, pval_corr = smm.multipletests(ttest_df['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    ttest_df['padj'] = pval_corr
    return (ttest_df)


def run_ttest2(input_df, ratio_df, abundancies_cols, abundancies_control_cols,max_nan_by_group):
    ttest_df = pd.DataFrame(columns=['pvalue', 'padj', 'Log2FoldChange'], index=input_df.index)

    for protein in input_df.index.values:
        non_control_group_abundancies = np.array(input_df.loc[protein][abundancies_cols].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))

        control_group_abundancies = np.array(input_df.loc[protein][abundancies_control_cols].map(lambda x: atof(x) if type(x) == str else x))  # apply(atof))

        if (np.count_nonzero(pd.isnull(control_group_abundancies)) < (len(control_group_abundancies) / 100) * max_nan_by_group) and (np.count_nonzero(pd.isnull(non_control_group_abundancies)) < (len(non_control_group_abundancies) / 100) * max_nan_by_group):

            stat, p_value = stats.ttest_ind(non_control_group_abundancies, control_group_abundancies, nan_policy='omit')
            #print(p_value)
            ttest_df.loc[protein]['pvalue'] = p_value
            ttest_df.loc[protein]['Log2FoldChange'] = np.log2(ratio_df.ix[protein].mean(skipna=True))
            #non_control_group_mean_ratio=np.mean(np.array(input_df.loc[protein][abundancies_cols].map(lambda x: atof(x) if type(x) == str else x)))
            #control_group_mean_ratio = np.mean(np.array(input_df.loc[protein][abundancies_control_cols].map(lambda x: atof(x) if type(x) == str else x)))
            #ttest_df.loc[protein]['Log2FoldChange'] = non_control_group_mean_ratio/control_group_mean_ratio
            #print(non_control_group_mean_ratio/control_group_mean_ratio)


    rej, pval_corr = smm.multipletests(ttest_df['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    ttest_df['padj'] = pval_corr
    #print(ttest_df)
    return ttest_df







def filter_by_CV(input_df, cv_threshold):
    col_to_check = input_df.filter(regex = '^CV_*')
    if 'CV_MDA_Control1' in col_to_check.columns:
        col_to_check = col_to_check.drop('CV_MDA_Control1', axis = 1)
    print(col_to_check.columns)
    for i in col_to_check.index.values:
        print(col_to_check.iloc[i])
        print(cv_threshold)
        if float(col_to_check.iloc[i]).any() < cv_threshold:
            print('nothing to be done')
        else:
            input_df = input_df.drop([i], axis=0)

    return(input_df)

def update_pvalues_two_sided(input_df):
    ratio_col = input_df.filter(regex = '^ratio_*')

    for i, row in ratio_col.iterrows():
        if input_df.ix[i][ratio_col.columns[0]] != 1000 and input_df.ix[i][ratio_col.columns[0]] != 0.001:
            continue
        #print(input_df.ix[i][ratio_col.columns].values)
        elif input_df.ix[i][ratio_col.columns[0]] == 1000:
            input_df.ix[i, 'pvalue'] = 0
            input_df.ix[i, 'padj'] = 0
        elif input_df.ix[i][ratio_col.columns[0]] == 0.001:
            input_df.ix[i, 'pvalue'] = 0
            input_df.ix[i, 'padj'] = 0
    return(input_df)

def update_pvalues_right_tailed(input_df):
    ratio_col = input_df.filter(regex = '^ratio_*')
    ratio = ratio_col.columns.tolist()[0]
    for i, row in ratio_col.iterrows():
        if input_df.ix[i][ratio_col.columns[0]] != 1000 and input_df.ix[i][ratio_col.columns[0]] != 0.001:
            continue
        elif input_df.ix[i][ratio_col.columns[0]] == 1000:
            input_df.ix[i, 'pvalue'] = 0
            #input_df.ix[i, 'padj'] = 0
        elif input_df.ix[i][ratio_col.columns[0]] == 0.001:
            input_df.ix[i, 'pvalue'] = 1
            #input_df.ix[i, 'padj'] = 1
    return(input_df)

def update_log2foldchange(input_df):
    ratio_col = input_df.filter(regex = '^ratio_*')
    for i, row in ratio_col.iterrows():
        if input_df.ix[i][ratio_col.columns].values == 1000:
            input_df.ix[i, 'Log2FoldChange'] = 10
    return(input_df)

#TODO : fonction completement con
def update_ratio_distrib(input_df):
    ratio_col = input_df.filter(regex = '^ratio_*')
    for i, row in ratio_col.iterrows():
        if input_df.ix[i][ratio_col.columns].values == 1000:
            input_df.ix[i, ratio_col] = 1000
    return(input_df)

def filtration_CV(input_df, dict_name):
    with open("./dict_files/dict_file_{}.txt".format(dict_name)) as dict_file:
        dict_mapping = json.load(dict_file)
        for group in dict_mapping:
            for sample in dict_mapping[group]:
                if 'CV_{}_{}'.format(group, sample) in input_df.columns:
                    col_cv = 'CV_{}_{}'.format(group, sample)
                    input_df = input_df[input_df[col_cv] < 0.5]
    return(input_df)



def run_pnorm_test_claire(input_df, type):
    if type == 'ratio':
        ratio_values = input_df.filter(regex  = '^[rR]atio_')
        loc_ratio = input_df.columns.get_loc(ratio_values.columns[0])
        ratio_name = input_df.columns.values.tolist()[loc_ratio]

    test_df = input_df.copy()

    test_df[ratio_name] = np.where(test_df[ratio_name] == 1000, np.nan, test_df[ratio_name])
    test_df = test_df.dropna(subset = [ratio_name], axis = 0)
    #list_z = stats.zscore([np.log2(x) for x in test_df[ratio_name].values])
    list_z = [np.log2(x) for x in test_df[ratio_name].values]


    df_z = pd.DataFrame(columns=['Accession', 'Description','pnorm_ratio', 'Log2FoldChange', 'pvalue', 'padj'], index=test_df.index)

    df_z['pnorm_ratio'] = list_z / np.mean(list_z)
    #df_z['ratio'] = list_z
    df_z['Log2FoldChange'] = [np.log2(x) for x in test_df[ratio_name].values]
    df_z['pvalue'] = norm.pdf(df_z['pnorm_ratio'], loc=np.mean(df_z['pnorm_ratio']), scale=np.std(df_z['pnorm_ratio']))
    #df_z['pvalue'] = norm.pdf(df_z['z-score'])
    for protein in test_df.index.values:
    #     print(df_z.ix[protein]['z-score'])
         df_z.loc[protein, 'Accession'] = test_df.loc[protein, 'Accession']
    #     df_z.loc[protein,'Description'] = test_df.loc[protein, "Description"]
    #     df_z.loc[protein, 'pvalue'] = norm.pdf(df_z.ix[protein]['z-score'])
    #     #df_z.loc[protein, 'pvalue'] = norm.pdf(df_z.ix[protein]['z-score'], loc=np.mean(df_z.ix[protein]['z-score']))
    #     #df_z.loc[protein,'pvalue'] = norm.pdf(df_z.ix[protein]['z-score'], loc=np.mean(df_z.ix[protein]['z-score']), scale=np.std(df_z.ix[protein]['z-score']))
    #     print(df_z.loc[protein,'pvalue'])
    df_z = df_z.sort_values(by='pvalue')
    rej, pval_corr = smm.multipletests(df_z['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
    df_z['padj'] = pval_corr

    return df_z


def get_protein_number(stats_df, output_df, filename, rule_name):
    stats_df.loc[rule_name, filename] = len(output_df)
    return(stats_df)

    #indexi =  np.where(input_df['Accession'] is in intersection)
    #row_list = list()
    #for protein in input_df.index.values:
    ##    if input_df.loc[protein, 'Accession'] in intersection:
    #        row_list.append(input_df.iloc[protein])
    #result_df = pd.DataFrame(row_list)
    #stats_df[filename] =
    #suivre numéro d'accession des protéines perdues

    #ouvrir fichier de suivi du dataset = un pour parti préparation + un pour analyse ?
    #créer une colonne/updater une colonne correspondant au sample étudié
    #faire différence protéines présentent au début et à la fin = interesction  ?
    #update colonne avec numééro d'accesssion, description et "raison" = rule name

    #suivre nombre de protéines
    #écrire sur deuxième fichier en groupant par 'rule name' pour obtenir nombre de protééines perdues
    #produire graph montrant pour chaque sample ddiminution

    #intersection = set(input_df['Accession']).intersection(set(output_df['Accession']))







# Create models from data
def best_fit_distribution(data, bins=200):
    matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
    matplotlib.style.use('ggplot')
    """Model data by finding best fit distribution to data"""
    #Get histogram of original data
    y, x = np.histogram(data, bins=bins, density=True)

    x = (x + np.roll(x, -1))[:-1] / 2.0



    #Distributions to check
    # DISTRIBUTIONS = [
    #     st.alpha,st.anglit,st.arcsine,st.beta,st.betaprime,st.bradford,st.burr,st.cauchy,st.chi,st.chi2,st.cosine,
    #     st.dgamma,st.dweibull,st.erlang,st.expon,st.exponnorm,st.exponweib,st.exponpow,st.f,st.fatiguelife,st.fisk,
    #     st.foldcauchy,st.foldnorm,st.frechet_r,st.frechet_l,st.genlogistic,st.genpareto,st.gennorm,st.genexpon,
    #     st.genextreme,st.gausshyper,st.gamma,st.gengamma,st.genhalflogistic,st.gilbrat,st.gompertz,st.gumbel_r,
    #     st.gumbel_l,st.halfcauchy,st.halflogistic,st.halfnorm,st.halfgennorm,st.hypsecant,st.invgamma,st.invgauss,
    #     st.invweibull,st.johnsonsb,st.johnsonsu,st.ksone,st.kstwobign,st.laplace,st.levy,st.levy_l,st.levy_stable,
    #     st.logistic,st.loggamma,st.loglaplace,st.lognorm,st.lomax,st.maxwell,st.mielke,st.nakagami,st.ncx2,st.ncf,
    #     st.nct,st.norm,st.pareto,st.pearson3,st.powerlaw,st.powerlognorm,st.powernorm,st.rdist,st.reciprocal,
    #     st.rayleigh,st.rice,st.recipinvgauss,st.semicircular,st.t,st.triang,st.truncexpon,st.truncnorm,st.tukeylambda,
    #     st.uniform,st.vonmises,st.vonmises_line,st.wald,st.weibull_min,st.weibull_max,st.wrapcauchy
    # ]
    DISTRIBUTIONS = [
        st.alpha, st.anglit, st.arcsine, st.beta, st.betaprime, st.bradford, st.burr, st.cauchy, st.chi, st.chi2,
        st.cosine,
        st.dgamma, st.dweibull, st.erlang, st.expon, st.exponnorm, st.exponweib, st.exponpow, st.f, st.fatiguelife,
        st.foldcauchy, st.foldnorm, st.frechet_r, st.frechet_l, st.genlogistic, st.genpareto, st.gennorm, st.genexpon,
        st.genextreme, st.gausshyper, st.gamma, st.gengamma, st.genhalflogistic, st.gilbrat, st.gompertz, st.gumbel_r,
        st.gumbel_l, st.halfcauchy, st.halflogistic, st.halfnorm, st.halfgennorm, st.hypsecant, st.invgamma,
        st.invgauss,
        st.invweibull, st.johnsonsb, st.johnsonsu, st.ksone, st.kstwobign, st.laplace, st.levy, st.levy_l,st.fisk,
        st.logistic, st.loggamma, st.loglaplace, st.lognorm, st.lomax, st.maxwell, st.mielke, st.nakagami, st.ncx2,
        st.ncf,
        st.nct, st.norm, st.pareto, st.pearson3, st.powerlaw, st.powerlognorm, st.powernorm, st.rdist, st.reciprocal,
        st.rayleigh, st.rice, st.recipinvgauss, st.semicircular, st.t, st.triang, st.truncexpon, st.truncnorm,
        st.tukeylambda,
        st.uniform, st.vonmises, st.vonmises_line, st.wald, st.weibull_min, st.weibull_max, st.wrapcauchy
    ]

    # Best holders
    best_distribution = st.norm
    best_params = (0.0, 1.0)
    best_sse = np.inf

    # Estimate distribution parameters from data
    for distribution in DISTRIBUTIONS:
        # Try to fit the distribution
        try:
            # Ignore warnings from data that can't be fit
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')

                # fit dist to data
                params = distribution.fit(data)

                # Separate parts of parameters
                arg = params[:-2]
                loc = params[-2]
                scale = params[-1]

                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse = np.sum(np.power(y - pdf, 2.0))
                # identify if this distribution is better
                if best_sse > sse > 0:
                    best_distribution = distribution
                    best_params = params
                    best_sse = sse

        except Exception:
            pass

    return (best_distribution.name, best_params)

def make_pdf(dist, params, size=10000):
    """Generate distributions's Probability Distribution Function """

    # Separate parts of parameters
    arg = params[:-2]
    loc = params[-2]
    scale = params[-1]

    # Get sane start and end points of distribution
    start = dist.ppf(0.01, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
    end = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)

    # Build PDF and turn into pandas Series
    x = np.linspace(start, end, size)
    y = dist.pdf(x, loc=loc, scale=scale, *arg)
    pdf = pd.Series(y, x)

    return pdf

def get_best_fit(input_array, out_file):
    matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
    matplotlib.style.use('ggplot')
    """Return the best fit distribution to data and its parameters"""

    # Load data
    data = pd.Series(input_array)

    # Find best fit distribution
    best_fit_name, best_fit_params = best_fit_distribution(data, 200)
    best_dist = getattr(st, best_fit_name)

    # Make PDF with best params
    pdf = make_pdf(best_dist, best_fit_params)

    # Display
    # ax.set_ylim(dataYLim)
    plt.figure(figsize=(12,8))
    #ax =
    # below "density" should be replaced by "normed" is matplotlib < 2.2
    #ax = data.plot(kind='hist', bins=50, density=True, alpha=0.5, label='Data', legend=True)
    #pdf.plot(lw=2, label='PDF', legend=True, ax = ax)

    # #plot methode alternative https://stackoverflow.com/questions/6620471/fitting-empirical-distribution-to-theoretical-ones-with-scipy-python
    # plt.figure(figsize=(12, 8))
    # ax = data.plot(kind='hist', bins=50, density=True, alpha=0.5, label = 'Data', legend = True)
    # # Save plot limits
    # TODO : checker effet bin auto
    plt.hist(data,bins=150, density=True, alpha = 0.5, label='Data')
    plt.plot(pdf, lw=2, label='PDF')
    plt.legend(loc='upper right', shadow=True, fontsize='x-large')



    param_names = (best_dist.shapes + ', loc, scale').split(', ') if best_dist.shapes else ['loc', 'scale']
    param_str = ', '.join(['{}={:0.2f}'.format(k,v) for k,v in zip(param_names, best_fit_params)])
    dist_str = '{}({})'.format(best_fit_name, param_str)
    plt.title(u'Best fit distribution \n' + dist_str)
    plt.xlabel(u'ratio')
    plt.ylabel('frequency')
    # ax.set_title(u'Best fit distribution \n' + dist_str)
    # ax.set_xlabel(u'ratio')
    # ax.set_ylabel('frequency')
    plt.savefig(out_file)
    return best_fit_name, param_str


def list_powerset2(lst):
    return reduce(lambda result, x: result + [subset + [x] for subset in result],
                      lst, [[]])

### fonction Macha : takes two vectors with 2 values min and max
def overlaps(a, b):
    return min(a[1], b[1]) - max(a[0], b[0])

### overlaps plus large : takes two array and return overlaps
def overlap_min_max(x, y):
    a = [np.nanmin(x), np.nanmax(x)]
    b = [np.nanmin(y), np.nanmax(y)]

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    overlap = np.nanmin([a[1], b[1]]) - np.nanmax([a[0], b[0]])

    return(overlap)

def overlap_max_min(x, y):
    a = [np.nanmin(x), np.nanmax(x)]
    b = [np.nanmin(y), np.nanmax(y)]

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    overlap =  np.nanmax([a[0], b[0]]) - np.nanmin([a[1], b[1]])

    return(overlap)

def overlap_oriente(capture, control):
    overlap = np.nanmin(capture) - np.nanmax(control)
    return(overlap)

def filtering_distribution(input_df, overlap = None, pvalue = None, padj = None, ratio = None, log2FoldChange = None):
    selected_df = pd.DataFrame(columns=['Accession', 'ratio', 'my_score', 'zscore', 'pvalue'])
    """
    Sélection possible sur :
    - ratio
    - log2FC
    - pvalue
    - p-adj
    - overlap
    """
    #list_params = [overlap, pvalue, padj, ratio, log2FoldChange]
    #relevant_params = [x for x in list_params if x != None]


    return(selected_df)


def adding_overlap(input_df, selected_df, overlap):
    """ à simplifier"""
    ratio_col = input_df.filter(regex='^[rR]atio_')
    loc_ratio = input_df.columns.get_loc(ratio_col.columns[0])
    ratio_name = input_df.columns.values.tolist()[loc_ratio]

    for protein in input_df.index.values:
        if input_df.loc[protein]['overlap'] > overlap :
            continue
        selected_df.loc[protein] = [input_df['Accession'], input_df.loc[protein][ratio_name],
                                    input_df.loc[protein]['my_score'], input_df.loc[protein]['zscore'],
                                    input_df.loc[protein]['pvalue']]
    return(selected_df)


def adding_pvalue(input_df, selected_df, pvalue):
    """ à simplifier"""
    ratio_col = input_df.filter(regex='^[rR]atio_')
    loc_ratio = input_df.columns.get_loc(ratio_col.columns[0])
    ratio_name = input_df.columns.values.tolist()[loc_ratio]

    for protein in input_df.index.values:
        if input_df.loc[protein]['pvalue'] > pvalue:
            continue
        selected_df.loc[protein] = [input_df['Accession'], input_df.loc[protein][ratio_name],
                                    input_df.loc[protein]['my_score'], input_df.loc[protein]['zscore'],
                                    input_df.loc[protein]['pvalue']]
    return (selected_df)

def adding_ratio_pos(input_df, selected_df, ratio):
    """ à simplifier"""
    ratio_col = input_df.filter(regex='^[rR]atio_')
    loc_ratio = input_df.columns.get_loc(ratio_col.columns[0])
    ratio_name = input_df.columns.values.tolist()[loc_ratio]

    for protein in input_df.index.values:
        if input_df.loc[protein][ratio_name] < ratio:
            continue
        selected_df.loc[protein] = [input_df['Accession'], input_df.loc[protein][ratio_name],
                                    input_df.loc[protein]['my_score'], input_df.loc[protein]['zscore'],
                                    input_df.loc[protein]['pvalue']]
    return (selected_df)

def adding_ratio_neg(input_df, selected_df, ratio):
    """ à simplifier"""
    ratio_col = input_df.filter(regex='^[rR]atio_')
    loc_ratio = input_df.columns.get_loc(ratio_col.columns[0])
    ratio_name = input_df.columns.values.tolist()[loc_ratio]

    for protein in input_df.index.values:
        if input_df.loc[protein][ratio_name] > ratio:
            continue
        selected_df.loc[protein] = [input_df['Accession'], input_df.loc[protein][ratio_name],
                                    input_df.loc[protein]['my_score'], input_df.loc[protein]['zscore'],
                                    input_df.loc[protein]['pvalue']]
    return (selected_df)


def filtering_overlap(input_df, overlap):
    #-1 : score for all proteins with complete overlap
    input_df = input_df[input_df['overlap'] != -1]

    if overlap==0:
        input_df = input_df[input_df['overlap'] == overlap]
    if overlap != 0:
        input_df = input_df[input_df['overlap'] < overlap]
    return(input_df)

def filtering_overlap_min_max(input_df, overlap):
    input_df = input_df[input_df['overlap'] >= overlap]
    return(input_df)



def filtering_pvalue(input_df, pvalue):
    input_df = input_df[input_df['pvalue'] < pvalue]
    return (input_df)

def filtering_padj(input_df, padj):
    input_df = input_df[input_df['padj'] < padj]
    return (input_df)

def filtering_ratio_inf(input_df, ratio_inf):
    ratio_col = input_df.filter(regex='^[rR]atio_')
    loc_ratio = input_df.columns.get_loc(ratio_col.columns[0])
    ratio_name = input_df.columns.values.tolist()[loc_ratio]
    input_df = input_df[input_df[ratio_name] < ratio_inf]
    return (input_df)

def filtering_ratio_sup(input_df, ratio_sup):
    ratio_col = input_df.filter(regex='^[rR]atio_')
    loc_ratio = input_df.columns.get_loc(ratio_col.columns[0])
    ratio_name = input_df.columns.values.tolist()[loc_ratio]
    input_df = input_df[input_df[ratio_name] > ratio_sup]
    return (input_df)

def flatten(lst):
	return sum( ([x] if not isinstance(x, list) else flatten(x)
		     for x in lst), [] )

"""TODO"""
def checking(gomf, goid):
    if goid in gomf:
        print('yes')
    else:
        print('no')
    return()



def isfloat(x):
    try:
        float(x)
    except:
        return False
    else:
        return True

def plot_histogram_distribution_by_group(list,group,filename,filepath, type, ylabel,bins, cv_threshold=None):
    plt.hist(np.array(list),bins=bins)
    plt.xlabel(type+' values')
    plt.ylabel(ylabel)
    if cv_threshold:
        plt.axvline(cv_threshold, color='k', linestyle='dashed', linewidth=1)
    plt.title(filename+ '_' + type +'_distribution')
    # print('filepath', filepath)
    # print('filename', filename)
    plt.savefig(filepath+ '/' + filename+ '_'+ 'histogram' + ".png")
    plt.close()

def plot_histogram_distribution(v_list,filename,filepath, type, ylabel,bins,log=False, axvline = None):
    plt.hist(list(v_list),bins=bins)
    plt.xlabel(type+' values')
    plt.ylabel(ylabel)
    if axvline != None:
        plt.axvline(axvline, color='red', linestyle='dashed', linewidth=1)
    if log:
        plt.yscale('log')
        plt.xscale('log')
        plt.savefig(filepath+ '/' + filename+ '_'+ 'histogram_log'+ ".png")
        plt.title(type + ' log distribution')
    else:
        plt.title(type + ' distribution')
        plt.savefig(filepath+ '/' + filename+ '_'+ 'histogram'+ ".png")
    plt.close()


def show_box_plot_distribution(cv_list,group,filename,filepath):
    plt.boxplot(np.array(cv_list))
    plt.xlabel('CV values')
    plt.ylabel('CV #')
    plt.title(filename+ ' CV_distribution')
    plt.savefig(filepath+ '/' + filename+ ' CV_boxplot for' + ".png")
    plt.close()


def build_heatmap(data,output_file):
    # retrieve heatmap data
    xlabels = data.columns.values
    ylabels = data.index.values
    plt.figure(figsize=(30, 20))
    sns.set(font_scale=0.7)
    ax = sns.heatmap(data, xticklabels=xlabels, yticklabels=ylabels, cbar=True, cmap="coolwarm")
    plt.savefig(output_file)
    plt.close()

def build_clustermap(data,output_file):

    xlabels = data.columns.values
    ylabels = data.index.values
    #lut = dict(zip(group_list.unique(), "rbg"))
    plt.figure(figsize=(30, 20))
    sns.set(font_scale=0.7)
    g = sns.clustermap(data,cmap="coolwarm",xticklabels=xlabels, yticklabels=ylabels,metric="euclidean",method="ward")

    plt.savefig(output_file)
    plt.close()


def plot_scored_df(df, threshold_type, threshold_other,biomarked_type,output_fig):
    x_good = []
    y_good = []
    x_bad = []
    y_bad = []
    for protein in df.index.values:
        best_in_type = df.loc[protein]['pos_in_type']
        in_other = df.loc[protein]['neg_in_other']
        if df.loc[protein]['neg_in_type'] > best_in_type:
            best_in_type = df.loc[protein]['neg_in_type']
            in_other = df.loc[protein]['pos_in_other']
        if best_in_type > threshold_type and in_other > threshold_other:
            x_good.append(best_in_type)
            y_good.append(in_other)
        else:
            x_bad.append(best_in_type)
            y_bad.append(in_other)

    data = [[x_good, y_good], [x_bad, y_bad]]
    colors = ("green", "red")
    groups = ("selected", "rejected")

    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, facecolor="1.0")

    for data, color, group in zip(data, colors, groups):
        x, y = data
        ax.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        plt.title("Scatterplot of opposite signes for samples in " + biomarked_type)
        plt.legend(loc=1, fontsize=10)
        plt.xlabel("Majority sign proportion in " + biomarked_type)
        plt.ylabel('Opposite sign proportion in others')
        plt.savefig(output_fig)

def run_gsea_propre(gene_list,output_dir,output_file):
    #print gp.__version__
    #names = gp.get_library_name()

    glist=list(gene_list)
    output_file = output_file.split('.')[0]
    if len(glist) > 0:
        result_path = str(output_dir + '/' + output_file + "_BP_gsea_result")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_Biological', gene_sets='GO_Biological_Process_2018', outdir=result_path, cutoff=0.05, figsize=(8, 8))
        print(enrichr_results)
        print(enrichr_results.res2d.columns.values)
        #print('enrich GO biological processs')
        dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_BP")
        df=pd.read_csv(result_path+"/GO_Biological_Process_2018.GO_Biological.enrichr.reports.txt",index_col=0,sep='\t')
        #print(df['Combined Score'])
        #df = df.drop(['P-value','Adjusted P-value','Old P-value','Old Adjusted P-value','Z-score','Combined Score'], axis=1)
        df=df.head(10)
        df = df.sort_values(by = 'Adjusted P-value')
        df.to_csv(result_path+"/GO_Biological_Process_2018_"+get_filename(output_file)+".csv",sep='\t')


        result_path = str(output_dir + '/' + output_file + "_CC_gsea_result")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_CC', gene_sets='GO_Cellular_Component_2018', outdir=result_path, cutoff=0.05, figsize=(8, 8))
        dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_CC")
        df = pd.read_csv(result_path + "/GO_Cellular_Component_2018.GO_CC.enrichr.reports.txt", index_col=0,sep='\t')
        #df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        df = df.sort_values(by = 'Adjusted P-value')
        #df = df.head(10)
        df.to_csv(result_path + "/GO_Cellular_Component_2018_"+get_filename(output_file)+".csv", sep='\t')


        result_path = str(output_dir + '/' + output_file + "_MF_gsea_result")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_Molecular', gene_sets='GO_Molecular_Function_2018', outdir=result_path, cutoff=0.05, figsize=(8, 8))
        dotplot_claire(enrichr_results.res2d, ofname=result_path+'/' +output_file+"_MF")
        df = pd.read_csv(result_path + "/GO_Molecular_Function_2018.GO_Molecular.enrichr.reports.txt", index_col=0,sep='\t')
        #df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        df = df.sort_values(by='Adjusted P-value')
        df = df.head(10)
        df.to_csv(result_path + "/GO_Molecular_Function_2018_"+get_filename(output_file)+".csv", sep='\t')

def run_gsea_local(gene_list,output_dir,output_file):
    glist=list(gene_list)
    output_file = output_file.split('.')[0]
    if len(glist) > 0:
        gmt_BP_no_iea = "/home/claire/Documents/ProteomX_Benjamin/data/annotation_data/mmusculus/MOUSE_GO_bp_no_GO_iea_symbol.gmt"
        result_path = str(output_dir + '/' + output_file + "_BP_gsea_result_no_iea")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_BP',
                                     gene_sets=gmt_BP_no_iea, background = 22073, outdir=result_path,
                                     cutoff=0.05, figsize=(8, 8))
        print(enrichr_results)
        print(enrichr_results.res2d.columns.values)
        print('enrich GO biological processs')
        #dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_BP")
        # df = pd.read_csv(result_path + "/GO_Biological_Process_no_iea.GO_Biological.enrichr.reports.txt", index_col=0,
        #                  sep='\t')
        # # df = df.drop(['P-value','Adjusted P-value','Old P-value','Old Adjusted P-value','Z-score','Combined Score'], axis=1)
        # df = df.head(10)
        # df = df.sort_values(by='Adjusted P-value')
        # df.to_csv(result_path + "/GO_Biological_Process_no_iea.GO_Biological.enrichr.reports.csv", sep='\t')

        gmt_BP_iea = "/home/claire/Documents/ProteomX_Benjamin/data/annotation_data/mmusculus/MOUSE_GO_bp_with_GO_iea_symbol.gmt"
        result_path = str(output_dir + '/' + output_file + "_BP_gsea_result_iea")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_BP',
                                     gene_sets=gmt_BP_iea, background = 'mmusculus_gene_ensembl', outdir=result_path,
                                     cutoff=0.05, figsize=(8, 8))
        print('enrich GO biological processs')
        # dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_BP")
        # df = pd.read_csv(result_path + "/GO_Biological_Process_iea.GO_Biological.enrichr.reports.txt", index_col=0,
        #                  sep='\t')
        # # df = df.drop(['P-value','Adjusted P-value','Old P-value','Old Adjusted P-value','Z-score','Combined Score'], axis=1)
        # df = df.head(10)
        # df = df.sort_values(by='Adjusted P-value')
        # df.to_csv(result_path + "/GO_Biological_Process_iea.GO_Biological.enrichr.reports.csv", sep='\t')


        gmt_CC = "/home/claire/Documents/ProteomX_Benjamin/data/annotation_data/MOUSE_GO_cc_no_GO_iea_symbol.gmt"
        result_path = str(output_dir + '/' + output_file + "_CC_gsea_result")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_CC',
                                     gene_sets=gmt_CC, background = 'mmusculus_gene_ensembl', outdir=result_path,
                                     cutoff=0.05, figsize=(8, 8))
        print('enrich GO CC')
        # print('enrich GO biological processs')
        # dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_BP")
        # df = pd.read_csv(result_path + "/GO_Cellular_Component.Cellular_Component.enrichr.reports.txt", index_col=0,
                         #sep='\t')
        # # df = df.drop(['P-value','Adjusted P-value','Old P-value','Old Adjusted P-value','Z-score','Combined Score'], axis=1)
        # df = df.head(10)
        # df = df.sort_values(by='Adjusted P-value')
        # df.to_csv(result_path + "/GO_Cellular_Component.GO_Cellular_Component.enrichr.reports.csv", sep='\t')


        gmt_MF = "/home/claire/Documents/ProteomX_Benjamin/data/annotation_data/MOUSE_GO_mf_no_GO_iea_symbol.gmt"
        result_path = str(output_dir + '/' + output_file + "_MF_gsea_result")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_MF',
                                     gene_sets=gmt_MF, background = 'mmusculus_gene_ensembl', outdir=result_path,
                                     cutoff=0.05, figsize=(8, 8))
        print('enrich GO MF')
        # print('enrich GO biological processs')
        # dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_BP")
        # df = pd.read_csv(result_path + "/GO_Molecular_Function.GO_Molecular_Function.enrichr.reports.txt", index_col=0,
        #                  sep='\t')
        # # df = df.drop(['P-value','Adjusted P-value','Old P-value','Old Adjusted P-value','Z-score','Combined Score'], axis=1)
        # df = df.head(10)
        # df = df.sort_values(by='Adjusted P-value')
        # df.to_csv(result_path + "/GO_Molecular_Function.GO_Molecular_Function.enrichr.reports.csv", sep='\t')

def gsea_mouse(gene_list,output_dir,output_file):
    glist=list(gene_list)
    output_file = output_file.split('.')[0]
    if len(glist) > 0:
        result_path = str(output_dir + '/' + output_file + "_BP_gsea_result")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_Biological',
                                     gene_sets='GO_Biological_Process_2018', organism = 'Mouse', outdir=result_path,
                                     cutoff=0.05, figsize=(8, 8))
        # print('enrich GO biological processs')
        dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_BP")
        df = pd.read_csv(result_path + "/GO_Biological_Process_2018.GO_Biological.enrichr.reports.txt", index_col=0,
                         sep='\t')
        # print(df['Combined Score'])
        # df = df.drop(['P-value','Adjusted P-value','Old P-value','Old Adjusted P-value','Z-score','Combined Score'], axis=1)
        df = df.head(10)
        df = df.sort_values(by='Adjusted P-value')
        df.to_csv(result_path + "/GO_Biological_Process_2018.GO_Biological.enrichr.reports.csv", sep='\t')


        result_path = str(output_dir + '/' + output_file + "_CC_gsea_result")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_CC', gene_sets='GO_Cellular_Component_2018', organism = 'Mouse',
                                     outdir=result_path, cutoff=0.05, figsize=(8, 8))
        dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_CC")
        df = pd.read_csv(result_path + "/GO_Cellular_Component_2018.GO_CC.enrichr.reports.txt", index_col=0, sep='\t')
        # df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        df = df.sort_values(by='Adjusted P-value')
        # df = df.head(10)
        df.to_csv(result_path + "/GO_Cellular_Component_2018.GO_CC.enrichr.reports.csv", sep='\t')


        result_path = str(output_dir + '/' + output_file + "_MF_gsea_result")
        enrichr_results = gp.enrichr(gene_list=glist, description='GO_Molecular', gene_sets='GO_Molecular_Function_2018', organism = 'Mouse',
                                     outdir=result_path, cutoff=0.05, figsize=(8, 8))
        dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_MF")
        df = pd.read_csv(result_path + "/GO_Molecular_Function_2018.GO_Molecular.enrichr.reports.txt", index_col=0,
                         sep='\t')
        # df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        df = df.sort_values(by='Adjusted P-value')
        df = df.head(10)
        df.to_csv(result_path + "/GO_Molecular_Function_2018.GO_Molecular.enrichr.reports.csv", sep='\t')


def run_gsea(gene_list,output_dir,output_file):
    #print gp.__version__
    #names = gp.get_library_name()

    glist=list(gene_list)
    output_file = output_file.split('.')[0]
    if len(glist) > 0:

        # print
        # #result_path = str(output_dir + '/' + output_file + "_Hallmark_gsea_result")
        # #enrichr_results = gp.enrichr(gene_list=glist, description='GO_CC', gene_sets='GO_Cellular_Component_2018',outdir=result_path, cutoff=0.05, figsize=(8, 8))
        # #dotplot(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_CC")
        # #df = pd.read_csv(result_path + "/GO_Cellular_Component_2018.GO_CC.enrichr.reports.txt", index_col=0,sep='\t')
        # #df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        # #df = df.head(10)
        # #df.to_csv(result_path + "/GO_Cellular_Component_2018.GO_CC.enrichr.reports.csv", sep='\t')
        #
        # result_path = str(output_dir + '/' + output_file + "_BP_gsea_result")
        # enrichr_results = gp.enrichr(gene_list=glist, description='GO_Biological', gene_sets='GO_Biological_Process_2018', outdir=result_path, cutoff=0.05, figsize=(8, 8))
        # #print('enrich GO biological processs')
        # dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_BP")
        # df=pd.read_csv(result_path+"/GO_Biological_Process_2018.GO_Biological.enrichr.reports.txt",index_col=0,sep='\t')
        # #print('df', df)
        # #print(df.columns)
        # #df.columns=df.columns.map(str.strip)
        # #print(df.columns)
        # print(df['Combined Score'])
        # #df = df.sort_values(df['Combined Score'], ascending = False)
        # df = df.drop(['P-value','Adjusted P-value','Old P-value','Old Adjusted P-value','Z-score','Combined Score'], axis=1)
        # df=df.head(10)
        # df = df.sort_values(by = 'Adjusted P-value')
        # df.to_csv(result_path+"/GO_Biological_Process_2018.GO_Biological.enrichr.reports.csv",sep='\t')
        #
        # print('bp enrichr done')
        #
        # result_path = str(output_dir + '/' + output_file + "_BP_gsea_result_gmt")
        # enrichr_results = gp.enrichr(gene_list=glist, description='GO_Biological_gmt',
        #                               gene_sets='/home/claire/Documents/Projet_PolyphenolProt/Results_AGondeau/Resources/c2.all.v6.2.symbols.gmt',
        #                               #background='hsapiens_gene_ensembl',
        #                               background = 'human',
        #                               outdir=result_path, cutoff=0.05,
        #                               figsize=(8, 8))
        #                               #verbose=True)
        # #print(df['Combined Score'])
        # # print('enrich GO biological processs')
        # print(enrichr_results.res2d.columns)
        # barplot(enrichr_results.res2d, title='BP_test_gmt', ofname=result_path + '/' + output_file + "_BP_gmt")
        # dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_BP_test")
        # #df=pd.read_csv(result_path+"/GO_Biological_Process_2018.GO_Biological.enrichr.reports.txt",index_col=0,sep='\t')
        # #df = df.drop(['P-value','Adjusted P-value','Old P-value','Old Adjusted P-value','Z-score','Combined Score'], axis=1)
        # #df=df.head(10)
        # #df.to_csv(result_path+"/GO_Biological_Process_2018_test.GO_Biological.enrichr.reports.csv",sep='\t')


        print('bp gmt done')
        #
        result_path = str(output_dir + '/' + output_file + "_onco_gsea_result_gmt")
        enrichr_results = gp.enrichr(gene_list=glist, description='onco_gmt',
                                      gene_sets='/home/claire/Documents/Projet_PolyphenolProt/Results_AGondeau/Resources/c6.all.v6.2.symbols.gmt',
                                      background=20000,
                                      outdir=result_path, cutoff=0.05,
                                      figsize=(8, 8),
                                      verbose=True)
        barplot(enrichr_results.res2d, title='onco_gmt', ofname=result_path + '/' + output_file + "_onco_gmt")
        dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_onco_test")

        print('---------------------------------')
        # result_path = str(output_dir + '/' + output_file + "_KEGG_gsea_result")
        # enrichr_results = gp.enrichr(gene_list=glist, description='KEGG_2019', gene_sets='KEGG_2019_Human', outdir=result_path, cutoff=0.05, figsize=(8,8))
        # dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_KEGG")
        # df = pd.read_csv(result_path + "/KEGG_2019_Human.KEGG_2019.enrichr.reports.txt", index_col=0,sep='\t')
        # df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        # df = df.head(10)
        # df.to_csv(result_path + "/KEGG_2019_Human.KEGG_2019.enrichr.reports.csv", sep='\t')
        #
        # result_path = str(output_dir + '/' + output_file + "_Wiki_pathway_gsea_result")
        # enrichr_results = gp.enrichr(gene_list=glist, description='WikiPathways_2019', gene_sets='WikiPathways_2019_Human',outdir=result_path, cutoff=0.05, figsize=(8, 8))
        # dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_WP")
        # df = pd.read_csv(
        #     result_path + "/WikiPathways_2019_Human.WikiPathways_2019.enrichr.reports.txt",index_col=0,sep='\t')
        # df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        # df = df.head(10)
        # df.to_csv(result_path + "/WikiPathways_2019_Human.WikiPathways_2019.enrichr.reports.csv",sep='\t')
        #
        #
        # result_path = str(output_dir + '/' + output_file + "_CC_gsea_result")
        # enrichr_results = gp.enrichr(gene_list=glist, description='GO_CC', gene_sets='GO_Cellular_Component_2018', outdir=result_path, cutoff=0.05, figsize=(8, 8))
        # dotplot_claire(enrichr_results.res2d, ofname=result_path + '/' + output_file + "_CC")
        # df = pd.read_csv(result_path + "/GO_Cellular_Component_2018.GO_CC.enrichr.reports.txt", index_col=0,sep='\t')
        # df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        # df = df.sort_values(by = 'Adjusted P-value')
        # df = df.head(10)
        # df.to_csv(result_path + "/GO_Cellular_Component_2018.GO_CC.enrichr.reports.csv", sep='\t')
        #
        #
        # result_path = str(output_dir + '/' + output_file + "_MF_gsea_result")
        # enrichr_results = gp.enrichr(gene_list=glist, description='GO_Molecular', gene_sets='GO_Molecular_Function_2018', outdir=result_path, cutoff=0.05, figsize=(8, 8))
        # dotplot_claire(enrichr_results.res2d, ofname=result_path+'/' +output_file+"_MF")
        # df = pd.read_csv(result_path + "/GO_Molecular_Function_2018.GO_Molecular.enrichr.reports.txt", index_col=0,sep='\t')
        # df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        # df = df.sort_values(by='Adjusted P-value')
        # df = df.head(10)
        # df.to_csv(result_path + "/GO_Molecular_Function_2018.GO_Molecular.enrichr.reports.csv", sep='\t')
        #
        #
        # result_path = str(output_dir + '/' + output_file + "_NCI_cancer")
        # enrichr_results = gp.enrichr(gene_list=glist, description='NCI_cancer_cell_lines', gene_sets='NCI-60_Cancer_Cell_Lines', outdir=result_path, cutoff=0.05, figsize=(8, 8))
        # print(len(enrichr_results.res2d.columns))
        # dotplot_claire(enrichr_results.res2d, ofname=result_path+'/' +output_file+"_MF")
        # df = pd.read_csv(result_path + "/NCI-60_Cancer_Cell_Lines.NCI_cancer_cell_lines.enrichr.reports.txt", index_col=0,sep='\t')
        # df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        # df = df.sort_values(by='Adjusted P-value')
        # df = df.head(10)
        # df.to_csv(result_path + "/NCI-60_Cancer_Cell_Lines.NCI_cancer_cell_lines.enrichr.reports.csv", sep='\t')
        # #
        # result_path = str(output_dir + '/' + output_file + "_Cancer_cell_lines_encyclopedia")
        # enrichr_results = gp.enrichr(gene_list=glist, description='Cancer_cell_lines', gene_sets='Cancer_Cell_Line_Encyclopedia', outdir=result_path, cutoff=0.05, figsize=(8, 8))
        # dotplot_claire(enrichr_results.res2d, ofname=result_path+'/' +output_file+"_MF")
        # df = pd.read_csv(result_path + "/Cancer_Cell_Line_Encyclopedia.Cancer_cell_lines.enrichr.reports.txt", index_col=0,sep='\t')
        # df = df.drop(['P-value', 'Adjusted P-value', 'Old P-value', 'Old Adjusted P-value', 'Z-score', 'Combined Score'], axis=1)
        # df = df.sort_values(by='Adjusted P-value')
        # df = df.head(10)
        # df.to_csv(result_path + "/Cancer_Cell_Line_Encyclopedia.Cancer_cell_lines.enrichr.reports.csv", sep='\t')
        #
        # # result_path = str(output_dir + '/' + output_file + "_Cancer_c6")
        # # gseapy_results = gp.gsea(data=glist)

def dotplot_claire(df, column='Adjusted P-value', title='', cutoff=0.05, top_term=10,
            sizes=None, norm=None, legend=True, figsize=(6, 5.5),
            cmap='RdBu_r', ofname=None, **kwargs):
    """Visualize enrichr results.

    :param df: GSEApy DataFrame results.
    :param column: which column of DataFrame to show. Default: Adjusted P-value
    :param title: figure title
    :param cutoff: p-adjust cut-off.
    :param top_term: number of enriched terms to show.
    :param ascending: bool, the order of y axis.
    :param sizes: tuple, (min, max) scatter size. Not functional for now
    :param norm: maplotlib.colors.Normalize object.
    :param legend: bool, whether to show legend.
    :param figsize: tuple, figure size.
    :param cmap: matplotlib colormap
    :param ofname: output file name. If None, don't save figure

    """

    colname = column
    # sorting the dataframe for better visualization
    if colname in ['Adjusted P-value', 'P-value']:
        # check if any values in `df[colname]` can't be coerced to floats
        can_be_coerced = df[colname].map(isfloat)
        if np.sum(~can_be_coerced) > 0:
            raise ValueError('some value in %s could not be typecast to `float`' % colname)
        else:
            df.loc[:, colname] = df[colname].map(float)
        df = df[df[colname] <= cutoff]
        if len(df) < 1:
            msg = "Warning: No enrich terms when cutoff = %s" % cutoff
            return msg
        df = df.assign(logAP=lambda x: - x[colname].apply(np.log10))
        colname = 'logAP'
    df = df.sort_values(by=colname).iloc[-top_term:, :]
    #
    temp = df['Overlap'].str.split("/", expand=True).astype(int)
    df = df.assign(Hits=temp.iloc[:, 0], Background=temp.iloc[:, 1])
    df = df.assign(Hits_ratio=lambda x: x.Hits / x.Background)
    # x axis values
    x = df.loc[:, colname].values
    combined_score = df['Combined Score'].round().astype('int')
    # y axis index and values
    y = [i for i in range(0, len(df))]
    ylabels = df['Term'].values
    # Normalise to [0,1]
    # b = (df['Count']  - df['Count'].min())/ np.ptp(df['Count'])
    # area = 100 * b

    # control the size of scatter and legend marker
    levels = numbers = np.sort(df.Hits.unique())
    if norm is None:
        norm = Normalize()
    elif isinstance(norm, tuple):
        norm = Normalize(*norm)
    elif not isinstance(norm, Normalize):
        err = ("``size_norm`` must be None, tuple, "
               "or Normalize object.")
        raise ValueError(err)
    min_width, max_width = np.r_[20, 100] * plt.rcParams["lines.linewidth"]
    norm.clip = True
    if not norm.scaled():
        norm(np.asarray(numbers))
    size_limits = norm.vmin, norm.vmax
    scl = norm(numbers)
    widths = np.asarray(min_width + scl * (max_width - min_width))
    if scl.mask.any():
        widths[scl.mask] = 0
    sizes = dict(zip(levels, widths))
    df['sizes'] = df.Hits.map(sizes)
    area = df['sizes'].values

    # creat scatter plot
    if hasattr(sys, 'ps1') and (ofname is None):
        # working inside python console, show figure
        fig, ax = plt.subplots(figsize=figsize)
    else:
        # If working on commandline, don't show figure
        fig = Figure(figsize=figsize)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
    vmin = np.percentile(combined_score.min(), 2)
    vmax = np.percentile(combined_score.max(), 98)
    sc = ax.scatter(x=x, y=y, s=area, edgecolors='face', c=combined_score,
                    cmap=cmap, vmin=vmin, vmax=vmax)

    if column in ['Adjusted P-value', 'P-value']:
        xlabel = "-log$_{10}$(%s)" % column
    else:
        xlabel = column
    ax.set_xlabel(xlabel, fontsize=14, fontweight='bold')
    ax.yaxis.set_major_locator(plt.FixedLocator(y))
    ax.yaxis.set_major_formatter(plt.FixedFormatter(ylabels))
    ax.set_yticklabels(ylabels, fontsize=16)

    # ax.set_ylim([-1, len(df)])
    ax.grid()
    # colorbar
    cax = fig.add_axes([0.95, 0.20, 0.03, 0.22])
    cbar = fig.colorbar(sc, cax=cax, )
    cbar.ax.tick_params(right=True)
    cbar.ax.set_title('Combined\nScore', loc='left', fontsize=12)



    # for terms less than 3
    print(df)
    if len(df) >= 3:

        # find the index of the closest value to the median
        idx = [area.argmax(), np.abs(area - area.mean()).argmin(), area.argmin()]
        idx = unique(idx)
        label = df.iloc[idx, df.columns.get_loc('Hits')]
    else:
        idx = df.index.values
        label = df.ix[idx, 'Hits']
        idx = idx.tolist()

    if legend:

        handles, _ = ax.get_legend_handles_labels()

        legend_markers = []
        for ixe in idx:
            #if len(df) == 1:
            #    legend_markers.append(ax.scatter([], [], s=30.0, c='b'))
            if len(df) >= 3:
                legend_markers.append(ax.scatter([], [], s=area[ixe], c='b'))
            else:
                legend_markers.append(ax.scatter([], [], s=df.ix[ixe, 'sizes'], c='b'))
        # artist = ax.scatter([], [], s=size_levels,)

        ax.legend(legend_markers, label, title='Hits')
    ax.set_title(title, fontsize=20, fontweight='bold')

    if ofname is not None:

        # canvas.print_figure(ofname, bbox_inches='tight', dpi=300)
        fig.savefig(ofname, bbox_inches='tight', dpi=300)
        return
    return ax


def plot_profiles(abundancies_data,conditions_set,protein,output_file):
    # Create a figure instance
    fig = plt.figure(1, figsize=(9, 6))
    # Create an axes instance
    ax = fig.add_subplot(111)
    # Create the boxplot
    bp = ax.boxplot(abundancies_data)

    ax.set_xticklabels(conditions_set)
    # for i in range(1,len(abundancies_data)):
    #     print(abundancies_data[i-1])
    #     plt.scatter(i,abundancies_data[i-1])
    #plt.xlabel('groups')
    plt.ylabel('reduced abundances')
    plt.title(protein)
    # Save the figure
    fig.savefig(output_file, bbox_inches='tight')
    plt.close()



def conditions_names(input_col_ab):
    # Get rid of '_REP_XX' at the end of abundance column names
    cond_col = ['_'.join(col.split('_')[:-2]) for col in input_col_ab.columns.values]
    unique_col_name = list(set(cond_col))
    conditions = autovivify(1, list)
    for i in np.arange(len(unique_col_name)):
        cond_splitted = re.split('Reduced_GR_|_SA_', unique_col_name[i])
        group = cond_splitted[1]
        sample = cond_splitted[2]
        conditions[group].append(sample)
    return(conditions)


def conditions_ab_columns(input_col_ab, conditions):
    list_of_col = list()
    print(conditions)
    #dict_test = {'Control': {'Control', 'ctrl'}, 'Infundibulum': {'Infundibulum1', '3'}}
    for group in conditions:
        for sample in conditions[group]:
            print('group', group)
            print('sample', sample)
            print('--')



    sys.exit()
    return(list_of_col)


# for sample in dict_test[group]:
#     print('group', group)
#     print('sample', sample)
#     # cond_col = [x for x in input_col_ab.columns.values if (group and sample) in x]
#     # print(cond_col)
#
#     # if len(cond_col)>0:
#     #    list_of_col.append(cond_col)




def suppress_na_triplicate(input_df, specific, triplicate):
    abundance_df = input_df.filter(regex='GR')

    reference = [x for x in abundance_df.columns.values if 'reference' in x]
    condition = [x for x in abundance_df.columns.values if 'reference' not in x]

    input_df = input_df.reset_index()
    accession_tokeep = []


    for protein in input_df.index.values:
        accession = input_df.iloc[protein]['Accession']

        reference_abundancies = np.array(input_df.loc[protein][reference].map(lambda x: atof(x) if type(x) == str else x))
        condition_abundancies = np.array(input_df.loc[protein][condition].map(lambda x: atof(x) if type(x) == str else x))

        nb_na_reference = np.isnan(reference_abundancies).sum()
        nb_na_condition = np.isnan(condition_abundancies).sum()

        if nb_na_reference >= 2 and nb_na_condition >= 2:
            continue
        elif nb_na_reference < 2 and nb_na_condition < 2:
            accession_tokeep.append(accession)

        if specific == 'y':
            if triplicate == 'y':
                if nb_na_reference == 3 and nb_na_condition < 1:
                    accession_tokeep.append(accession)
                elif nb_na_reference < 1 and nb_na_condition == 3:
                    accession_tokeep.append(accession)
            else:
                if nb_na_reference == 3 and nb_na_condition < 2:
                    accession_tokeep.append(accession)
                elif nb_na_reference < 2 and nb_na_condition == 3:
                    accession_tokeep.append(accession)

    result_df = input_df[input_df['Accession'].isin(accession_tokeep)]
    return(result_df)


def comparison_df(df1, df2):
    # Suppose que df2 soit un sous ensemble de df1 (ou inverse)
    diff_len = abs(len(df1)-len(df2))
    prot_nb_info = 'Difference of ' + str(diff_len) + ' proteins.'
    print(prot_nb_info)
    df1 = df1.set_index('Accession')
    df2 = df2.set_index('Accession')
    protein_common=[]
    protein_notcommon = []
    if len(df1) > len(df2):
        for protein in df1.index.values:
            if protein in df2.index.values:
                protein_common.append(protein)
            elif protein not in df2.index.values:
                protein_notcommon.append(protein)
        df_common = df1[df1.index.isin(protein_common)]
        df_not_common = df1[df1.index.isin(protein_notcommon)]
    if len(df2) > len(df1):
        for protein in df2.index.values:
            if protein in df1.index.values:
                protein_common.append(protein)
            elif protein not in df1.index.values:
                protein_notcommon.append(protein)
        df_common = df2[df2.index.isin(protein_common)]
        df_not_common = df2[df2.index.isin(protein_notcommon)]
    return(df_common, df_not_common)


def plot_CV(filename, input_df, output_fig, bins, threshold):
    CV_col = input_df.filter(regex = 'CV_')
    for col in CV_col:
        plot_name = col.split('_')[1] #ex : vescalagine

        plt.hist(np.array(input_df[col]), bins=bins)
        plt.xlabel('CV values')
        plt.ylabel('proteins #')
        if threshold:
            plt.axvline(threshold, color='k', linestyle='dashed', linewidth=1)
        plt.title('CV ' + plot_name)
        output_png = output_fig + '_histogramm_' + plot_name + '.png'
        plt.savefig(output_png)
        plt.close()



def plot_boxplot_protein(input_df, col, output_file, id_col, ref='Control', nb_chunk=5):
    print(input_df.head())



    input_df.reset_index(drop=True, inplace=True)
    abundance_df = input_df.filter(regex='VAL')
    print(abundance_df.columns.values)
    print(ref)
    reference = [x for x in abundance_df.columns.values if ref in x]
    condition = [x for x in abundance_df.columns.values if ref not in x]
    print(reference)
    reference_name = list(set([re.search(r"(?<=METABO_).*?(?=_)", col).group(0) for col in reference]))[0]
    condition_name = list(set([re.search(r"(?<=METABO_).*?(?=_)", col).group(0) for col in condition]))[0]
    print(reference_name)
    print(condition_name)

    ### Number of plots : 10 proteins per plot
    numb_plot = len(input_df) / nb_chunk
    max_value = abundance_df.max().max()

    ### Organize data
    chunk = nb_chunk

    for n_plot in np.arange(0,numb_plot):
        print(ref)
        #print(chunk * n_plot)
        #print(chunk * n_plot + (nb_chunk-1))
        protein_for_plot = input_df.loc[chunk * n_plot : chunk * n_plot + (nb_chunk-1)]
        list_metabo = protein_for_plot['Accession']
        #print(protein_for_plot)
        df = pd.DataFrame(columns=['metabolite', 'reduced abundance', 'group'])
        j = 0
        for i in protein_for_plot.index.values:
            protein = 'CP-' + str(protein_for_plot.loc[i, id_col])
            for colp in abundance_df.columns.values:
                abundance = protein_for_plot.loc[i, colp]
                if ref in colp:
                    group = reference_name
                else:
                    group = condition_name

                df.loc[j] = [protein, abundance, group]
                j = j + 1

            # plot
            sns.set_style('ticks')
            fig, ax = plt.subplots()
            # the size of A4 paper
            fig.set_size_inches(11.7, 8.27)
            print(df)

            sns.boxplot(x='metabolite', y='reduced abundance', data=df, hue='group', palette = 'muted')
            sns.set_context("paper", font_scale=1.6)
            #plt.xticks(rotation=45)
            for i in range(len(df['metabolite'].unique()) - 1):
                    plt.vlines(i + .5, 0, 45, linestyles='solid', colors='gray', alpha=0.2)
            plt.ylim(top = max_value, bottom=0)
            plt.savefig(output_file + '_' + str(n_plot) + ".png")
            sns.set_style('ticks')

            plt.close()

def get_samples_name(input_df, ref):
    abundance_df = input_df.filter(regex='GR')

    reference = [x for x in abundance_df.columns.values if ref in x]
    condition = [x for x in abundance_df.columns.values if ref not in x]

    reference_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in reference]))[0]
    condition_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in condition]))[0]

    return(reference_name, condition_name)


def get_group_name(input_df, ref):
    abundance_df = input_df.filter(regex='GR')

    reference = [x for x in abundance_df.columns.values if ref in x]
    group_name = list(set([re.search(r"(?<=GR_).*?(?=_SA)", col).group(0) for col in reference]))[0]

    return (group_name)

def genename_proteins(input_df, swiss_df, trembl_df, fragment, duplicate, noname):
    df_list = [input_df, swiss_df, trembl_df]
    result_df = reduce(lambda left, right: pd.merge(left, right, on='Accession', how='left'), df_list)

    result_df.reset_index(drop=True, inplace=True)
    result_df['gene_name'] = 'no gene name'
    result_df['gene_name_bank'] = 'no bank'

    for i in result_df.index.values:

        if fragment == 'y' and "Fragment" in str(result_df.ix[i, 'Description']):
            result_df.ix[i, 'gene_name'] = 'no gene name'
            continue

        gn_s = result_df.ix[i, 'gene_name_swiss']
        gn_t = result_df.ix[i, 'gene_name_trembl']
        if gn_s != gn_s:  # check for nan
            if gn_t != gn_t:
                result_df.ix[i, 'gene_name'] = 'no gene name'
                result_df.ix[i, 'gene_name_bank'] = 'no bank'
            else:
                result_df.ix[i, 'gene_name'] = gn_t
                result_df.ix[i, 'gene_name_bank'] = 'trembl'
        else:
            result_df.ix[i, 'gene_name'] = gn_s
            result_df.ix[i, 'gene_name_bank'] = 'swissprot'

    result_df = result_df.drop(columns=['gene_name_swiss', 'gene_name_trembl'])

    if duplicate != None:
        result_df = result_df[~result_df.duplicated(subset=['gene_name'])]

    if noname != None:
        result_df = result_df[result_df['gene_name'] != 'no gene name']

    return(result_df)



def create_csv_comparison_upset(path, output_path):
    #TODO : à tester
    # trous dans colonnes ?
    file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    file_list = [f.split('.')[0] for f in file_list] # get rid of csv extension

    files_df = pd.DataFrame(index=file_list)
    try:
        files_df.to_csv(output_path)
        return('csv created')
    except TypeError as e:
        return('Error while creating csv')


comparison_dict = {"OBVescalaginOx_vs_OBCtrlOx": "M6.OB-Vescalagin-C+_vs_OB-Control-C+",
                   "OBVescalagin_vs_OBControl": "M5.OB-Vescalagin_vs_OB-Control",
                   "OCVescalaginOx_vs_OCCtrlOx": "M6.OC-Vescalagin-C+_vs_OC-Control-C+",
                   "OCVescalagin_vs_OCControl": "M5.OC-Vescalagin_vs_OC-Control",
                   "OBVescalinOx_vs_OBCtrlOx": "M6.OB-Vescalin-C+_vs_OB-Control-C+",
                   "OBVescalin_vs_OBControl": "M5.OB-Vescalin_vs_OB-Control",
                   "OCVescalinOx_vs_OCCtrlOx": "M6.OC-Vescalin-C+_vs_OC-Control-C+",
                   "OCVescalin_vs_OCControl": "M5.OC-Vescalin_vs_OC-Control",
                   "OCPiceatannol_vs_OCControl": "M5.OC-Piceatannol_vs_OC-Control",
                   "OBPiceatannol_vs_OBControl": "M5.OB-Piceatannol_vs_OB-Control",
                   "OCResveratrol_vs_OCControl": "M5.OC-Resveratrol_vs_OC-Control",
                   "OBResveratrol_vs_OBControl": "M5.OB-Resveratrol_vs_OB-Control",
                   "OCVescalaginNox_vs_OCCtrlNox": "M6.OC-Vescalagin-D_vs_OC-Control-D",
                   "OCVescalinNox_vs_OCCtrlNox": "M6.OC-Vescalin-D_vs_OC-Control-D",
                   "OBVescalaginNox_vs_OBCtrlNox": "M6.OB-Vescalagin-D_vs_OB-Control-D",
                   "OBVescalinNox_vs_OBCtrlNox": "M6.OB-Vescalin-D_vs_OB-Control-D",
                   "Piceatannol_vs_ControlB": "M8.Pic-B_vs_Control-B",
                   "Vescalagine_vs_ControlB": "M8.Vg-B_vs_Control-B",
                   "Catechol_vs_ControlC60": "M8.Cat-C60_vs_Control-C60",
                   "Piceatannol_vs_ControlC60": "M8.Pic-C60_vs_Control-C60",
                   "Resveratrol_vs_ControlC60": "M8.Res-C60_vs_Control-C60",
                   "Vescalagine_vs_ControlC60": "M8.Vg-C60_vs_Control-C60",
                   "Piceatannol_vs_ControlIC": "M8.Pic-IC_vs_Control-IC",
                   "Vescalagine_vs_ControlIC": "M8.Vg-IC_vs_Control-IC",
                   "AvecOx_vs_SansOx": "M7.060_vs_O00",
                   "Control_vs_SansOx": "M7.020_vs_O00",
                   "Vescalagin_vs_AvecOx": "M7.2.Vg_vs_O60",
                   "Resveratrol_vs_AvecOx": "M7.2.Res_vs_O60",
                   "Piceatannol_vs_AvecOx": "M7.2.Pic_vs_O60",
                   "Catechol_vs_AvecOx": "M7.2.Cat_vs_O60"
                   }


upset_names = {"Vescalagin_vs_AvecOx" : "M7.2_Vg_MDA_O60"
               }
