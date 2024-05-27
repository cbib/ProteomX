FROM ubuntu:22.04
ENV TIMEZONE=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TIMEZONE /etc/localtime && echo $TIMEZONE > /etc/timezone
RUN apt-get update \
  && apt-get -y install build-essential \
  && apt-get install -y wget \
  && apt-get install -y apt-utils \
  && rm -rf /var/lib/apt/lists/* \
  && wget -N https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-Linux-aarch64.sh \
      -q -O /tmp/cmake-install.sh \
      && chmod u+x /tmp/cmake-install.sh \
      && mkdir /opt/cmake-3.28.1 \
      && /tmp/cmake-install.sh --skip-license --prefix=/opt/cmake-3.28.1 \
      && rm /tmp/cmake-install.sh \
      && ln -s /opt/cmake-3.28.1/bin/* /usr/local/bin
RUN apt-get update \
  && apt-get remove -y python \
  && apt-get install -y python3.9 r-base python3-pip python-is-python3
COPY requirements.txt /backend/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /backend/requirements.txt
ENV R_VERSION=4.3.0
RUN apt-get install -y libcurl4-openssl-dev
RUN apt-get install -y x11-apps
RUN apt-get install -y xvfb xauth xfonts-base
RUN apt-get install -y libx11-dev
RUN apt-get install -y xorg-dev
RUN apt-get install -y curl \
  && curl -O https://cran.rstudio.com/src/base/R-4/R-${R_VERSION}.tar.gz \
  && tar -xzvf R-${R_VERSION}.tar.gz \
  && cd /R-${R_VERSION}
RUN /R-${R_VERSION}/configure \
    --prefix=/opt/R/${R_VERSION} \
    --with-x \
    --enable-R-shlib \
    --enable-memory-profiling \
    --with-blas \
    --with-lapack
RUN make
RUN make install
RUN ln -s /opt/R/${R_VERSION}/bin/R /usr/local/bin/R
RUN ln -s /opt/R/${R_VERSION}/bin/Rscript /usr/local/bin/Rscript
RUN R -e "install.packages('tibble', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('paletteer', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('dplyr', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('factoextra', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('FactoMineR', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('dendextend', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('RColorBrewer', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('argparse', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('dichromat', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('pheatmap', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('tidyverse', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('data.table', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('glue', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('BiocManager', repos='http://cran.us.r-project.org')"
RUN R -e "BiocManager::install('ComplexHeatmap')"
RUN R -e "BiocManager::install('EnhancedVolcano')"
RUN R -e "install.packages('stringr', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('rjson', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('gprofiler2', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('openxlsx', repos='http://cran.us.r-project.org')"
RUN R -e "install.packages('readxl', repos='http://cran.us.r-project.org')"
RUN apt-get install -y libxml2-dev
RUN apt-get install -y libharfbuzz-dev libfribidi-dev libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev libssl-dev
RUN R -e "install.packages('tidyverse', repos='http://cran.us.r-project.org')"
RUN apt-get install -y xfonts-100dpi
RUN apt-get install -y xfonts-75dpi
RUN R -e "install.packages('gprofiler2', repos='http://cran.us.r-project.org')"
ENV PYTHONPATH "${PYTHONPATH}:/backend"
CMD ["/scripts/Docker_run.sh"]
