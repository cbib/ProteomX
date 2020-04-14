#!/usr/bin/env python
import argparse

import numpy as np
import pandas as pd
import statsmodels.stats.multitest as smm
from loguru import logger
from scipy import stats

import helpers as h
from legacy.utils import get_filename

parser = argparse.ArgumentParser(description='compute t-test')
parser.add_argument('-i', '--input_file')
parser.add_argument('-o', '--output_file')
parser.add_argument('-id', '--id_col')
parser.add_argument('-test', help='choose between "one-sided" or "two-sided" test')

# get arguments
args = vars(parser.parse_args())
input_file = args['input_file']
output_file = args['output_file']
test = args['test']
id_col = args['id_col']

# check_dir(get_filepath(output_file))
# check_dir(get_logpath(output_file))


# logging.basicConfig(filename=get_logpath(output_file) + 'ttest_welch.log', level=logging.INFO)
# logging.info(' Starting computing Welch t-test...')

input_df = pd.read_csv(input_file, header=0, index_col=None)
# logging.info(' Analysing ' + str(len(input_df)) + ' proteins')
print(input_df.columns.values)
ratio = input_df.filter(regex='^[rR]atio')

ratio_col = ratio.columns.tolist()[0]
specific_proteins_up = input_df[input_df[ratio_col] == 1000]
specific_proteins_down = input_df[input_df[ratio_col] == 0.001]

input_df[ratio_col] = np.where(input_df[ratio_col] == 1000, np.nan, input_df[ratio_col])
input_df[ratio_col] = np.where(input_df[ratio_col] == 0.001, np.nan, input_df[ratio_col])

input_df = input_df.dropna(subset=[ratio_col], axis=0)

input_df.reset_index(drop=True, inplace=True)

ttest_df = pd.DataFrame(columns=[id_col, 'pvalue', 'padj'], index=input_df.index)

abundance_df = input_df.filter(regex='VAL')
reference = [x for x in abundance_df.columns.values if 'OCVescalagin' in x]
condition = [x for x in abundance_df.columns.values if 'OCVescalagin' not in x]

for protein in input_df.index.values:
    reference_values = input_df.iloc[protein][reference]
    condition_values = input_df.iloc[protein][condition]

    condition_values = condition_values.dropna()
    reference_values = reference_values.dropna()

    stat, p_value = stats.ttest_ind(condition_values, reference_values, equal_var=False, nan_policy='omit')

    ttest_df.loc[protein]['pvalue'] = p_value

    ttest_df.loc[protein][id_col] = input_df.loc[protein][id_col]

rej, pval_corr = smm.multipletests(ttest_df['pvalue'].values, alpha=float('0.05'), method='fdr_i')[:2]
ttest_df['padj'] = pval_corr

result_df = input_df.merge(ttest_df, how='left', on=id_col)
result_df = result_df.sort_values("pvalue")
# """ Update p-value/padj for specific proteins """
# result_df = pd.concat([result_df, specific_proteins_up, specific_proteins_down], sort=False)
# result_df.reset_index(drop=True, inplace=True)
# if test == 'right-tailed':
#     result_df = update_pvalues_right_tailed(result_df)
# if test == 'two-sided':
#     result_df = update_pvalues_two_sided(result_df)
# result_df = result_df.sort_values("padj", axis=0)


significant = 0

for protein in result_df.index.values:
    if np.round(result_df.loc[protein]['padj'], decimals=3) <= 0.05:
        significant = significant + 1

logger.info(" {} significant proteins in {}".format(significant, get_filename(input_file)))
print(" got", significant, " significant proteins (p-adj < 0.05)")

h.export_result_to_csv(result_df, output_file)
