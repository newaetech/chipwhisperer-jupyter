FROM ubuntu:18.04

ENV CW_USER="cwtests"

# install apt-get packages
RUN apt-get update && \
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
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/list/* /tmp/* /var/tmp/*

# install the mail server
RUN echo "postfix postfix/mailname string cw-testing-server.com" | debconf-set-selections && \
    echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections && \
    apt-get install -y mailutils 

# install the correct version of GNU ARM toolchain
RUN wget https://mirrors.kernel.org/ubuntu/pool/universe/n/newlib/libnewlib-dev_3.0.0.20180802-2_all.deb && \
    wget https://mirrors.kernel.org/ubuntu/pool/universe/n/newlib/libnewlib-arm-none-eabi_3.0.0.20180802-2_all.deb && \
    dpkg -i libnewlib-arm-none-eabi_3.0.0.20180802-2_all.deb libnewlib-dev_3.0.0.20180802-2_all.deb

# add local --user install directory to path
RUN echo PATH=$PATH:/home/$CW_USER/.local/bin/ >> /etc/environment

# upgrade pip and install setuptools
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install setuptools

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

USER root

# add user to plugdev group used by host
RUN usermod -aG plugdev $CW_USER && \
    usermod -aG plugdev root

COPY jupyter-tests-cron /etc/cron.d/jupyter-tests-cron
COPY cw-run-jupyter-tests.sh /home/$CW_USER/cw-run-jupyter-tests.sh
COPY tests.yaml /home/$CW_USER/tests.yaml

# script that starts the container
COPY start-container.sh /home/$CW_USER/run.sh
RUN chmod +x /home/$CW_USER/run.sh

# allow $CW_USER to use mail
RUN MAIL_DIR=/var/mail/$CW_USER && \
    touch $MAIL_DIR && \
    chown $CW_USER:mail $MAIL_DIR && \
    chmod o-r $MAIL_DIR && \
    chmod g+rw $MAIL_DIR

# configure the postfix server
COPY postfix.config /etc/postfix/main.cfg

# make the cw-run-jupyter-tests.sh file executable and change the owner
RUN chmod +x /home/$CW_USER/cw-run-jupyter-tests.sh && \
    chown $CW_USER /home/$CW_USER/cw-run-jupyter-tests.sh /home/$CW_USER/tests.yaml

# set the permissions for the cronjob
RUN chmod 0644 /etc/cron.d/jupyter-tests-cron && \
    crontab /etc/cron.d/jupyter-tests-cron

CMD ["/home/cwtests/run.sh"]




