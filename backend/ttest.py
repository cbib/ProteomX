#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Compute statistical tests : Student or Welch test. Test choosen with "equal_var" parameter in the config file.
"""

import argparse
import pandas as pd
from loguru import logger
import helpers as h
import functions_analysis as fa


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def log_significant_protein_number(res):
    significant = len(result_df.loc[res['padj'] < 0.05])
    logger.info(" {} significant proteins (p-adj < 0.05) in {}".format(significant, filename))
    return


if __name__ == "__main__":
    args = get_args()
    filename = h.filename(args.input_file)

    logger = h.get_logger(args.file_id, 'ttest')

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # get parameters
    rule_params = h.load_json_parameter(args.file_id)
    id_col = rule_params["all"]["id_col"]

    # get groups of sample to analyse
    groups = h.get_data_subset(data_df, rule_params['all']['values_cols_prefix'], rule_params['all']['reference'])

    # compute statistics
    ttest_pval = fa.compute_p_value(data_df,
                                    groups[0], groups[1],
                                    id_col,
                                    rule_params["ttest"]["equal_var"],
                                    rule_params["ttest"]["test_type"])
    ttest_padj = fa.compute_p_adjusted(ttest_pval, rule_params["ttest"]["correction_method"])
    result_df = fa.merge_and_sort_results(data_df, ttest_padj, id_col, rule_params["ttest"]["sort_result_by"])

    log_significant_protein_number(result_df)

    if rule_params['all']['specific_proteins']['keep']:
        result_df = fa.update_pvalue_specific_proteins(result_df,
                                                       rule_params["ttest"]["test_type"],
                                                       rule_params['all']['specific_proteins']['column_name'])

    h.export_result_to_csv(result_df, args.output_file)
