FROM phusion/baseimage:latest

ENV USER="tester"

# Use baseimage-dockser's system.
CMD ["sbin/my_init"]

# install apt-get packages
RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		avr-libc \
		gcc-avr \
		gcc-arm-none-eabi \
		git \
		python3-pip \
		wget && \
	apt-get clean && \
	rm -rf /var/lib/apt/list/* /tmp/* /var/tmp/*

# install the correct version of GNU ARM toolchain
RUN wget https://mirrors.kernel.org/ubuntu/pool/universe/n/newlib/libnewlib-dev_3.0.0.20180802-2_all.deb && \
	wget https://mirrors.kernel.org/ubuntu/pool/universe/n/newlib/libnewlib-arm-none-eabi_3.0.0.20180802-2_all.deb && \
	dpkg -i libnewlib-arm-none-eabi_3.0.0.20180802-2_all.deb libnewlib-dev_3.0.0.20180802-2_all.deb

# upgrade pip and install setuptools
RUN python3 -m pip install --upgrade pip && \
	python3 -m pip install setuptools

# make a non-root user
RUN useradd --create-home --shell /bin/bash $USER && \
	chown -R $USER /home/$USER

USER $USER
# install chipwhisperer
RUN	cd /home/$USER && \
	git clone https://github.com/newaetech/chipwhisperer.git && \
	cd chipwhisperer && \
	git submodule update --init jupyter && \
	python3 setup.py develop --user && \
	python3 -m pip install --user -r jupyter/requirements.txt


