# This is a build image meaning that all the dependancies
# will be build in this image and will not clean
# up after itself. In the katana image, we'll copy
# the build artifcats into the newer image
FROM ubuntu:18.04

LABEL maintainer="Scott Havens <scott.havens@usda.gov>"

####################################################
## System requirements
####################################################

RUN echo 'Etc/UTC' > /etc/timezone \
    && ln -s /usr/share/zoneinfo/Etc/UTC /etc/localtime

RUN mkdir -p /build/windninja \
    && cd /build \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
    git \
    gcc \
    g++ \
    cmake \
    make \
    ca-certificates \
    libblas-dev \
    ncdu \
    liblapack-dev \
    libatlas-base-dev \
    libffi-dev \
    libssl-dev \
    gfortran \
    libyaml-dev \
    libfreetype6-dev \
    libcurl4-gnutls-dev \
    libnetcdf-dev \
    libpng-dev \
    python3 \
    python3-pip \
    curl \
    libeccodes-dev \
    libeccodes-tools \
    wget \
    # end windninja
    && curl -L ftp://ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz | tar xz \
    && curl -L https://github.com/firelab/windninja/archive/3.5.0.tar.gz | tar xz \
    && mv windninja-3.5.0 /build/windninja/windninja \
    # && rm -rf /var/lib/apt/lists/* \
    && apt-get remove -y curl \
    && apt-get autoremove -y

####################################################
## Wind Ninja
####################################################
ENV PREFIX=/usr/local
# ENV POPPLER="poppler-0.23.4"
ENV PROJ="proj-4.8.0"
ENV GDAL="gdal-2.0.3"
ENV WNSCRIPTS="/build/windninja/depends"

# Poppler is not really needed for this application which means
# that we can save some time and space by not building it
# RUN mkdir $WNSCRIPTS \
#     && cd $WNSCRIPTS \
#     && apt-get update && apt-get install -y xz-utils pkg-config fontconfig \
#     && wget http://poppler.freedesktop.org/$POPPLER.tar.xz \
#     && tar -xvf $POPPLER.tar.xz \
#     && cd $WNSCRIPTS/$POPPLER \
#     && ./configure --prefix=$PREFIX --enable-xpdf-headers \
#     && make install -j8 \
#     && make clean

# Proj
RUN mkdir -p $WNSCRIPTS/$PROJ \
    && cd $WNSCRIPTS/$PROJ \
    && wget http://download.osgeo.org/proj/$PROJ.tar.gz \
    && tar xvfz $PROJ.tar.gz \
    && cd $PROJ \
    && ./configure --prefix=$PREFIX \
    && make clean \
    && make \
    && make install -j 8 \
    && make clean \
    && cp $PREFIX/include/proj_api.h $PREFIX/lib \
    && rm -rf $WNSCRIPTS/$PROJ

# GDAL
RUN mkdir -p $WNSCRIPTS/$GDAL \
    && cd $WNSCRIPTS/$GDAL \
    && wget http://download.osgeo.org/gdal/2.0.3/$GDAL.tar.gz \
    && tar -xvf $GDAL.tar.gz \
    && cd $GDAL \
    && ./configure --prefix=$PREFIX --with-curl=/usr/bin/curl-config \
    && make -j 8 \
    && make install -j 8 \
    && make clean \
    && ldconfig \
    && rm -rf $WNSCRIPTS/$GDAL

# build windninja
RUN apt-get install -y \
    libfontconfig1-dev \
    qt4-dev-tools \
    libqtwebkit-dev \
    libboost-program-options-dev \
    libboost-date-time-dev \
    libgeos-dev \
    libboost-test-dev \
    && mkdir /build/windninja/build \
    && cd /build/windninja/windninja \
    && cmake -DNINJA_CLI=ON -DNINJAFOAM=OFF -DNINJA_QTGUI=OFF /build/windninja/windninja \
    && make \
    && make install \
    && ldconfig \
    && export WINDNINJA_DATA=/build/windninja/windninja/data \
    && rm -rf /build/windninja/ \
    && apt-get remove -y libfontconfig1-dev libcurl4-gnutls-dev qt4-dev-tools \
    libqtwebkit-dev libgeos-dev libboost-test-dev


####################################################
## WGRIB2
####################################################

ENV CC=gcc
ENV FC=gfortran

RUN cd /build/grib2 \
    && make \
    && make lib \
    && cp wgrib2/wgrib2 /usr/local/bin/wgrib2 \
    && make deep-clean \
    && rm -rf /build/grib2

####################################################
## clean up
####################################################
RUN apt-get remove -y gcc gcc-7 g++ cmake wget \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /build