#!/usr/bin/env bash
set -ex
cd /app/ && ng serve --port 4200 --host 0.0.0.0 --disableHostCheck --verbose --watch
