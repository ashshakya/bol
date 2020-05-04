# Command for building the container sending the build arguments.
# docker-compose build --build-arg ssh_prv_key="$(cat ~/.ssh/id_rsa)" --build-arg ssh_pub_key="$(cat ~/.ssh/id_rsa.pub)"

FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

# Receive the current user's ssh keys as command line arguments while 
# building the container.
ARG ssh_prv_key
ARG ssh_pub_key

# RUN apt-get update && apt-get install -y git
RUN apk update && apk add --no-cache curl-dev \
                                     gcc \
                                     git \
                                     libffi-dev \
                                     musl-dev \
                                     openssh \
                                     postgresql-dev \
                                     vim \
                                     redis \
                                     #Pillow dependencies
                                     freetype-dev \
                                     jpeg-dev \
                                     lcms2-dev \
                                     openjpeg-dev \
                                     tcl-dev \
                                     tiff-dev \
                                     tk-dev \
                                     zlib-dev

# We have to add `phab.renewbuy.com` hosts entry before running each 
# command because adding it once doesn't carry it forward to the images 
# that are built after this one.

RUN mkdir /code /var/log/boloo
RUN mkdir /code/static

WORKDIR /code

ADD requirements /code/requirements

RUN echo "Installing Requirements"; \
    # Install python project requirements.
    pip install -r /code/requirements/pip.txt -U

# Copy all the code.
COPY . /code/
