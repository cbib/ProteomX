SHAREDVOLUMES= -v ${PWD}/data:/data:delegated  -v ${PWD}/config_files:/config_files:delegated -v ${PWD}/scripts:/scripts:delegated -v ${PWD}/backend/:/backend:delegated -v ${PWD}/frontend/src:/app/src:delegated
# -v ${PWD}/frontend/node_modules:/app/node_modules:delegated
image:
	docker build -t example:dev .

serve_dev: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 --rm example:dev '/scripts/serve_dev.sh'

serve_prod: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 --rm example:dev '/scripts/serve_prod.sh'

shell: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 --rm example:dev bash

tests: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 --rm example:dev '/scripts/run_tests.sh'
