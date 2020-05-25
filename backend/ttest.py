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
    rule_params = h.load_json_parameter(args.file_id)

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    id_col = rule_params["all"]["id_col"]
    groups = h.get_data_subset(data_df, rule_params['all']['values_cols_prefix'], rule_params['ratio']['reference'])
    ttest_pval = fa.compute_p_value(data_df, groups[0], groups[1], id_col, rule_params["ttest"]["equal_var"])
    ttest_padj = fa.compute_p_adjusted(ttest_pval, rule_params["ttest"]["correction_method"])
    result_df = fa.merge_and_sort_results(data_df, ttest_padj, id_col, rule_params["ttest"]["sort_res_by"])

    log_significant_protein_number(result_df)

    h.export_result_to_csv(result_df, args.output_file)

