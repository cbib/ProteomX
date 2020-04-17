# ProteomX

This is the best proteomics analysis pipeline, accessible on the https://services.cbib.u-bordeaux.fr/ProteomX/.

# Prerequisites & Sample run

ProteomX is provided as a stand-alone application as well as a set of docker images.

## Docker based install

The docker image is defined in the main `Dockerfile`.

1. Ensure that docker is installed on your host machine (`docker ps`)
1. From the top level directory, `make image` will build the ProteomX main image
1. Once the image is built :
	1. `make shell` will open a bash shell in a new container, in this container you can :
		1. `/scripts/retrieve_test_dataset_docker.sh` to pull sample datafiles from the CBIB servers
		1. `/scripts/analyse_test_dataset_docker.sh` to run a sample analysis pipeline on the test dataset. Results are available in the `data/proteomX/sample` folder.
	1. `make tests` will run all unit tests
	1. `make serve_ng_dev` will start the angular server and make the app accessible via `http://localhost:4201`
	1. `make serve_ng_prod` is used internally at the CBIB for our production environment
	1. `make serve_api_dev` will start the API and backend container
1. The container shares the following volumes with the host machine :
	1. `data` -> `/data/` where all datasets and results are stored
	1. `config_files` -> `/config_files` where all job configurations are stored
	1. `scripts` -> `/scripts/` where helper maintenance scripts are stored
	1. `backend` -> `/backend/` where the (python) backend code is stored
	1. `frontend/src` -> `/app/src/` where the (angular) fronted code is stored
	1. `api/src` -> `/api/src/` where the (node) API code is stored 

