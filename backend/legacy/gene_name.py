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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (without extension)')
    parser.add_argument("--project", "-p", help='Project name')
    parser.add_argument("--version", "-v", help='Analysis version name')
    parser.add_argument("--config_file", "-c")

    args = parser.parse_args()
    return args


def add_gene_name_gprofiler(data_df, col, organism):
    print(type(data_df[col].tolist()))
    gp = GProfiler(return_dataframe=True)

    # details of what returns the following function : caleydo.org/tools/
    res = gp.convert(organism=organism,
                     query=data_df[col].tolist(),
                     target_namespace='UNIPROTSWISSPROT')

    # now add the relevant results to dataframe
    res_f = res[['incoming', 'name', 'namespaces']]

    res_f.rename(columns={"incoming":col,
                       "name": "gene_name",
                       "namespaces": "gene_name_bank"}, inplace=True)

    res_f = res_f.replace({'UNIPROTSWISSPROT,UNIPROT_GN_ACC':'Swiss-Prot',
                           'UNIPROTSPTREMBL,UNIPROT_GN_ACC':'TrEMBL'})

    df = data_df.merge(res_f, how='left', on=col)

    # TODO check if concordant with description
    #df['OK'] = np.where(df['gene_name_PD'] == df['converted_gprofiler'], True, False)
    print(df)

    return df


def add_gene_name_annotation_files(data_df, column_input, organism):
    #TODO
    swiss_file = '/home/claire/Documents/ProteomX_Benjamin/data/annotation_data/mmusculus/swiss_annot_mouse_unique.csv'
    trembl_file = '/home/claire/Documents/ProteomX_Benjamin/data/annotation_data/mmusculus/trembl_annot_mouse_unique.csv'
    swiss_df = pd.read_csv(swiss_file, index_col = False, header = 0)
    trembl_df = pd.read_csv(trembl_file, index_col = False, header = 0)

    swiss_df = swiss_df.rename({'Swiss': 'Accession', 'Gene name': 'gene_name_swiss'}, axis=1)
    trembl_df = trembl_df.rename({'Trembl': 'Accession', 'Gene name': 'gene_name_trembl'}, axis=1)

    res = genename_proteins(input_df, swiss_df, trembl_df, fragment, duplicate, noname)
    return res


def genename_proteins(input_df, swiss_df, trembl_df, fragment, duplicate, noname):
    #TODO
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


if __name__ == "__main__":
    args = get_args()

    if not args.config_file:
        rule_params = h.load_json_parameter(args.project, args.version)
    else:
        with open(args.config_file) as f:
            rule_params = json.load(f)

    # get parameters

    organism = rule_params['gene_name']['organism']
    sources_gn = rule_params['gene_name']['gene_name_source'] # gProfiler and/or annotation_file
    sources_accession = rule_params['gene_name']['accession_source'] # column(s) to use as input

    # get data

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # add gene identifier
    functions = {'gProfiler': add_gene_name_gprofiler,
                 'annotions_files': add_gene_name_annotation_files}

    for tool in sources_gn:
        for col in sources_accession:
            print(functions[tool])
            result_df = functions[tool](data_df, col, organism)

            # check for duplicate -
            result_df_notdup = result_df[~result_df['Accession'].duplicated(keep='first')]

            result_df_notdup.to_csv(args.output_file, index=False)