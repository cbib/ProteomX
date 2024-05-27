#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cedric Usureau, Aurélien Barré, Hayssam Soueidan


"""
Collection of functions used in data analysis :
- log2FC
- overlap
- ttest
"""

import numpy as np
import pandas as pd
import statsmodels.stats.multitest as smm
from scipy import stats
from scipy.stats._continuous_distns import _distn_names  # import distributions names
import warnings
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')



def compute_overlap(df: pd.DataFrame, group1, group2, overlap_method: str) -> pd.DataFrame:
    for i in df.index.values:
        group1_values = np.array(group1.iloc[i])
        group2_values = np.array(group2.iloc[i])

        if overlap_method == "symmetric":
            df.loc[i, 'score_overlap'] = overlap_symmetric(group1_values, group2_values)
        else:
            df.loc[i, 'score_overlap'] = overlap_asymmetric(group1_values, group2_values)

    return df


def overlap_symmetric(x: np.array, y: np.array) -> int:
    a = [np.nanmin(x), np.nanmax(x)]
    b = [np.nanmin(y), np.nanmax(y)]

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    overlap = np.nanmax([a[0], b[0]]) - np.nanmin([a[1], b[1]])
    return overlap


def overlap_asymmetric(x: np.array, y: np.array) -> int:
    # x is the reference group
    overlap = np.nanmin(y) - np.nanmax(x)
    return overlap


def compute_p_value(df, group1, group2, id_col, equal_var, paired_samples=False):

    ttest_df = pd.DataFrame(columns=[id_col, 'pvalue'], index=df.index)

    for i in df.index.values:
        group1_values = np.array(group1.iloc[i], dtype=float)
        group2_values = np.array(group2.iloc[i], dtype=float)

        # two-tailed t-test
        if paired_samples:
            stat, p_value = stats.ttest_rel(group1_values, group2_values, nan_policy='omit')
        else:
            stat, p_value = stats.ttest_ind(group1_values, group2_values, equal_var=equal_var, nan_policy='omit')
        ttest_df.loc[i] = [df.loc[i][id_col], p_value]

    return ttest_df


def compute_p_adjusted(df: pd.DataFrame, correction_method: str) -> pd.DataFrame:
    #print(smm.multipletests(df['pvalue'].values, alpha=float('0.05'), method=correction_method)[:2])
    rej, pval_corr = smm.multipletests(df['pvalue'].values, alpha=0.1, method=correction_method)[:2]
    #rej, pval_corr = smm.fdrcorrection(df['pvalue'].values, alpha=0.05, method='indep', is_sorted=False)[:2]
    df['padj'] = pval_corr
    print(df)
    return df


def merge_and_sort_results(df: pd.DataFrame, padj_df: pd.DataFrame, col_for_merge, sort_df_by:str):
    res = df.merge(padj_df, how='left', on=col_for_merge)
    res = res.sort_values(sort_df_by)
    return res


def sort_dataframe(df: pd.DataFrame, sort_df_by:str) -> pd.DataFrame:
    res = df.sort_values(sort_df_by)
    return res


def update_pvalue_specific_proteins(df: pd.DataFrame, analysis_test_type, specific_column) -> pd.DataFrame:
    """
    Update 'pvalue' 'padj' column values for proteins specific to one condition/group
    """
    if analysis_test_type == "right-tailed":
        print("Updating overlap score for right-tailed test")
        mask = ((df[specific_column] == "specific") & (df['ratio'] == 1000))

        df['pvalue'][mask] = np.where(mask, 0, 1)
        df['padj'][mask] = np.where(mask, 0, 1)

    elif analysis_test_type == "left-tailed":
        print("Updating overlap score for left-tailed test")
        mask = ((df[specific_column] == "specific") & (df['ratio'] == 0.001))

        df['pvalue'][mask] = np.where(mask, 0, 1)
        df['padj'][mask] = np.where(mask, 0, 1)

    elif analysis_test_type == "two-tailed":
        print("Updating overlap score for two-tailed test")
        mask = ((df[specific_column] == "specific") & (df['ratio'] == 1000) | (df[specific_column] == "specific") & (df['ratio'] == 0.001))
        df['pvalue'][mask] = 0
        try:
            df['padj'][mask] = 0
        except KeyError:
            pass

    return df


# Distribution
def update_res_with_specific_proteins(specific_proteins: pd.DataFrame, reference: str, test: str) -> pd.DataFrame:
    """
    Update with arbitrary p-value for specific proteins
    """
    if test == 'two-sided':
        specific_proteins['pvalue'] = 0
        specific_proteins['pvalue_left'] = 0
        specific_proteins['pvalue_right'] = 0

    elif test == 'right-tailed':
        specific_proteins['pvalue'] = np.where((specific_proteins['ratio'] == 0.001), 1, 0)

    return specific_proteins


