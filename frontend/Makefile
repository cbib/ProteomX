image:
	docker build -t example:dev .

serve_dev: image
	docker run -it -v ${PWD}/src:/app/src -v /app/node_modules -p 4201:4200 --rm example:dev '/app/serve_dev.sh'

serve_prod: image
	docker run -it -v ${PWD}/src:/app/src -v /app/node_modules -p 4201:4200 --rm example:dev '/app/serve_prod.sh'

shell: image
	docker run -it -v ${PWD}/src:/app/src -v /app/node_modules -p 4201:4200 --rm example:dev bash
