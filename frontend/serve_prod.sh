#!/usr/bin/env bash
set -ex
ng serve --port 4200 --host 0.0.0.0 --disableHostCheck --base-href /ProteomX/ --deploy-url /ProteomX/ --public-host https://services.cbib.u-bordeaux.fr/ProteomX/
