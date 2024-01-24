FROM pandoc/core:2.19.2

WORKDIR /src
COPY requirements.txt /src
COPY mwimporter.py /src
COPY python-mwtypes /src/python-mwtypes
COPY python-mwxml /src/python-mwxml

RUN apk --no-cache add python3 py3-pip && \
    pip install -r requirements.txt

RUN cd python-mwtypes && python3 setup.py install && \
    cd ../python-mwxml && python3 setup.py install 

ENTRYPOINT /usr/bin/python3 mwimporter.py
