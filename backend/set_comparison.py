#!/usr/bin/env python

from utils import *


#create the parser
parser = argparse.ArgumentParser(description= 'Search for proteins present only in one condition and produce a venn diagram')
parser.add_argument('-i', '--input_file')
parser.add_argument('-o', '--output_file')
parser.add_argument('-dataset')
parser.add_argument('-r', '--ref', default = 'reference', type=str, help='Control columns')
parser.add_argument('-id_col', type=str)

#get arguments
args = vars(parser.parse_args())
input_file=args['input_file']
output_file=args['output_file']
dataset = args['dataset']
ref = args['ref']
id_col = args['id_col']

check_dir(get_filepath(output_file))
check_dir(get_logpath(output_file))

id_col = 'Accession'
logging.basicConfig(filename=get_logpath(output_file) + '/setcomparison.log', level=logging.INFO)
logging.info('Starting comparing samples for specific proteins...')

input_df = pd.read_csv(input_file, sep=",", index_col= 0, header=0)
dict_name = get_filename(input_file).split('_')[0]

d =  {"Polyphenolprot190725aPV": "Polyphenolprot190725a.Manip7-1", "Polyphenolprot190725c" : "Polyphenolprot190725c.Manip9",
      "Polyphenolprot190725aPVC" : "Polyphenolprot190725a.Manip7_BgNoise",
      "PolyPhenolProt190423" : "PolyPhenolProt190423.Manip6", "PolyPhenolProt190320b" : "PolyPhenolProt190320.Manip5-2",
      "PolyPhenolProt190320a" : "PolyPhenolProt190320.Manip5-1",
      "Polyphenolprot190725aa" : "Polyphenolprot190725a.Manip7_BgNoise"}

cdict_name = ' '.join([d.get(i, i) for i in dict_name.split()])
abundance_df = input_df.filter(regex = 'GR')

reference = [x for x in abundance_df.columns.values if ref in x]
condition = [x for x in abundance_df.columns.values if ref not in x]

reference_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in reference]))[0]
condition_name = list(set([re.search(r"(?<=SA_).*?(?=_REP)", col).group(0) for col in condition]))[0]

cond_spec = []
ref_spec = []
not_spec = []

input_df.reset_index(drop=True, inplace=True)
output_df = input_df.copy()

for protein in input_df.index.values:
    accession = input_df.loc[protein, id_col]

    reference_abundancies = np.array(input_df.loc[protein][reference].map(lambda x: atof(x) if type(x) == str else x))
    condition_abundancies = np.array(input_df.loc[protein][condition].map(lambda x: atof(x) if type(x) == str else x))

    n_NA_ref = np.count_nonzero(np.isnan(reference_abundancies))
    n_NA_cond = np.count_nonzero(np.isnan(condition_abundancies))

    ## File already without problematic NA
    # Proteine spécifique à la capture
    if n_NA_ref == 3:
        if n_NA_cond < 2:
            output_df.loc[protein, 'Venn_{}_{}'.format(condition_name, reference_name)] = 1
            cond_spec.append(accession)

    # Protéine spécifique au controle
    elif n_NA_cond == 3:
        if n_NA_ref < 2:
            output_df.loc[protein, 'Venn_{}_{}'.format(condition_name, reference_name)] = -1
            ref_spec.append(accession)

    # Protéine présente dans les deux conditions
    else:
        output_df.loc[protein, 'Venn_{}_{}'.format(condition_name, reference_name)] = 0
        not_spec.append(accession)


# Plot Venn Diagram
logging.info('Comparing ' + condition_name + ' to ' +  reference_name)
logging.info(str(len(cond_spec)) + ' proteins are specific to ' + str(condition_name) + ', and ' + str(len(ref_spec)) + ' to ' + str(reference_name))

cond_set = set(cond_spec + not_spec)
ref_set = set(ref_spec + not_spec)

cols = sns.color_palette(['orange', 'b'])

cond_dict =  {"OCVescalaginOx": "OC-Vg-C+", "OCVescalaginNox" : "OC-Vg-D",
              "OCVescalinOx" : "OC-Vl-C+",  "OCVescalinNox" : "OC-Vl-D",
              "OBVescalaginOx": "OB-Vg-C+", "OBVescalaginNox" : "OB-Vg-D",
              "OBVescalinOx" : "OB-Vl-C+",  "OBVescalinNox" : "OB-Vl-D",
              "OCCtrlOx" : "OC-∅-C+", "OCCtrlNox" : "OC-∅-D",
              "OBCtrlOx" : "OB-∅-C+", "OBCtrlNox" : "OB-∅-D",
              "OCPiceatannol" : "OC-Pic-C+", "OBPiceatannol" : "OB-Pic-C+",
              "OCResveratrol" : "OC-Res-C+", "OBResveratrol" : "OB-Res-C+",
              "OCVescalagin" : "OC-Vg-C+", "OBVescalagin" : "OB-Vg-C+",
              "OCVescalin" : "OC-Vl-C+", "OBVescalin" : "OB-Vl-C+",
              "OCControl" : "OC-∅-C+", "OBControl" : "OB-∅-C+",
              "SansOx" : "∅-",
              "AvecOx" : "∅60+",
              "Control": "Control"
              #"Control": "∅60+",
              }


ccapture_name = ' '.join([cond_dict.get(i, i) for i in condition_name.split()])
creference_name = ' '.join([cond_dict.get(i, i) for i in reference_name.split()])

plt.figure()

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 18

plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=SMALL_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

mv.venn2_unweighted([cond_set, ref_set], [ccapture_name, creference_name], set_colors=cols)
plt.suptitle('{} \n {} vs. {}'.format(cdict_name, ccapture_name, creference_name), fontsize=16)
#plt.set_title('{}'.dict_name)

dir_png = 'data/' + dataset +'/Figures/VennDiagram/'

try:
    check_dir(dir_png)
except OSError:
    os.makedirs(dir_png)

output_png = dir_png + get_filename(output_file) + '.png'


plt.savefig(output_png)
plt.close()


try:
    output_df.to_csv(output_file, index=False)
    logging.info(' Writing in ' + output_file)

except TypeError as e:

    logging.info(' Error writing output file:  ' + e + '...')

logging.info(' ------------------')