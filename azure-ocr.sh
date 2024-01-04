#!/bin/bash


bash /usr/src/paperless/scripts/is_ocrd_pdf.sh "${DOCUMENT_WORKING_PATH}"

retc=$?

if [[ $retc -eq 0 ]];
then
	echo "${DOCUMENT_WORKING_PATH} is a scanned document, sending to azure for ocr"
	python3 /usr/src/paperless/scripts/fr_generate_searchable_pdf.py "${DOCUMENT_WORKING_PATH}" -o "${DOCUMENT_WORKING_PATH}"
else
	echo "${DOCUMENT_WORKING_PATH} is likely computer generated, checking character count"
	pdfcc=$(/usr/local/bin/pdf2txt.py  "${DOCUMENT_WORKING_PATH}" |wc -m)
	if [[ $pdfcc -ge 100 ]]
	then
		echo "${DOCUMENT_WORKING_PATH} has more than 100 characters of text, no need to send for ocr"
	else
		echo "${DOCUMENT_WORKING_PATH} has less than 100 characters of text, sending to azure"
		python3 /usr/src/paperless/scripts/fr_generate_searchable_pdf.py "${DOCUMENT_WORKING_PATH}" -o "${DOCUMENT_WORKING_PATH}"
	fi
fi


