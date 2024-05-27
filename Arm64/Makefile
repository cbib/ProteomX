SHAREDVOLUMES= -v ${PWD}/../data:/data:delegated  -v ${PWD}/../logging.conf:/logging.conf:delegated -v ${PWD}/../resources:/resources:delegated -v ${PWD}/../resources/annotation_data:/resources/annotation_data:delegated -v ${PWD}/../config_files:/config_files:delegated -v ${PWD}/../scripts:/scripts:delegated -v ${PWD}/../backend/:/backend:delegated
ENVVARIABLES= -e PYTHONPATH=/backend:$PYTHONPATH

image:
	docker build -t proteomix_arm64:dev .
shell: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 -p 4000:4000 --rm proteomix_arm64:dev bash

tests: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 -p 4000:4000 --rm proteomix_arm64:dev '/scripts/run_tests.sh'

run: image
	docker run -it ${SHAREDVOLUMES} -p 4201:4200 -p 4000:4000 --rm proteomix_arm64:dev '/scripts/Docker_run.sh' -i $(project)
