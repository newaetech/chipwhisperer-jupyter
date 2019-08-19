FROM ubuntu:18.04

ENV CW_USER="cwtests"

# for timezone installation
RUN ln -fs /usr/share/zoneinfo/America/Halifax /etc/localtime

# install apt-get packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends \
    avr-libc=1:2.0.0+Atmel3.6.0-1 \
    cron \
    gcc=4:7.4.0-1ubuntu2.3 \
    gcc-avr=1:5.4.0+Atmel3.6.0-1build1 \
    gcc-arm-none-eabi=15:6.3.1+svn253039-1build1 \
    git \
    libusb-dev \
    make \
    pandoc \
    python3-dev \
    python3-pip \
    tzdata \
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/list/* /tmp/* /var/tmp/*

# set timezone
RUN echo "America/Halifax" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# Add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# install the correct version of GNU ARM toolchain
RUN wget https://mirrors.kernel.org/ubuntu/pool/universe/n/newlib/libnewlib-dev_3.0.0.20180802-2_all.deb && \
    wget https://mirrors.kernel.org/ubuntu/pool/universe/n/newlib/libnewlib-arm-none-eabi_3.0.0.20180802-2_all.deb && \
    dpkg -i libnewlib-arm-none-eabi_3.0.0.20180802-2_all.deb libnewlib-dev_3.0.0.20180802-2_all.deb

# add local --user install directory to path
RUN echo PATH=$PATH:/home/$CW_USER/.local/bin/ >> /etc/environment

# upgrade pip and install setuptools
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install setuptools

# install virtualenvwrapper for testing dependencies
RUN python3 -m pip install virtualenv

# Add sendgrid library for python for sending e-mail results
RUN python3 -m pip install sendgrid

# make a non-root user
RUN useradd --create-home --shell /bin/bash $CW_USER && \
    chown -R $CW_USER /home/$CW_USER

USER $CW_USER
# install chipwhisperer
RUN cd /home/$CW_USER && \
    git clone https://github.com/newaetech/chipwhisperer.git && \
    cd chipwhisperer && \
    git submodule update --init jupyter && \
    python3 -m pip install -e . --user --no-warn-script-location && \
    python3 -m pip install --user -r jupyter/requirements.txt --no-warn-script-location

RUN mkdir -p /home/$CW_USER/.virtualenvs && \
    virtualenv --python=/usr/bin/python3 /home/$CW_USER/.virtualenvs/tests

USER root

# add user to plugdev group used by host
RUN usermod -aG plugdev $CW_USER && \
    usermod -aG plugdev root

# add to python scripts for testing server
COPY testing_server.py /home/$CW_USER/testing_server.py
COPY mail.py /home/$CW_USER/mail.py
RUN chown $CW_USER:$CW_USER /home/$CW_USER/testing_server.py && \
    chown $CW_USER:$CW_USER /home/$CW_USER/mail.py

# add test configuration file
COPY tests.yaml /home/$CW_USER/tests.yaml
RUN chown $CW_USER:$CW_USER /home/$CW_USER

# script that starts the container
COPY start-container.sh /home/$CW_USER/run.sh
RUN chmod +x /home/$CW_USER/run.sh

CMD ["/home/cwtests/run.sh"]

