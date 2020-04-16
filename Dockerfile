FROM nikolaik/python-nodejs:python3.8-nodejs13
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY requirements.txt /backend/requirements.txt
RUN pip install -r /backend/requirements.txt
COPY frontend/package.json /app/package.json
RUN npm install
COPY frontend/angular.json /app/angular.json
COPY frontend/tsconfig.spec.json /app/tsconfig.spec.json
COPY frontend/tsconfig.app.json /app/tsconfig.app.json
# node server
WORKDIR /api
ENV PATH /api/node_modules/.bin:$PATH
COPY api/package.json /api/package.json
RUN cd /api && npm install
# copy angular app
COPY frontend/src/ /app/src
COPY scripts/serve_dev.sh /scripts/serve_dev.sh
COPY scripts/serve_prod.sh /scripts/serve_prod.sh
ENV PYTHONPATH "${PYTHONPATH}:/backend"
#increase memory limit for angular
ENV NODE_OPTIONS="--max_old_space_size=8096"
CMD ["/scripts/serve_dev.sh"]
