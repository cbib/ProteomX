#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski


"""
Compute statistical tests :
    ttest : Student or Welch test. Test choosen with "equal_var" parameter in the config file.
    Mann Whithney rank test (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html)
    distribution fitting
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


if __name__ == "__main__":
    args = get_args()
    filename = h.filename(args.input_file)

    logger = h.get_logger(args.file_id, 'statistical_test')

    data_df = pd.read_csv(args.input_file, header=0, index_col=None)

    # get parameters
    rule_params = h.load_json_parameter(args.file_id)
    id_col = rule_params["all"]["id_col"]
    test_to_perform = rule_params["statistical_test"]["test"]

    if test_to_perform == "student_ttest" or test_to_perform == "welch_ttest":
        # get groups of sample to analyse
        # assumption: only two groups of sample in the dataframe
        groups = h.get_data_subset(data_df, rule_params['all']['values_cols_prefix'], rule_params['all']['reference'])

        # compute statistics
        ttest_pval = fa.compute_p_value_with_ttest(data_df,
                                        groups[0], groups[1],
                                        id_col,
                                        rule_params["statistical_test"]["equal_var"],
                                        rule_params["statistical_test"]["test_type"])
        # correct p-values
        ttest_padj = fa.compute_p_adjusted(ttest_pval, rule_params["statistical_test"]["correction_method"])

        # merge original df with p-values and adjusted p-values
        df_result = h.merge_dataframes(data_df, ttest_padj, how="left", on=id_col)
       
    elif test_to_perform == "wilcoxon_rank_sum":
        pass

    elif test_to_perform == "distribution_fitting":
        pass
    else
        loguru.logger.warning("Must specify a statistical test to perform : student_ttest / welch_ttest / wilcoxon_rank_sum / distribution_fitting")

    # TODO : function to sort dataframe
    result_df = fa.merge_and_sort_results(data_df, ttest_padj, id_col, rule_params["statistical_test"]["sort_result_by"])
    

    # TODO: where to place this ? // distribution.py
    if rule_params['all']['specific_proteins']['keep']:
        result_df = fa.update_pvalue_specific_proteins(result_df,
                                                       rule_params["ttest"]["test_type"],
                                                       rule_params['all']['specific_proteins']['column_name'])

    h.export_result_to_csv(result_df, args.output_file)
