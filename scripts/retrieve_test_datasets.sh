#!/usr/bin/env bash

curl https://services.cbib.u-bordeaux.fr//prestations/ProteomX_sprint/ProteomX_sprint_rawData.xlsx -o data/proteomX/sample/raw_data/ProteomX_sprint_rawData.xlsx
curl https://services.cbib.u-bordeaux.fr//prestations/ProteomX_sprint/mapping_ProteomX_sprint_rawData.csv -o data/proteomX/sample/mapping/mapping_ProteomX_sprint_rawData.csv
curl https://services.cbib.u-bordeaux.fr//prestations/ProteomX_sprint/config_file.json -o config_files/proteomX/sample/config_file.json
