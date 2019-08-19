FROM camptocamp/c2cwsgiutils:3 AS base
LABEL maintainer Camptocamp "info@camptocamp.com"

ARG VERSION
ENV VERSION=$VERSION

ENV \
  DEBIAN_FRONTEND=noninteractive \
  SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

RUN \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends apt-utils && \
  apt-get install --assume-yes --no-install-recommends gettext postgresql-client && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN \
  python3 -m pip install --disable-pip-version-check --no-cache-dir --requirement=/tmp/requirements.txt && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*


#############################################################################################################
# Finally used by upgrader

FROM base AS base-upgrader

RUN \
  . /etc/os-release && \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends git && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/* && \
  curl https://raw.githubusercontent.com/awslabs/git-secrets/1.3.0/git-secrets > /usr/bin/git-secrets


#############################################################################################################
# Finally used by runner and builder

FROM base AS base-node

ENV NODE_PATH=/usr/lib/node_modules
RUN \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends apt-transport-https chromium-browser && \
  . /etc/os-release && \
  echo "deb https://deb.nodesource.com/node_10.x ${VERSION_CODENAME} main" > /etc/apt/sources.list.d/nodesource.list && \
  curl --silent https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends 'nodejs=10.*' && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*


#############################################################################################################
# Finally used by runner

FROM base-node AS base-runner

COPY bin/npm-packages /usr/bin/
COPY package.json /tmp/
RUN \
  cd /tmp && \
  npm-packages --src=package.json --dst=npm-packages && \
  npm --no-optional --global --unsafe-perm --no-package-lock install $(cat npm-packages) && \
  npm cache clear --force && \
  rm -rf /tmp/*

WORKDIR /app/c2cgeoportal/geoportal


#############################################################################################################
# Finally used by builder

FROM base-node AS common-build

COPY requirements-dev.txt /tmp/
RUN \
  . /etc/os-release && \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends git make postgresql-client-10 net-tools iputils-ping \
  vim vim-editorconfig vim-addon-manager tree && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/* && \
  vim-addon-manager --system-wide install editorconfig && \
  echo 'set hlsearch  " Highlight search' > /etc/vim/vimrc.local && \
  echo 'set wildmode=list:longest  " Completion menu' >> /etc/vim/vimrc.local && \
  echo 'set term=xterm-256color " Make home and end working' >> /etc/vim/vimrc.local
RUN \
  python3 -m pip install --disable-pip-version-check --no-cache-dir --requirement=/tmp/requirements-dev.txt && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*

# For awscli
COPY etc/bash_completion.d/* /etc/bash_completion.d/

# For mypy
RUN \
  touch /usr/local/lib/python3.7/dist-packages/zope/__init__.py && \
  touch /usr/local/lib/python3.7/dist-packages/c2c/__init__.py


#############################################################################################################
# Build files for builder

FROM common-build AS build1

ARG MAJOR_VERSION
ENV MAJOR_VERSION=$MAJOR_VERSION

RUN \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends libxml2-utils && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*

COPY bin/npm-packages /usr/bin/
COPY geoportal/package.json /app/c2cgeoportal/geoportal/
WORKDIR /app/c2cgeoportal/geoportal
RUN \
  npm-packages --src=package.json --dst=/tmp/npm-packages && \
  npm --no-optional --global --unsafe-perm --no-package-lock install `cat /tmp/npm-packages` && \
  npm cache clear --force && \
  rm -rf /tmp/*

RUN npm-packages \
  @camptocamp/cesium @type jasmine-core karma karma-chrome-launcher karma-coverage \
  karma-coverage-istanbul-reporter karma-jasmine karma-sourcemap-loader karma-webpack \
  typedoc \
  --src=/usr/lib/node_modules/ngeo/package.json --src=package.json --dst=npm-packages

COPY admin/package.json /app/c2cgeoportal/admin/
WORKDIR /app/c2cgeoportal/admin
RUN \
  npm --no-optional --no-package-lock install && \
  npm cache clear --force && \
  rm -rf /tmp/*


#############################################################################################################
# Base image for builder

FROM common-build AS common-build-npm

COPY --from=build1 /app/c2cgeoportal/geoportal/npm-packages /opt/npm-packages
RUN \
  npm install --no-optional --global --unsafe-perm --no-package-lock $(cat /opt/npm-packages) && \
  npm cache clear --force && \
  rm -rf /tmp/*
RUN \
  git clone --branch=v1.7.x --depth=1 --single-branch https://github.com/angular/angular.js.git \
  /tmp/angular && \
  mv /tmp/angular/src/ngLocale/ /opt/angular-locale/ &&\
  rm -rf /tmp/angular
RUN \
  curl --output /opt/jasperreport.xsd http://jasperreports.sourceforge.net/xsd/jasperreport.xsd


#############################################################################################################
# Build files for builder

FROM build1 AS build

COPY . /app/c2cgeoportal/
WORKDIR /app/c2cgeoportal
COPY bin/import-ngeo-apps bin/eval-templates bin/wait-db bin/transifex-init /usr/bin/
RUN make build
RUN python3 -m pip install --editable=commons --editable=geoportal --editable=admin


#############################################################################################################
# Image used to build the project

FROM common-build-npm AS builder

WORKDIR /src

COPY bin/eval-templates /usr/bin/
COPY --from=build /app/c2cgeoportal/geoportal/c2cgeoportal_geoportal/locale/ \
    /opt/c2cgeoportal_geoportal/c2cgeoportal_geoportal/locale/


#############################################################################################################
# Intermediate image used to prepare the copy files to upgrade image

FROM build AS build-upgrade

RUN rm --recursive --force /app/c2cgeoportal/*/tests


#############################################################################################################
# Intermediate image used to prepare the copy files to run image

FROM build-upgrade AS build-run

RUN rm --recursive --force /app/c2cgeoportal/geoportal/c2cgeoportal_geoportal/scaffolds


#############################################################################################################
# Image used to run the project

FROM base-runner AS runner

COPY bin/eval-templates bin/wait-db bin/update-po bin/list4vrt /usr/bin/
COPY --from=build-run /app/c2cgeoportal/commons /opt/c2cgeoportal_commons
COPY --from=build-run /app/c2cgeoportal/geoportal /opt/c2cgeoportal_geoportal
COPY --from=build-run /app/c2cgeoportal/admin /opt/c2cgeoportal_admin
COPY --from=build1 /usr/lib/node_modules/ngeo/buildtools/check-example.js /usr/bin/

RUN \
  ln -s /opt/c2cgeoportal_commons/c2cgeoportal_commons/alembic /opt && \
  python3 -m pip install --disable-pip-version-check --no-cache-dir --no-deps \
    --editable=/opt/c2cgeoportal_commons \
    --editable=/opt/c2cgeoportal_geoportal \
    --editable=/opt/c2cgeoportal_admin

RUN adduser www-data root


#############################################################################################################
# Image used to upgrade the project

FROM base-upgrader AS upgrader

ARG VERSION
ENV VERSION=$VERSION

WORKDIR /src
COPY bin/run bin/run-git /usr/bin/
COPY --from=build-upgrade /app/c2cgeoportal/commons /opt/c2cgeoportal_commons
COPY --from=build-upgrade /app/c2cgeoportal/geoportal /opt/c2cgeoportal_geoportal

RUN \
  python3 -m pip install --disable-pip-version-check --no-cache-dir --no-deps \
    --editable=/opt/c2cgeoportal_commons \
    --editable=/opt/c2cgeoportal_geoportal && \
  pcreate -l|grep c2cgeoportal


#############################################################################################################
# Image that run the checks

FROM build AS checks
RUN make checks