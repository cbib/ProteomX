#!/usr/bin/env bash

echo "Removing previous dataset test folder"
if [ -d "./data/ExampleProject/" ]; then
  rm -rf "./data/ExampleProject/"
fi

echo "Creating appropriate folders"
mkdir -p ./data/ExampleProject/xlsx/
mkdir -p ./data/ExampleProject/mapping/

echo "Retrieving data..."
printf "\n... xslx data file\n"
curl -k https://services.cbib.u-bordeaux.fr/proteomx_dataset/ExampleProject/xlsx/ExampleProject.xlsx -o data/ExampleProject/xlsx/ExampleProject.xlsx
printf "\n... mapping info\n"
curl -k https://services.cbib.u-bordeaux.fr/proteomx_dataset/ExampleProject/mapping/mapping_ExampleProject.csv -o data/ExampleProject/mapping/mapping_ExampleProject.csv
printf "\n... mapping info\n"
curl -k https://services.cbib.u-bordeaux.fr/proteomx_dataset/ExampleProject/mapping/comparison_ExampleProject.csv -o data/ExampleProject/mapping/comparison_ExampleProject.csv
printf "\n...config_file.json (template)\n"
curl -k https://services.cbib.u-bordeaux.fr/proteomx_dataset/ExampleProject/config_file.json -o data/ExampleProject/config_file.json

echo "DONE"
