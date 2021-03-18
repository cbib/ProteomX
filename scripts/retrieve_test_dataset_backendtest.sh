#!/usr/bin/env bash

echo "Removing previous dataset test folder"
rm -rf ./data_folder/dataset_test1/

echo "Creating appropriate folders"
mkdir -p ./data_folder/dataset_test1/xlsx/
mkdir -p ./data_folder/dataset_test1/dummy_data/

echo "Retrieving data..."
printf "\n... xslx data file\n"
curl -k https://services.cbib.u-bordeaux.fr//prestations/ProteomX_sprint/dataset_test1/test1.xlsx -o data_folder/dataset_test1/xlsx/test1.xlsx
printf "\n... mapping info\n"
curl -k https://services.cbib.u-bordeaux.fr//prestations/ProteomX_sprint/dataset_test1/mapping_info_test1.csv -o data_folder/dataset_test1/dummy_data/mapping_info_test1.csv
printf "\n...config_file.json (template)\n"
curl -k https://services.cbib.u-bordeaux.fr//prestations/ProteomX_sprint/TEMPLATE_config_file.json -o resources/TEMPLATE_config_file.json

echo "DONE"
