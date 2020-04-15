#!/usr/bin/env python

from utils import *


#create the parser
parser = argparse.ArgumentParser(description='Compute CV, plot results and filter proteins under CV threshold')
parser.add_argument('-i', '--input_file')
parser.add_argument('-o', '--output_file')
parser.add_argument('-of', '--output_fig', help = 'Output directory for CV figures')
parser.add_argument('-t', '--threshold', type = float)
parser.add_argument('-dataset')
parser.add_argument('-s', '--specific', type=str, help='to keep proteins even without set comparison previously')
parser.add_argument('-ref', default='reference', type=str)


#get arguments
args = vars(parser.parse_args())
input_file=args['input_file']
output_file=args['output_file']
output_fig=args['output_fig']
threshold=args['threshold']
dataset = args['dataset']
specific = args['specific']
ref = args['ref']

check_dir(get_filepath(output_file))
check_dir(get_logpath(output_file))


check_dir(get_filepath(output_fig))
check_dir(get_logpath(output_fig))

logging.basicConfig(filename=get_logpath(output_file) + '/CV.log', level=logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s')
logging.info(' Starting checking quality of the data...')


input_df = read_csv_file(input_file, "input file", sep=",",index_col=0,header=0)
dict_name = get_filename(input_file).split('_')[0]

""" Compute CV """
abundance_df = input_df.filter(regex='GR')
reference = [x for x in abundance_df.columns.values if ref in x]
condition = [x for x in abundance_df.columns.values if ref not in x]

reference_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in reference]))[0]
condition_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in condition]))[0]

for protein in input_df.index.values:
    reference_abundancies = np.array(input_df.loc[protein][reference].map(lambda x: atof(x) if type(x) == str else x))
    condition_abundancies = np.array(input_df.loc[protein][condition].map(lambda x: atof(x) if type(x) == str else x))

    input_df.loc[protein, 'CV_{}'.format(condition_name)] = np.nan
    input_df.loc[protein, 'CV_{}_reference'.format(reference_name)] = np.nan

    CV_reference = np.nanstd(reference_abundancies) / np.nanmean(reference_abundancies)
    input_df.loc[protein, 'CV_{}_reference'.format(reference_name)] = CV_reference
    CV_condition = np.nanstd(condition_abundancies) / np.nanmean(condition_abundancies)
    CV_condition = np.nanstd(condition_abundancies) / np.nanmean(condition_abundancies)
    input_df.loc[protein, 'CV_{}'.format(condition_name)] = CV_condition

len_before = len(input_df)


""" Export all proteins to check"""
output_wo_filtering = get_filepath(output_file) + '/tmp/' + get_filename(input_file) + '_all.csv'
check_dir(get_filepath(output_wo_filtering))
input_df.to_csv(output_wo_filtering)
logging.info(' Writing in ' + output_wo_filtering)

""" Plot CV histogram & boxplot """
output_fig = 'data/' + dataset + '/Figures/CV/' + get_filename(input_file)
check_dir(get_filepath(output_fig))
plot_CV(get_filename(input_file), input_df, output_fig, bins=150, threshold=threshold)
plot_cvs_by_sample_claire(get_filename(input_file), output_fig, input_df, dict_name)

""" Filter results """
col_cv = input_df.filter(regex = '^CV_*')
logging.info('CV : len({}), col({})'.format(len(col_cv.columns), col_cv.columns))
print(col_cv.columns)
for a in col_cv:
     col_cv = col_cv[col_cv[a] < threshold]
result_df = input_df.ix[col_cv.index.values]


input_df.reset_index(drop=True, inplace=True)
if specific == 'y':
    cv_col = input_df.filter(regex='^CV_')
    cv_col_ctrl = [col for col in cv_col.columns.values if ref in col]
    cv_col_sample = [col for col in cv_col if ref not in col]

    for i in input_df.index.values:
        capture = input_df.loc[i][cv_col_sample]
        ctrl = input_df.loc[i][cv_col_ctrl]
        if 0 < capture.values < threshold and ctrl.values != ctrl.values:
            result_df = result_df.append(input_df.iloc[i])

        elif 0 < ctrl.values < threshold and capture.values != capture.values:
            result_df = result_df.append(input_df.iloc[i])


result_df.to_csv(output_file)
len_after = len(result_df)
percent_kept = 100 * len_after / len_before

logging.info('Comparison ' + get_filename(input_file) + ' : ' + str(round(percent_kept,2)) + '% of all proteins have been kept')
print(round(percent_kept,2), '% of all proteins have been kept')

try:
    result_df.to_csv(output_file)
    logging.info(' Writing in ' + output_file)

except TypeError as e:

    logging.info(' Error writing output file:  ' + e + '...')

logging.info(' ------------------')