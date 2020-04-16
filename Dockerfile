FROM nikolaik/python-nodejs:python3.8-nodejs13
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY requirements.txt /backend/requirements.txt
RUN pip install -r /backend/requirements.txt
COPY frontend/package.json /app/package.json
RUN npm install
RUN npm install -g @angular/cli@7.3.9
RUN npm install -g @angular/cdk
RUN npm install -g rxjs
RUN npm install -g schematics-utilities
RUN npm install -g @angular/material
RUN npm install -g angular-datatables
COPY frontend/angular.json /app/angular.json
COPY frontend/tsconfig.spec.json /app/tsconfig.spec.json
COPY frontend/tsconfig.app.json /app/tsconfig.app.json
COPY frontend/src/ /app/src
COPY scripts/serve_dev.sh /scripts/serve_dev.sh
COPY scripts/serve_prod.sh /scripts/serve_prod.sh
# node server
WORKDIR /api
ENV PATH /api/node_modules/.bin:$PATH
COPY api/package.json /api/package.json
RUN cd /api && npm install
ENV PYTHONPATH "${PYTHONPATH}:/backend"
CMD ["/scripts/serve_dev.sh"]
