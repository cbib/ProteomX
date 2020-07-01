#!/usr/bin/env bash
rm -rf ./data_folder/test/
rm -rf ./data_folder/test_multiple


mkdir ./data_folder/test/
mkdir ./data_folder/test_multiple

scp -r https://services.cbib.u-bordeaux.fr//prestations/ProteomX_sprint/test_multiple/ ./data_folder/



