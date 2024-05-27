#!/usr/bin/env bash

if [ -d "/data/ExampleProject/" ]; then
  rm -rf "/data/ExampleProject/"
fi


mkdir -p /data/ExampleProject/xlsx/
mkdir -p /data/ExampleProject/mapping/
mkdir -p /data/ExampleProject/log/

curl -k https://services.cbib.u-bordeaux.fr/proteomx_dataset/ExampleProject/xlsx/ExampleProject.xlsx -o /data/ExampleProject/xlsx/ExampleProject.xlsx
curl -k https://services.cbib.u-bordeaux.fr/proteomx_dataset/ExampleProject/mapping/mapping_ExampleProject.csv -o /data/ExampleProject/mapping/mapping_ExampleProject.csv
curl -k https://services.cbib.u-bordeaux.fr/proteomx_dataset/ExampleProject/mapping/comparison_ExampleProject.csv -o /data/ExampleProject/mapping/comparison_ExampleProject.csv
curl -k https://services.cbib.u-bordeaux.fr/proteomx_dataset/ExampleProject/config_file.json -o /data/ExampleProject/config_file.json
