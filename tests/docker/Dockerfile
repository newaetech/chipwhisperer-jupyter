FROM ubuntu:18.04

ENV CW_USER="cwtests"

# for timezone installation
RUN ln -fs /usr/share/zoneinfo/America/Halifax /etc/localtime

# install apt-get packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends \
    cron \
    gcc=4:7.4.0-1ubuntu2.3 \
    gcc-avr \
    avr-libc \
    gcc-arm-none-eabi \
    git \
    libnewlib-arm-none-eabi \
    libusb-dev \
    make \
    curl \
    pandoc \
    tzdata \
    ca-certificates \
    openssl \
    usbutils \
    make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/list/* /tmp/* /var/tmp/*

    # python3-dev \
    # python3-pip \
# set timezone
RUN echo "America/Halifax" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# Add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# install the correct version of GNU ARM toolchain
# RUN wget https://mirrors.kernel.org/ubuntu/pool/universe/n/newlib/libnewlib-dev_3.0.0.20180802-2_all.deb && \
#     wget https://mirrors.kernel.org/ubuntu/pool/universe/n/newlib/libnewlib-arm-none-eabi_3.0.0.20180802-2_all.deb && \
#     dpkg -i libnewlib-arm-none-eabi_3.0.0.20180802-2_all.deb libnewlib-dev_3.0.0.20180802-2_all.deb
# make a non-root user
RUN useradd --create-home --shell /bin/bash $CW_USER && \
    chown -R $CW_USER /home/$CW_USER

RUN echo $HOME

# add local --user install directory to path
# RUN update-ca-certificates
RUN curl https://pyenv.run | bash
RUN cp -r $HOME/.pyenv /home/$CW_USER/
RUN echo PATH=/home/$CW_USER/.pyenv/bin:/home/$CW_USER/.pyenv/shims:$PATH:/home/$CW_USER/.local/bin/ >> /etc/environment
ENV PATH=/home/$CW_USER/.pyenv/bin:/home/$CW_USER/.pyenv/shims:${PATH}:/home/$CW_USER/.local/bin
RUN ls /home/$CW_USER/.pyenv -a
RUN echo $PATH
# run echo 'eval "$(pyenv init -)" >> $HOME/.bashrc'
# run echo 'eval "$(pyenv virtualenv-init -)" >> $HOME/.bashrc'
# RUN eval "$(pyenv init -)"
# RUN eval "$(pyenv virtualenv-init -)"
ENV PYENV_ROOT /home/$CW_USER/.pyenv
# ENV PYENV_ROOT /home/$CW_USER/.pyenv
RUN pyenv install 3.9.5
RUN pyenv global 3.9.5
RUN pyenv rehash
RUN mkdir -p /home/$CW_USER/results
RUN cd /home/$CW_USER && curl -L https://github.com/xpack-dev-tools/openocd-xpack/releases/download/v0.11.0-3/xpack-openocd-0.11.0-3-linux-x64.tar.gz --output openocd.tar.gz && tar -xzf openocd.tar.gz
# RUN pyenv activate cw

# upgrade pip and install setuptools
RUN python -m pip install --upgrade pip && \
    python -m pip install setuptools && \
    python -m pip install wheel

# install virtualenvwrapper for testing dependencies
RUN python -m pip install virtualenv

# Add sendgrid library for python for sending e-mail results
RUN python -m pip install sendgrid

ARG CACHEBUST=1

USER $CW_USER
# install chipwhisperer
RUN cd /home/$CW_USER && \
    git clone https://github.com/newaetech/chipwhisperer.git && \
    cd chipwhisperer && \
    git submodule update --init jupyter && \
    python -m pip install -e . --user --no-warn-script-location && \
    python -m pip install --user -r jupyter/requirements.txt --no-warn-script-location && \
    python -m pip install pyyaml

RUN cd /home/$CW_USER && \
	git clone https://github.com/Ledger-Donjon/lascar.git && \
	cd lascar && \
	python -m pip install -e . --user --no-warn-script-location

# RUN mkdir -p /home/$CW_USER/.virtualenvs && \
#     virtualenv --python=/home/$CW_USER/.pyenv/shims/python /home/$CW_USER/.virtualenvs/tests

USER root

# # add user to plugdev group used by host
# RUN usermod -aG plugdev $CW_USER && \
#     usermod -aG plugdev root

# add to python scripts for testing server
COPY testing_server.py /home/$CW_USER/testing_server.py
COPY mail.py /home/$CW_USER/mail.py
COPY mail/* /home/$CW_USER/mail/
RUN chown $CW_USER:$CW_USER /home/$CW_USER/testing_server.py && \
    chown $CW_USER:$CW_USER /home/$CW_USER/mail.py && \
    chown $CW_USER:$CW_USER /home/$CW_USER/mail/*

# add test configuration file
COPY tests.yaml /home/$CW_USER/tests.yaml
COPY long_tests.yaml /home/$CW_USER/long_tests.yaml
RUN chown $CW_USER:$CW_USER /home/$CW_USER

# script that starts the container
COPY start-container.sh /home/$CW_USER/run.sh
COPY usbreset /home/$CW_USER/chipwhisperer/jupyter/tests/docker
RUN chmod +x /home/$CW_USER/run.sh

CMD ["/home/cwtests/run.sh"]

