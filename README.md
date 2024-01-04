# OCRforPaperless-ngx
pre_consume_script for paperless-ngx to turn pdf's into searchable documents using azure document ai. 

the free version of azure only supports documents up to 2 pages, if you do more than 2 pages you will get an error that the document is too large.

in paperless set
PAPERLESS_PRE_CONSUME_SCRIPT=/usr/src/paperless/scripts/azure-ocr.sh

edit the fr_generate_searchable_pdf.py file with your azure key and endpoint.

fr_generate_searchable_pdf.py is from here:
https://techcommunity.microsoft.com/t5/ai-azure-ai-services-blog/generate-searchable-pdfs-with-azure-form-recognizer/bc-p/3930832

is_ocrd_pdf.sh is from here:
https://github.com/jfilter/pdf-scripts
