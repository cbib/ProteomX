#!/usr/bin/env python

from utils import *


#create the parser
parser = argparse.ArgumentParser(description='Filter proteins lists according to different criteria')
parser.add_argument('-i', '--input_file')
parser.add_argument('-o', '--output_file')
parser.add_argument('-specific', type=str, help='keep specific proteins ? "all" / "reference" / "condition"')
parser.add_argument('-column', nargs='+') # MEME ORDRE POUR COLUMN / TYPE / VALUE
parser.add_argument('-type', nargs='+')
parser.add_argument('-value', nargs='+')
parser.add_argument('-id_col')


#get arguments
args = vars(parser.parse_args())
input_file=args['input_file']
output_file=args['output_file']
specific = args['specific']
id_col = args['id_col']

column = args['column']
type = args['type']
value = args['value']


check_dir(get_filepath(output_file))
check_dir(get_logpath(output_file))

logging.basicConfig(filename=get_logpath(output_file) + '/filtering_distribution.log', level=logging.INFO)
logging.info('Starting filtering proteins...')

input_df = read_csv_file(input_file, "input file", sep=",",index_col=0,header=0)


len_before = len(input_df)
selected_df = input_df.copy()

# Create dictionary with selection filters
selection = autovivify(1, list)
for (col, type, value) in zip(column, type, value):
     selection[col] = {}
     selection[col]['type'] = type
     selection[col]['value'] = value

# dict test
# selection = {'ratio' :  {'type' : 'superieur', 'value' : 2}, 'overlap' : {'type' : 'inferieur',  'value' : 0}}


for criteria in selection:
    selection_type = selection[criteria]['type']
    selection_value = float(selection[criteria]['value'])
    print(criteria, selection_type, selection_value)

    col_to_filter = selected_df.filter(regex=criteria)
    col_name = col_to_filter.columns.tolist()[0]
    print(col_name)

    if selection_type == 'inferieur':
        selected_df = selected_df[selected_df[col_name] < selection_value]

    elif selection_type == 'superieur':
        selected_df = selected_df[selected_df[col_name] > selection_value]

    elif selection_type == 'interval': # ]-a;+a[
        selected_df = selected_df[selected_df[col_name] > - selection_value]
        selected_df = selected_df[selected_df[col_name] < selection_value]
    # ]a;b[ ?
    elif selection_type == 'inversed_interval': # ]-∞;-a[ U ]a;+∞[
        selected_df = selected_df[selected_df[col_name] < - selection_value]
        selected_df = selected_df[selected_df[col_name] > selection_value]

    elif selection_type == 'keep_unique_value':
        selected_df = selected_df[selected_df[col_name] == selection_value]

    elif selection_type == 'discard_unique_value':
        selected_df = selected_df[selected_df[col_name] != selection_value]

if specific != None:
    ratio = input_df.filter(regex = 'ratio_')
    ratio_col = ratio.columns.tolist()[0]
    if specific == 'all':
        specific_neg = input_df[input_df[ratio_col] == 0.001]
        selected_df = selected_df.append(specific_neg, ignore_index = True)
        specific_pos = input_df[input_df[ratio_col] == 1000]
        selected_df = selected_df.append(specific_pos, ignore_index=True)
    elif specific == 'reference':
        specific = input_df[input_df[ratio_col] == 0.001]
        selected_df = selected_df.append(specific, ignore_index = True)
    elif specific == 'condition':
        specific = input_df[input_df[ratio_col] == 1000]
        selected_df = selected_df.append(specific, ignore_index=True)


selected_df = selected_df[~selected_df.duplicated(subset=id_col, keep='first')]
print(selected_df.head())
len_after = len(selected_df)
percent_kept = 100 * len_after / len_before
prot_discarded = len_before - len_after

print(round(percent_kept,2), '% of all proteins have been kept ({} proteins discarded and {} kept)'.format(prot_discarded, len_after))
logging.info(' {} proteins ({} % of all proteins) have been kept.'.format(len_after, str(round(percent_kept,2))))

try:
    selected_df = selected_df.sort_values('pvalue')
    selected_df.to_csv(output_file, index=False)
    logging.info(' Writing in ' + output_file)

except TypeError as e:

    logging.info(' Error writing output file:  ' + e + '...')

logging.info(' ------------------')