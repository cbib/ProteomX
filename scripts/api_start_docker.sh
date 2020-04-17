#!/usr/bin/env bash
set -ex
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"

API=$CURRENT_DIR/../api/

cd ${API}/src && NODE_ENV=docker node server.js