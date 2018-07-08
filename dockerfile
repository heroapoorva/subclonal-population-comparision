# Using ubuntu machine.
FROM ubuntu:latest

# Install environment dependencies.
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y r-base
RUN apt-get install -y wget
RUN apt-get install -y git
RUN apt-get install -y python-tk
RUN wget https://download1.rstudio.org/rstudio-xenial-1.1.383-amd64.deb
RUN apt install -y ./rstudio-xenial-1.1.383-amd64.deb

RUN apt-get install -y openssl libssl-dev libssh2-1-dev libcurl4-openssl-dev
RUN touch ~/.Rprofile
RUN echo "options(repos=structure(c(CRAN=\"http://cran.uk.r-project.org\")))" > ~/.Rprofile
RUN Rscript -e 'install.packages("devtools", dependencies = TRUE)'
RUN Rscript -e 'devtools::install_github("keyuan/ccube")'
RUN Rscript -e 'install.packages("foreach", dependencies = TRUE)'

RUN mkdir pypy
WORKDIR pypy

RUN wget https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-5.9-linux_x86_64-portable.tar.bz2 && \
    tar xvf pypy-5.9-linux_x86_64-portable.tar.bz2 && \
    pypy-5.9-linux_x86_64-portable/bin/pypy -m ensurepip && \
    pypy-5.9-linux_x86_64-portable/bin/pip2.7 install -U pip wheel && \
    pypy-5.9-linux_x86_64-portable/bin/pip2.7 install scipy && \
    pypy-5.9-linux_x86_64-portable/bin/pip2.7 install PyYAML pandas && \
    mv pypy-5.9-linux_x86_64-portable /opt && \
    ln -s /opt/pypy-5.9-linux_x86_64-portable/bin/pypy /usr/bin/pypy && \
    rm pypy-5.9-linux_x86_64-portable.tar.bz2

RUN wget https://bitbucket.org/aroth85/pydp/downloads/PyDP-0.2.2.tar.gz && \
    tar xvf PyDP-0.2.2.tar.gz && \
    cd PyDP-0.2.2 && \
    pypy setup.py install  && \
    cd ../  && \
    rm -rf PyDP-0.2.2  && \
    rm PyDP-0.2.2.tar.gz

RUN wget https://bitbucket.org/aroth85/pyclone/downloads/PyClone-0.13.0.tar.gz && \
    tar xvf PyClone-0.13.0.tar.gz

RUN wget https://gist.githubusercontent.com/markoglasgow/3ebdb8524eb9dfcf41635924a916a0b8/raw/fd5ce4df349919c7478f7d45c43a35535f7b16ec/pyclone_pypy_patch.diff  && \
    patch -p0 -i pyclone_pypy_patch.diff

WORKDIR PyClone-0.13.0

RUN pypy setup.py install && \
    chmod a+x PyClone  && \
    cd ../  && \
    mv PyClone-0.13.0 /opt && \
    ln -s /opt/PyClone-0.13.0/PyClone /usr/bin/PyClone && \
    cd ../  && \
    rm -rf pypy

ENV PATH="${PATH}:/opt/PyClone-0.13.0/PyClone"
RUN PyClone --version

RUN pip install --user ete2
RUN apt-get install -y libgsl2 libgsl-dev

WORKDIR ../
RUN git clone https://github.com/markoglasgow/phylowgs.git && \
    cd ./phylowgs && \
    chmod a+x evolve.py && \
    chmod a+x write_results.py && \
    chmod a+x parser/parse_cnvs.py && \
    chmod a+x parser/create_phylowgs_inputs.py

WORKDIR phylowgs/
RUN g++ -o mh.o -O3 mh.cpp  util.cpp `gsl-config --cflags --libs` && \
    ln -s /opt/phylowgs/evolve.py /usr/bin/PhyloWGS && \
    ln -s /opt/phylowgs/write_results.py /usr/bin/PhyloWGS_write_results && \
    ln -s /opt/phylowgs/parser/parse_cnvs.py /usr/bin/PhyloWGS_parse_cnvs && \
    ln -s /opt/phylowgs/parser/create_phylowgs_inputs.py /usr/bin/PhyloWGS_create_inputs

WORKDIR ../
RUN mv phylowgs /opt/phylowgs
ENV PHYLOWGS_PATH="/opt/phylowgs"

# Create working directory with pipeline code.
COPY . /app
WORKDIR /app

# Install pipeline python dependecies.
RUN pip install -r requirements.txt