#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cédric Usureau, Aurélien Barré, Hayssam Soueidan


"""
Take list of UniProt accessions in a dataframe as input and add new column 'gene_name' to the dataframe. Use gProfiler.
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
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def add_gene_name_gprofiler(data_df: pd.DataFrame, col: str, organism: str) -> pd.DataFrame:
    #gp = gprofiler(return_dataframe=True)
    gp  = GProfiler()
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

    # gProfiler returns one line for each alias of the gene (as in alias section in Uniprot) => keep only the
    # first one
    df = df[~df['Accession'].duplicated(keep='first')]

    # TODO check if concordant with description
    # df['OK'] = np.where(df['gene_name_PD'] == df['converted_gprofiler'], True, False)

    return df


if __name__ == "__main__":
    args = get_args()
    rule_params = h.load_json_parameter(args.file_id)

    organism = rule_params['gene_name']['organism']
    sources_accession = rule_params['gene_name']['accession_source']  # column to use as input, a bit useless atm

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    res = add_gene_name_gprofiler(data_df, sources_accession, organism)

    h.export_result_to_csv(res, args.output_file)
