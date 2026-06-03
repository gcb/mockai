FROM debian:stable-slim
ARG USER
# some commands ignore args! so we also set ENV so it "bleeds" to the commands that ignore it.
# also, debian doesn't seem to set USER env on docker shells... so i guess this is needed anyway?
# will be weird if logging in as other users. sigh. maybe use another name and let USER unset.
ENV USER=${USER}
ARG PATH_CODE # will use these only when starting the container
ARG PATH_CONF

RUN apt-get update
RUN apt dist-upgrade -y
# need gpg to install ppa key, curl to fetch keys/yolo-scripts. vim and sensible-utils are just common decency
RUN apt install -y gpg dialog vim sensible-utils curl

RUN apt-get install -y python3-pip python3-venv

# Set working directory
WORKDIR /workspace

# set up user and it's home
RUN useradd ${USER}
RUN mkdir /home/${USER}
COPY user-home/ /home/${USER}/
RUN chown -R ${USER} /home/${USER}

# force a single venv for this container
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN chown -R ${USER} /opt/venv

# Install the application
# - won't work because /code is only available after we mount it with docker run -v ...
#USER ${USER}
##RUN cd /home/${USER}/code; ls -lah; python3 -m pip install -r requirements.txt;
#USER root

# clean up
RUN rm -rf /var/lib/apt/lists/*

# entry as user
USER ${USER}
# --- debug start:
#WORKDIR /home/${USER}
#CMD ["bash", "--login"]
# --- automated start:
WORKDIR /home/${USER}/code/
# NOTE: these commands depend on the volume mounted at run time! so they
#       CANNOT run before docker run. hence they are concatenated on CMD.
#RUN ["python", "-m", "pip", "install", "-r", "requirements.txt"]
#CMD ["python", "mockai.py"]
CMD ["bash", "-c", "python -m pip install -r requirements.txt && python mockai.py"]
