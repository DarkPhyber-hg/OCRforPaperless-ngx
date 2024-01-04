FROM ghcr.io/paperless-ngx/paperless-ngx:latest
USER root

run apt update
run apt install -y wget
run apt install -y parallel ghostscript mupdf-tools qpdf poppler-utils detox libimage-exiftool-perl imagemagick

  
# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda

run /opt/conda/bin/conda install -c conda-forge poppler

run pip install --upgrade pip
run pip install --upgrade pip
run pip3 install azure-ai-formrecognizer>=3.3 pypdf>=3.0 reportlab pillow pdf2image
