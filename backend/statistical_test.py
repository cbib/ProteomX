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
import loguru
import helpers as h
import functions_analysis as fa
import os
import paths
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", "-i", help='Input file (csv)')
    parser.add_argument("--output_file", "-o", help='Output file (csv)')
    parser.add_argument("--file_id", "-f", help='Unique ID')

    args = parser.parse_args()
    return args


def compute_t_test(data: pd.DataFrame, config_dict: dict, paired_samples)-> pd.DataFrame:
    # get groups of sample to analyse
    # assumption: only two groups of sample in the dataframe
    groups_of_samples = h.get_data_subset(data, config_dict['all']['values_cols_prefix'],
                                              config_dict['all']['reference'])

    # compute two-tailed t-test
    t_test_pval = fa.compute_p_value(data_df, groups_of_samples[0], groups_of_samples[1], config_dict["all"]["id_col"],
                                                    config_dict["statistical_analysis"]["equal_var"], paired_samples)

    # correct p-values
    t_test_padj = fa.compute_p_adjusted(t_test_pval, config_dict["statistical_analysis"]["correction_method"])

    # merge original df with p-values and adjusted p-values
    res = h.merge_dataframes(data_df, t_test_padj, how="left", on=id_col)
    return res


def compute_distribution_fitting(data, config_dict, path_to_density_distribution):
    test = config_dict['distribution']['test_type']

    if config_dict['all']['specific_proteins']['keep']:
        logger.debug('Handling specific proteins')

        # Divide data frame in specific and aspecific proteins rows
        result, specific_proteins_df = fa.extract_specific_proteins(data)
        print(specific_proteins_df)
        # Add arbitrary p-value for specific proteins
        reference = config_dict["all"]["reference"]
        specific_proteins_pval = fa.update_res_with_specific_proteins(specific_proteins_df, reference, test)

    else:
        result = data.copy()
        # sanity check: remove any rows with nan in ratio (for analysis with only one replicate)
    result = result.dropna(subset=["ratio"])
    # Compute z-score
    #print(result)
    #print(result["ratio"])
    res_zscore = fa.compute_z_score(result)
    print(res_zscore)
    # Now find which distribution fits the best
    best_dist, args_param = fa.find_best_distribution(res_zscore, path_to_density_distribution)

    # compute p-value from the distribution
    res_pval = fa.compute_p_value_distribution(result, config_dict['distribution']['test_type'], best_dist, args_param)

    # Concatenate results on aspecific et specific proteins:
    if config_dict['all']['specific_proteins']['keep']:
        res_pval = pd.concat([res_pval, specific_proteins_pval], axis=0)

    # log results
    significant = len(res_pval[res_pval['pvalue'] < 0.05])
    logger.info("{} proteins are significant (p-value < 0.05).".format(str(significant)))

    return res_pval


if __name__ == "__main__":
    args = get_args()

    logpath = os.path.join(paths.global_data_dir, args.file_id, 'log/statistical_analysis.log')
    logger = h.get_logger(logpath)

    # load data
    data_df = pd.read_csv(args.input_file, header=0, index_col=None)
    loguru.logger.debug("Proteomic data loaded")

    # supported statistical test
    t_test_names = ["student_ttest", "welch_ttest", "ttest"]
    distribution = ['distribution_fitting', 'distribution']
    all_analysis_name = [*t_test_names, *distribution]

    # get parameters
    rule_params = h.load_json_parameter(args.file_id)
    loguru.logger.debug("Analysis parameters (config_file.json) loaded")

    try:
        id_col = rule_params["all"]["id_col"]
        analysis_to_perform = rule_params["statistical_analysis"]["analysis_to_perform"]

        if analysis_to_perform not in all_analysis_name:
            loguru.logger.error("Specified statistical test not supported (yet): {}".format(analysis_to_perform))
            sys.exit("NO ANALYSIS PERFORMED - Parameters missing")
        else:
            loguru.logger.debug("Statistical analysis to perform: {}".format(analysis_to_perform))

    except KeyError:
        loguru.logger.error("Must specify a statistical test to perform in the configuration file")
        sys.exit("NO ANALYSIS PERFORMED - Parameters missing")

    if analysis_to_perform in t_test_names:
        paired_samples = rule_params["statistical_analysis"]["paired_samples"]
        df_result = compute_t_test(data_df, rule_params, paired_samples)

    elif analysis_to_perform in distribution:
        file_name = h.filename(args.input_file)
        output_figure_density_distribution = os.path.join(paths.global_data_dir,
                                                          args.file_id,
                                                          "Figures",
                                                          "distribution",
                                                          "{}.png".format(file_name))
        print(output_figure_density_distribution)
        print(os.path.join(paths.global_data_dir, args.file_id, "Figures", "distribution"))
        os.makedirs(os.path.join(paths.global_data_dir, args.file_id, "Figures", "distribution"), exist_ok=True) 
        df_result = compute_distribution_fitting(data_df, rule_params, output_figure_density_distribution)

    if rule_params['all']['specific_proteins']['keep']:
        loguru.logger.debug("Adding arbitrary p-value / p-adj to specific proteins")
        df_result = fa.update_pvalue_specific_proteins(df_result,
                                                       rule_params["statistical_analysis"]["test_type"],
                                                       rule_params['all']['specific_proteins']['column_name'])

    # re-order dataframe
    df_result = fa.sort_dataframe(df_result, rule_params["statistical_analysis"]["sort_result_by"])
    
    h.export_result_to_csv(df_result, args.output_file)
