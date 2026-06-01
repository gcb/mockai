export SHELL = /usr/bin/env bash -xe

# DO NOT update the variables here!
#
# they only document the default. Add your
# choices in Makefile.local
#
# setting: user that will run code inside container
export USER=mockai
# setting: dir that will show up inside container (rw)
export PATH_CODE:=$(shell pwd -P)/code
export PORT=8080

export TZ="Etc/UTC"
export LOG_LEVEL=silly

# highlight output from make being verbose vs other commands it calls
export PS4=\[\e[93m\]+MAKE+ \[\e[m\]
-include Makefile.local
default: all
all: run

build: Dockerfile $(wildcard user-home)
	doas docker build --build-arg USER=${USER}  -t mockai .

# NOTE: we will name the container 'mockai01', so you can only have one using this file
run:
	doas docker run --rm -it -v "${PATH_CODE}:/home/${USER}/code" --env MOCKAI_PORT=${PORT} -p 127.0.0.1:${PORT}:${PORT} --name mockai01  mockai

# join a running container as root
.PHONY: root
root:
	doas docker exec -it -u root mockai01 /bin/bash

