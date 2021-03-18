#!/usr/bin/env bash
rm -rf ./data_folder/dataset_test1/

mkdir ./data_folder/dummy_data/

scp -r https://services.cbib.u-bordeaux.fr//prestations/ProteomX_sprint/dataset_test1/ ./data_folder/



