NGVOLUMES= -v ${PWD}/frontend/src:/app/src:delegated
SHAREDVOLUMES= -v ${PWD}/data:/data:delegated  -v ${PWD}/config_files:/config_files:delegated -v ${PWD}/scripts:/scripts:delegated -v ${PWD}/backend/:/backend:delegated -v ${PWD}/frontend/src:/app/src:delegated -v ${PWD}/api/src:/api/src:delegated
ENVVARIABLES= -e PYTHONPATH=/backend:$PYTHONPATH
# -v ${PWD}/frontend/node_modules:/app/node_modules:delegated
image:
	docker build -t example:dev .

serve_ng_dev: image
	# start the ng container and the node + backend container
	docker run  ${NGVOLUMES} -p 4201:4200 --rm example:dev '/scripts/serve_dev.sh'

serve_ng_prod: image
	docker run  ${NGVOLUMES} -p 4201:4200  --rm example:dev '/scripts/serve_prod.sh'

serve_api_dev: image
	# start the ng container and the node + backend container
	docker run  ${SHAREDVOLUMES} -p 4000:4000 --rm example:dev '/scripts/api_start_docker.sh'

shell: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 -p 4000:4000 --rm example:dev bash

tests: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 -p 4000:4000 --rm example:dev '/scripts/run_tests.sh'
