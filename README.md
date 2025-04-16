# PdfTableParse

A tool for extracting and parsing tabular data from PDF documents. This repository provides utilities to:

- Extract data from PDF files from a selected region.
- Convert PDF tables and text into structured formats (JSON, etc.)


## depends
Python (used 3.13.3 for windows)
opencv-python
numpy
pdfplumber


## Usage
usage: pdfToTable.py [-h] [--pages PAGES] [--last] pdf_file

Parse the PDF table to row an cols. Example: python ./pdfToTable.py [table.pdf]

positional arguments:
  pdf_file           Path to the PDF file to process

options:
  -h, --help         show this help message and exit
  --pages, -p PAGES  Pages to process
  --last, -l         Use last regions (no usr input)


## User interactions steps

1 Add pages.
2 Add or use the last marked region (region: graphical overlay box).
3 Select the appropriate parsing method for the marked region.

Output to extracted_data.json.

## Parsing Methods

- Table (with lines): Uses the default pdfplumber settings.
- Table (no lines): Uses vertical and horizontal settings to extract text.
- Plain text: Extracts all text.
- Keep blank text: Used for tables without lines (keep_blank_char), parses the text into rows and columns.

see Table-extraction settings in [pdfplumber](https://github.com/jsvine/pdfplumber)
Inspiration used: [jsvine](https://github.com/jsvine/pdfplumber/blob/stable/examples/notebooks/san-jose-pd-firearm-report.ipynb)

