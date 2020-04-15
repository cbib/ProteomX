FROM node:12.2.0
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json /app/package.json
RUN npm install
RUN npm install -g @angular/cli@7.3.9
COPY angular.json /app/angular.json
COPY tsconfig.spec.json /app/tsconfig.spec.json
COPY tsconfig.app.json /app/tsconfig.app.json
COPY src/ /app/src
COPY serve_dev.sh /app/serve_dev.sh
COPY serve_prod.sh /app/serve_prod.sh
CMD ["/app/serve_dev.sh"]
