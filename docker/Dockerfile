FROM node:16.3-slim

RUN apt-get update && apt-get install -y \
        build-essential curl libglu1 libxi6 libgconf-2-4 wget

RUN npm install -g firebase-tools


RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh -O ~/miniconda.sh \
    && bash ~/miniconda.sh -b -p /opt/anaconda \
    && rm ~/miniconda.sh

ENV PATH="/opt/anaconda/bin:$PATH" 

RUN conda install -c conda-forge mamba \
    && mamba install -c conda-forge \
        dvc dvc-s3 dvc-azure dvc-gdrive dvc-gs dvc-oss dvc-ssh

RUN pip install --upgrade pip
ADD requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt
