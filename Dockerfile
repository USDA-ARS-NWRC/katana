# Katana is built on a ubuntu 18.04 image with
# Python3, proj, gdal, wgrib2 and WindNinja
FROM usdaarsnwrc/katana_base:latest

LABEL maintainer="Scott Havens <scott.havens@usda.gov>"

####################################################
# katana
####################################################

# copy katana
COPY . / /code/katana/

RUN mkdir /data \
    && cd /code/katana \
    && python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir setuptools wheel \
    && python3 -m pip install --no-cache-dir -r /code/katana/requirements.txt \
    # && cp /code/katana/run_katana /usr/local/bin/
    # && python3 setup.py build_ext --inplace \
    && python3 setup.py install

COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
RUN echo "umask 0002" >> /etc/bash.bashrc
ENTRYPOINT ["/docker-entrypoint.sh"]
