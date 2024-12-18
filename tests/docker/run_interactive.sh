docker run -it --privileged \
    -v /dev:/dev \
    -v $HOME/tutorials/:/home/cwtests/chipwhisperer/tutorials \
    -p 8888:8888 \
    cw-testing-server:latest \
    su cwtests -c "jupyter notebook --port=8888 --ip 0.0.0.0 --no-browser"

