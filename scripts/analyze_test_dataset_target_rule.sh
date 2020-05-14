#!/usr/bin/env bash

# setup venv
while getopts "i:t:r:" opt; do
	case $opt in
		t)
			target=$OPTARG
			;;
		i)
			file=$OPTARG
			;;
		r)
			rerun=$OPTARG
			;;
		\?)
      		echo "Invalid option: -$OPTARG" >&2
      		exit 1
      ;;
	esac
done


CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACK_DIR=$CURRENT_DIR/../backend/
VENV_DIR=$CURRENT_DIR/../venv/

source ${VENV_DIR}/bin/activate
export PYTHONPATH=${BACK_DIR}:$PYTHONPATH


echo "$rerun"
echo "$file"
echo "$target"
 	
if [ $rerun = "False" ]
then
	snakemake -p -s ${BACK_DIR}/Snakefile --config file_id="$file" target="$target"
elif [ $rerun = "True" ]
then
	snakemake -p -s ${BACK_DIR}/Snakefile --config file_id="$file" target="$target" -R $target
fi

