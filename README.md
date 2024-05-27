# ProteomX_Docker
# ProteomX

# Prerequisites & Sample run

ProteomX is provided as a stand-alone application as well as a set of docker images.

## Docker based install

The docker image is defined in the main `Dockerfile`.

1. Ensure that docker is installed on your host machine (`docker ps`)
1. Go to architecture folder of your host machine (`cd Amd64|cd Arm64`)
1. `./scripts/retrieve_test_dataset.sh` to pull sample datafiles from the CBIB servers
1. From the corresponding architecture directory, `make image` will build the ProteomX main image
1. Once the image is built :
	1. `make shell` will open a bash shell in a new container, in this container you can :
		1. `/scripts/retrieve_test_dataset_docker.sh` to pull sample datafiles from the CBIB servers
		1. `/scripts/analyse_test_dataset_docker.sh` to run a sample analysis pipeline on the test dataset. Results are available in the `data/ExampleProject` folder.
	1. `make tests` will run all unit tests
    1. `make run project=PROJECTNAME` will run all steps of the proteomX pipeline (e.g make run project=ExampleProject)
1. The container shares the following volumes with the host machine :
	1. `data` -> `/data/` where all datasets and results are stored
	1. `config_files` -> `/config_files` where all job configurations are stored
	1. `scripts` -> `/scripts/` where helper maintenance scripts are stored
	1. `backend` -> `/backend/` where the (python) backend code is stored

## Conda based install

1. Ensure that conda is installed on your host machine (`conda info`)
1. Ensure that R is installed on your host machine (`R --version`)
1. `./scripts/retrieve_test_dataset.sh` to pull sample datafiles from the CBIB servers
1. Once the installation is complete :
   1. Run `./scripts/setup.sh` 
      1. to ensure repository integrity
      1. to install conda Proteomix environment if missing
      1. to install R packages if missing sample datafiles from the CBIB servers
   1. `./scripts/Conda_run.sh -i PROJECTNAME` will run all steps of the proteomX pipeline (e.g ./scripts/Conda_run.sh -i ExampleProject)
