#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Take UniProt accessions and add new column 'gene_name' to the dataframe in input, based on annotation files
or gProfiler.

TO DO:
- possibility to specify several differents columns as input => return as many columns with corresponding gene name
- specify format of gene name
"""

import argparse
import pandas as pd
import paths
import helpers as h
import json
from gprofiler import GProfiler
from functools import reduce
import os


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (without extension)')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def add_gene_name_gprofiler(data_df: pd.DataFrame, col: str, organism: str) -> pd.DataFrame:
    gp = GProfiler(return_dataframe=True)
    protein_list = data_df[col].tolist()

    # details of what returns the following function : https://pypi.org/project/gprofiler-official/
    # TODO : documentation
    res = gp.convert(organism=organism,
                     query=protein_list,
                     target_namespace='UNIPROTSWISSPROT')

    # now add the relevant results to dataframe
    res_f = res[['incoming', 'name', 'namespaces']]

    res_f.rename(columns={"incoming": col,
                          "name": "gene_name",
                          "namespaces": "gene_name_bank"}, inplace=True)

    res_f = res_f.replace({'UNIPROTSWISSPROT,UNIPROT_GN_ACC': 'Swiss-Prot',
                           'UNIPROTSPTREMBL,UNIPROT_GN_ACC': 'TrEMBL'})

    df = data_df.merge(res_f, how='left', on=col)

    # gProfiler returns one line for each alias of the gene (as in alias section in Uniprot): keep only the first one
    df = df[~df['Accession'].duplicated(keep='first')]

    return df


def add_gene_name_annotation_files(data_df, col, organism):
    # parameters :
    fragment = rule_params['gene_name']['fragment']

    if organism == "mmusculus":
        swiss_file = os.path.join(paths.global_data_dir, 'annotation_data/mmusculus/uniprot_swiss_prot_mmusculus.tab')
        trembl_file = os.path.join(paths.global_data_dir, 'annotation_data/mmusculus/uniprot_trembl_mmusculus.tab')

        swiss_df = pd.read_csv(swiss_file, index_col=False, header=0, sep='\t')
        trembl_df = pd.read_csv(trembl_file, index_col=False, header=0, sep='\t')

        swiss_df = swiss_df.rename({'Swiss': 'Accession', 'Gene names': 'gene_name_swiss'}, axis=1)
        swiss_df = swiss_df[['Accession', 'gene_name_swiss']]
        trembl_df = trembl_df.rename({'Trembl': 'Accession', 'Gene names': 'gene_name_trembl'}, axis=1)
        trembl_df = trembl_df[['Accession', 'gene_name_trembl']]

        res_gene_name = genename_proteins(data_df, col, swiss_df, trembl_df, fragment)
        
    if organism == "hsapiens":
        swiss_file = os.path.join(paths.global_data_dir, 'annotation_data/hsapiens/uniprot_swiss_prot_hsapiens.tab')
        trembl_file = os.path.join(paths.global_data_dir, 'annotation_data/hsapiens/uniprot_trembl_hsapiens.tab')

        swiss_df = pd.read_csv(swiss_file, index_col=False, header=0, sep='\t')
        trembl_df = pd.read_csv(trembl_file, index_col=False, header=0, sep='\t')

        swiss_df = swiss_df.rename({'Entry': 'Accession', 'Gene names': 'gene_name_swiss'}, axis=1)
        swiss_df = swiss_df[['Accession', 'gene_name_swiss']]
        trembl_df = trembl_df.rename({'Entry': 'Accession', 'Gene names': 'gene_name_trembl'}, axis=1)
        trembl_df = trembl_df[['Accession', 'gene_name_trembl']]

        res_gene_name = genename_proteins(data_df, col, swiss_df, trembl_df, fragment)
    return res_gene_name


def genename_proteins(input_df, col, swiss_df, trembl_df, fragment):
    df_list = [input_df, swiss_df, trembl_df]
    res = reduce(lambda left, right: pd.merge(left, right, on=col, how='left'), df_list)

    res.reset_index(drop=True, inplace=True)
    res['gene_name'] = 'no gene name'
    res['gene_name_bank'] = 'no bank'

    for i in res.index.values:

        if fragment and "Fragment" in str(res.loc[i, 'Description']):
            res.loc[i, 'gene_name'] = 'no gene name'
            continue

        gn_s = res.loc[i, 'gene_name_swiss']
        gn_t = res.loc[i, 'gene_name_trembl']
        if gn_s != gn_s:  # check for nan
            if gn_t != gn_t:
                res.loc[i, 'gene_name'] = 'no gene name'
                res.loc[i, 'gene_name_bank'] = 'no bank'
            else:
                res.loc[i, 'gene_name'] = gn_t
                res.loc[i, 'gene_name_bank'] = 'TrEMBL'
        else:
            res.loc[i, 'gene_name'] = gn_s
            res.loc[i, 'gene_name_bank'] = 'Swiss-Prot'

    res = res.drop(columns=['gene_name_swiss', 'gene_name_trembl'])
    res = remove_multiple_names(res)
    return res


def remove_multiple_names(df):
    """Keep only first alias of the gene"""

    df.reset_index(inplace=True, drop=True)
    for i in df.index.values:

        if df.loc[i, "gene_name"] == "no gene name":
            continue

        unique_gn = df.loc[i, "gene_name"].split(' ')[0]
        df.loc[i, "gene_name"] = unique_gn
    return df


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)

    # get parameters
    organism = rule_params['gene_name']['organism']
    sources_gn = rule_params['gene_name']['gene_name_source']  # gProfiler and/or annotation_file
    sources_accession = rule_params['gene_name']['accession_source']  # column(s) to use as input
    duplicate = rule_params['gene_name']['duplicate']
    noname = rule_params['gene_name']['noname']

    # get data
    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # add gene identifier
    functions = {'gProfiler': add_gene_name_gprofiler,
                 'annotions_files': add_gene_name_annotation_files}

    for tool in sources_gn:
        for col in sources_accession:

            result_df = functions[tool](data_df, col, organism)

            if duplicate:
                result_df = result_df[~result_df.duplicated(subset=['gene_name'], keep=False)]
            if noname:
                result_df = result_df[result_df['gene_name'] != 'no gene name']

            result_df.to_csv(args.output_file, index=False)
