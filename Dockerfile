# Katana is built on a ubuntu 18.04 image
FROM ubuntu:18.04

MAINTAINER Micah Sandusky <micah.sandusky@ars.usda.gov>

# create a working directory
RUN mkdir -p /code \
    && mkdir -p /code/katana \
    && mkdir -p /packages \
    && mkdir -p /packages/wind

####################################################
# System requirements
####################################################

RUN echo 'Etc/UTC' > /etc/timezone \
    && ln -s /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && apt-get update -y \
    && apt-get install -y build-essential man \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libblas-dev \
    git \
    cmake \
    liblapack-dev \
    libatlas-base-dev \
    libffi-dev \
    libssl-dev \
    gfortran \
    libyaml-dev \
    libfreetype6-dev \
    libpng-dev \
    # libhdf5-serial-dev \
    python3-dev \
    python3-pip \
    python3-tk \
    curl \
    libeccodes-dev \
    libeccodes-tools \
    # more for windninja
    libfontconfig1-dev \
    libcurl4-gnutls-dev \
    libnetcdf-dev \
    qt4-dev-tools \
    libqtwebkit-dev \
    libboost-program-options-dev \
    libboost-date-time-dev \
    libgeos-dev \
    libboost-test-dev \
    wget \
    # end windninja
    && cd /code \
    && curl -L ftp://ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz | tar xz \
    && curl -L https://github.com/firelab/windninja/archive/3.5.0.tar.gz | tar xz \
    && mv windninja-3.5.0 windninja \
    && mv windninja /packages/wind \
    && rm -rf /var/lib/apt/lists/* \
    && apt remove -y curl \
    && apt autoremove -y

####################################################
# Wind Ninja
####################################################
ENV PREFIX=/usr/local
ENV POPPLER="poppler-0.23.4"
ENV PROJ="proj-4.8.0"
ENV GDAL="gdal-2.0.3"
ENV WNSCRIPTS="/packages/wind/depends"

# get code and packages
Run cd /packages/wind \
    && mkdir $WNSCRIPTS \
    && cd $WNSCRIPTS \
    && wget http://poppler.freedesktop.org/$POPPLER.tar.xz \
    && tar -xvf $POPPLER.tar.xz \
    && rm $POPPLER.tar.xz \
    && wget http://download.osgeo.org/proj/$PROJ.tar.gz \
    && tar xvfz $PROJ.tar.gz \
    && rm $PROJ.tar.gz \
    && wget http://download.osgeo.org/gdal/2.0.3/$GDAL.tar.gz \
    && tar -xvf $GDAL.tar.gz \
    && rm $GDAL.tar.gz

# build packages
RUN cd $WNSCRIPTS/$POPPLER \
    && ./configure --prefix=$PREFIX --enable-xpdf-headers \
    && make install -j8 \
    && make clean

RUN cd $WNSCRIPTS/$PROJ \
    &&./configure --prefix=$PREFIX \
    && make clean \
    && make \
    && make install -j 8 \
    && make clean \
    && cp $PREFIX/include/proj_api.h $PREFIX/lib

RUN cd $WNSCRIPTS/$GDAL \
    &&./configure --prefix=$PREFIX --with-poppler=$PREFIX \
    && make -j 8 \
    && make install -j 8 \
    && make clean \
    && ldconfig

# build windninja
Run mkdir /packages/wind/build \
    # && cd /packages/wind/build \
    && cd /packages/wind/windninja \
    && cmake -DNINJA_CLI=ON -DNINJAFOAM=OFF -DNINJA_QTGUI=OFF /packages/wind/windninja \
    && make \
    && make install \
    && ldconfig \
    && export WINDNINJA_DATA=/packages/wind/windninja/data

####################################################
# WGRIB2
####################################################

ENV CC=gcc
ENV FC=gfortran

RUN cd /code/grib2 \
    && make \
    && make lib

# add to path
ENV PATH=/code/grib2/wgrib2:$PATH

####################################################
# katana
####################################################

# copy katana
COPY . / /code/katana/

RUN mkdir /data \
    && cd /code/katana \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install setuptools wheel \
    && python3 -m pip install -r /code/katana/requirements.txt \
    # && cp /code/katana/run_katana /usr/local/bin/
    # && python3 setup.py build_ext --inplace \
    && python3 setup.py install


####################################################
# clean up
####################################################
RUN apt-get clean \
    && apt remove -y wget \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf $WNSCRIPTS


# ENTRYPOINT ["/code/katana/run_katana"]
# ENTRYPOINT ["run_katana"]
# CMD ["/bin/bash"]
COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
RUN echo "umask 0002" >> /etc/bash.bashrc
ENTRYPOINT ["/docker-entrypoint.sh"]
