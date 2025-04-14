# PdfTableParse

A tool for extracting and parsing tabular data from PDF documents. This repository provides utilities to:

- Extract tables from PDF files
- Convert PDF tables into structured formats (CSV, JSON, etc.)
- Preserve table formatting and relationships

NB! The table requires a special formatting. 

## depends

opencv-python
numpy
pdfplumber

## Usage
usage: pdfToTable.py [-h] [--pages PAGES] pdf_file

Parse the PDF table to row an cols. Example: python ./pdfToTable.py [table.pdf]

positional arguments:
  pdf_file           Path to the PDF file to process

options:
  -h, --help         show this help message and exit
  --pages, -p PAGES  Pages to process