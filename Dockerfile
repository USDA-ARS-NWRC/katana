# Katana is built on a ubuntu 18.04 image
FROM usdaarsnwrc/katana_deps:latest

MAINTAINER Micah Sandusky <micah.sandusky@ars.usda.gov>

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


# ENTRYPOINT ["/code/katana/run_katana"]
# ENTRYPOINT ["run_katana"]
# CMD ["/bin/bash"]
COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
RUN echo "umask 0002" >> /etc/bash.bashrc
ENTRYPOINT ["/docker-entrypoint.sh"]
