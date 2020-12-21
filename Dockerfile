FROM python:3.7.8-buster

# project source codes
COPY ./ ./

# system graphviz
RUN apt-get update
RUN apt-get install -y graphviz-dev python3-dev graphviz libgraphviz-dev pkg-config
# RUN ls /usr/local/include/ | grep graphviz

# RUN pip install --install-option="--include-path=/usr/local/include/" --install-option="--library-path=/usr/local/lib/" pygraphviz
RUN pip install -U pip
RUN pip install -r requirements.txt

WORKDIR /

ENTRYPOINT ["python app.py"]
