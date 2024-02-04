#!/usr/bin/env bash
#init script to load required libraries for azure OCR into paperless at startup
apt update
apt install -y wget
apt install -y parallel ghostscript mupdf-tools qpdf poppler-utils detox libimage-exiftool-perl imagemagick 
# Install miniconda
export CONDA_DIR=/opt/conda
wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda
/opt/conda/bin/conda install -y -c conda-forge poppler
pip install --upgrade pip
pip install --upgrade pip
pip3 install azure-ai-formrecognizer>=3.3 pypdf>=3.0 reportlab pillow pdf2image
