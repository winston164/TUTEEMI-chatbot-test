FROM python:slim-buster

# project source codes
COPY ./ ./

# system graphviz
RUN apt-get update
RUN apt-get install -y python3-dev
# RUN ls /usr/local/include/ | grep graphviz

# RUN pip install --install-option="--include-path=/usr/local/include/" --install-option="--library-path=/usr/local/lib/" pygraphviz
RUN pip install -U pip
RUN pip install -r requirements.txt

WORKDIR /

ENTRYPOINT ["python", "app.py"]