def compute_z_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add one column with z-score of ratio already computed
    """
    # TODO: if no columns named "ratio" / if several columns with "ratio_"
    df['zscore'] = stats.zscore(df["ratio"])

    return df



def find_best_distribution(df: pd.DataFrame, out_histogram_distribution: str):
    """
    Find best distribution among all the scipy.stats distribution and returns it with its parameters
    """
    dist = np.around(np.array((df['zscore']).astype(float)), 2)  # TODO : pourquoi arrondir ??

    best_dist, best_dist_name, best_fit_params = get_best_fit(dist, out_histogram_distribution)
    print(best_dist_name)
    print('___')
    print(best_fit_params)

    # logger.info("Best fit is", str(best_dist_name), "with", str(*best_fit_params))
    args_param = dict(e.split('=') for e in best_fit_params.split(', '))
    for k, v in args_param.items():
        args_param[k] = float(v)

    best_distribution = getattr(stats, best_dist_name)
    q_val = best_dist.ppf(0.95, **args_param)
    print("And the q value is", q_val)
    return best_distribution, args_param


def compute_p_value_distribution(df: pd.DataFrame, test: str, best_dist, args_param) -> pd.DataFrame:
    """
    compute p-value depending on the chosen test
    """
    if test == 'right-tailed':
        df['pvalue'] = 1 - best_dist.cdf(df['zscore'], **args_param)
    elif test == 'left-tailed':
        df['pvalue'] = best_dist.cdf(df['zscore'], **args_param)
    elif test == 'two-sided':
        df['pvalue_right'] = 1 - best_dist.cdf(df['zscore'], **args_param)
        df['pvalue_left'] = best_dist.cdf(df['zscore'], **args_param)

        for i in df.index.values:
            pr = df.loc[i, 'pvalue_right']
            pl = df.loc[i, 'pvalue_left']
            df.loc[i, 'pvalue'] = 2 * (min(pr, pl))
            #df.loc[i, 'pvalue_best_side'] = min(pr, pl)

    else:
        print("WARNING: two-tailed / left-tailed / right-tailed ")
    return df


def extract_specific_proteins(df: pd.DataFrame) -> tuple:
    """
    Proteins specific to one condition (that is, only nan in the other condition values) are not included in the
    distribution analysis.
    Input: df with all values, metrics and metadata
    Returns: input df split in two sub-df: one without specific proteins ('res') and the other only with specific
    proteins ('specific_proteins')
    """
    specific_proteins = df[df['specific'] != "both"]

    df["analyse_in_distr"] = "OK"
    df["analyse_in_distr"] = np.where(df["specific"] != "both", np.nan, df["analyse_in_distr"])

    res = df.dropna(subset=["analyse_in_distr"], axis=0)

    return res, specific_proteins



def get_best_fit(input_array, out_file):
    matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
    matplotlib.style.use('ggplot')
    """Return the best fit distribution to data and its parameters"""

    # Load data
    data = pd.Series(input_array)

    # Find best fit distribution
    best_fit_name, best_fit_params = best_fit_distribution(data, 200)

    best_dist = getattr(stats, best_fit_name)

    # Make probability density function (PDF) with best params
    pdf = make_pdf(best_dist, best_fit_params)

    # parameters
    param_names = (best_dist.shapes + ', loc, scale').split(', ') if best_dist.shapes else ['loc', 'scale']
    print(best_fit_params)

    # get significant numbers
    sn = 3
    # for n, p in zip(param_names, best_fit_params):
    #     if n == "scale" or n == "loc":
    #         continue
    #     while float('{0:.{1}f}'.format(p, sn)) == 0:
    #         sn += 1

    # pour a > 0:
    # param_str = ', '.join(['{}={:0.{}f}'.format(k, v, sn) if k != "a" else '{}={:0.6f}'.format(k, v) for k, v in zip(param_names, best_fit_params) ])
    param_str = ', '.join(['{}={:0.{}f}'.format(k, v, sn) for k, v in zip(param_names, best_fit_params)])
    dist_str = '{} ({})'.format(best_fit_name, param_str)

    # old way
    # param_str = ', '.join(['{}={:0.2f}'.format(k, v) for k, v in zip(param_names, best_fit_params)])
    # dist_str = '{} ({})'.format(best_fit_name, param_str)

    print("dist_str : ", dist_str)

    # # Display
    param_str_plot = ', '.join(['{}={:0.2f}'.format(k, v) for k, v in zip(param_names, best_fit_params)])
    dist_str_plot = '{} ({})'.format(best_fit_name, param_str_plot)
    plot_best_fit(data, dist_str_plot, pdf, out_file)

    return best_dist, best_fit_name, param_str



def best_fit_distribution(data, bins=200):

    matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
    matplotlib.style.use('ggplot')

    """Model data by finding best fit distribution to data"""
    # Get histogram of original data
    y, x = np.histogram(data, bins=bins, density=True)

    x = (x + np.roll(x, -1))[:-1] / 2.0

    DISTRIBUTIONS = get_scipy_distributions()
    print(len(DISTRIBUTIONS))
    DISTRIBUTIONS=DISTRIBUTIONS[1:100]
    # Best holders
    best_distribution = stats.norm
    best_params = (0.0, 1.0)
    best_sse = np.inf

    # Estimate distribution parameters from data
    for distribution in DISTRIBUTIONS:
        print(distribution)
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
                    print("Distribution : {}" / format(distribution))
                    print(arg)

        except Exception:
            pass

    return best_distribution.name, best_params


def get_scipy_distributions():
    distribution_list = []
    print(_distn_names)
    for dist in _distn_names:
        if dist != "levy_stable":
            distribution_list.append(dist)

    stats_distributions = [getattr(stats, d) for d in distribution_list]

    return stats_distributions



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


def plot_best_fit(data, dist_str, pdf, out_file):
    # #plot methode alternative https://stackoverflow.com/questions/6620471/fitting-empirical-distribution-to-theoretical-ones-with-scipy-python
    # plt.figure(figsize=(12, 8))
    # ax = data.plot(kind='hist', bins=50, density=True, alpha=0.5, label = 'Data', legend = True)

    plt.figure(figsize=(12, 8))
    plt.hist(data, bins=150, density=True, alpha=0.5, label='Data')
    plt.plot(pdf, lw=2, label='PDF')
    plt.legend(loc='upper right', shadow=True, fontsize='x-large')
    plt.title(u'Best fit distribution \n' + dist_str)
    plt.xlabel(u'z-score')
    plt.ylabel('frequency')
    # plt.set_title(u'Best fit distribution \n' + dist_str)
    plt.savefig(out_file)
    return
