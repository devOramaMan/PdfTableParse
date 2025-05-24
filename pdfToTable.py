import argparse
import os
import pdfplumber
import re

import cv2
import json

from textwrap import wrap
from DropdownDialog import dropdown_dialog 
from InputDialog import input_dialog
from MessageDialog import message_dialog
import SetRegion



import selectinwindow

TABLE_NO_LINE_SETTINGS = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text"
}

def table_no_line_to_json(page, bbox):
    """
    Convert the parsed table to a JSON format.
    """
    # Extract the table from the page using pdfplumber
    parsed_table = page.within_bbox(bbox).extract_table(TABLE_NO_LINE_SETTINGS)
    json_data = []
    if parsed_table is None:
        print("table no line - No table found in region: %s (p: %d)" % (str(bbox), page))
        return

    for row in parsed_table:
        json_row = {}
        for i, cell in enumerate(row):
            json_row[f"col_{i}"] = cell
        json_data.append(json_row)
    return json_data

CONSECUTIVE_SPACE = 3
def keep_blank_text(page, bbox):
    """
    Convert plain text and keep blank chars 
    Algorithm:
    1 split line feed
    2 remove trailing space
    3 remove front space
    4 remove consecutive space above {CONSECUTIVE_SPACE}
    5 split consecutive space of {CONSECUTIVE_SPACE}
    """
    #col_split = "".join([" "] * CONSECUTIVE_SPACE)
    col_split = " " * CONSECUTIVE_SPACE
    parsed_str = page.within_bbox(bbox).extract_text( keep_blank_chars = True )
    lines = parsed_str.split("\n")
    json_data = []
    for line in lines:
        row = {}
        line = line.rstrip().strip()
        if len(line) == 0:
            continue

        pattern = r'\s{' + str(CONSECUTIVE_SPACE) + ',}'
        line = re.sub(pattern, col_split, line)
        if len(line) == 0:
            continue

        if line.find(col_split) == -1:
            continue

        cols = line.split(col_split)
        for idx, col in zip(range(len(cols)),cols):
            row[idx] = col

        if len(row):
            json_data.append(row)

    return json_data



def table_to_json(page, bbox):
    """
    Convert the parsed table to a JSON format.
    """
    # Extract the table from the page using pdfplumber
    parsed_table = page.within_bbox(bbox).extract_table()
    json_data = []
    if parsed_table is None:
        print("Table - No table found in region: %s (p, %d) " % (str(bbox), page.page_number))
        return

    for row in parsed_table:
        json_row = {}
        for i, cell in enumerate(row):
            json_row[f"col_{i}"] = cell
        json_data.append(json_row)
    return json_data


def plain_text_to_json(page, bbox):
    """
    Convert the parsed Plain text to a JSON format.
    """
    # Extract the text from the page using pdfplumber
    parsed_str = page.within_bbox(bbox).extract_text()
    if parsed_str is None:
        print("No text found")
        return
    json_data = {}
    json_data["Plain text"] = parsed_str
    return json_data
    

PARSE_OPTIONS = {
    "Table": table_to_json,
    "Table no lines": table_no_line_to_json,
    "Plain text": plain_text_to_json,
    "Keep blank text": keep_blank_text
}


OPTIONS = list(PARSE_OPTIONS.keys())

DEFAULT_BOUNDING_BOX = \
{
    "regions": [ ]
}

def load_bounding_boxes(pdfFileName, page ):
    json_file = ".tmp/regions_%s_%d.json" % (pdfFileName, page)
    data = DEFAULT_BOUNDING_BOX
    if os.path.exists(json_file) is False:
        return data["regions"]
    err = None
    with open(json_file, "r") as file:
        try:
            # Load the JSON data from the file
            data = json.load(file)
        except json.JSONDecodeError as ex:
            print(f"Error decoding JSON from file: {json_file} {ex}")
            err = ex

                
    #Delete the file if it is not valid JSON
    if err is not None:
        if os.path.exists(json_file):
            print(f"Deleting invalid JSON file: {json_file}")
            os.remove(json_file)
            
        # Extract the "boundaries" from each region
        #bounding_boxes = [tuple(region["boundaries"]) for region in data["regions"]]
        
    return data["regions"]


helpstr="""
Parse the PDF table to row an cols.
Example: python ./pdfToTable.py [table.pdf]
"""


def parse_range(arg):
    result = []
    for part in arg.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.extend(range(start-1, end ))
        else:
            result.append(int(part)-1)
    return result

PDF_PLUMB = None
PDF_FILENAME = None
def load_image(page,filename=None, pdf=None):
    """ 
    Load the image from the PDF page and save it as a PNG file.
    """
    if page < 0:
        print("Page number must be greater than 0")
        return None
    global PDF_PLUMB
    global PDF_FILENAME
    if pdf is None:
        pdf = PDF_PLUMB
    else:
        PDF_PLUMB = pdf

    if filename is None:
        filename = PDF_FILENAME
    else:
        PDF_FILENAME = filename

    if pdf is None or filename is None:
        print("PDF file or filename is not set")
        return None
    
    name = str( ".tmp/%s_%d.png" % (filename, page) )
    if os.path.exists(name) == False:
        page_pdf = pdf.pages[page]
        # Visualize the page layout
        #box = bbox['boundaries']
        im = page_pdf.to_image()#resolution=300)
        #im.draw_rect(box)  # Draw the bounding box
        im.save('%s' % (name))
    return name

#main
if __name__ == "__main__":
    import sys

    # Parse command line arguments
    #print(sys.argv)
    parser = argparse.ArgumentParser(description=helpstr)
    parser.add_argument("pdf_file", help="Path to the PDF file to process")
    parser.add_argument("--pages", "-p", help="Pages to process", required=False, type=parse_range, default=None)
    parser.add_argument("--last", "-l", action='store_true', help="Use last regions (no usr input)", required=False)
    args = parser.parse_args()

    #get the filename without extension
    pdfFileName = os.path.splitext(os.path.basename(args.pdf_file))[0]

    BOUNDING_BOXES = []

    #if tmp folder doesn't exist then make it
    if os.path.exists(".tmp") == False:
        os.mkdir(".tmp")

    image_files = []

    pages = args.pages

    if pages is None:
        # Get last page number used
        last_pages = "1-3"
        last = False
        if os.path.exists(".tmp/last_page"):
            with open(".tmp/last_page", "r") as file:
                last_pages = file.read()
                last = True
        if args.last is False or last is False:
            pages = input_dialog("Select pages", "Enter the pages to process (e.g., 1,2,3 or 1-3):", last_pages)
        else:
            pages = last_pages

        if pages is None:
            print("No pages selected. Exiting.")
            exit(0)

        with open(".tmp/last_page", "w") as file:
            file.write(pages)

        pages = parse_range(pages)

    with pdfplumber.open(args.pdf_file) as pdf:
        for page in pages:
            name = load_image(page, pdfFileName, pdf )
            # Extract text from the bounding box
            image_files.append(name)

        update_pages = []    

        if args.last is False:
            #Select bounderies for each page
            for f_image, page  in zip(image_files, pages):
                # Load the image saved from pdfplumber
                pagenum = page
                print(f"Processing image {f_image}")
                image = cv2.imread(f_image)
                
                load_regions = False

                #while add_region is True:
                wName = 'Draw a region and add the boundaries of table'
                #get the width and height of the image
                imageHeight, imageWidth = image.shape[:2]
                rectI = SetRegion.DragRectangle(image, wName, imageWidth, imageHeight,pageNum=pagenum, options=OPTIONS)
                cv2.namedWindow(rectI.wname)
                cv2.setMouseCallback(rectI.wname, SetRegion.dragrect, rectI)
                rectI.setRenderPtr(load_image)

                # keep looping until rectangle finalized
                regions = {}
                if SetRegion.run(rectI) is True:
                    regions = rectI.regions
                    
                if len(regions) == 0:
                    print("No regions added")
                    continue

                for lpage in regions:
                    json_file = ".tmp/regions_%s_%d.json" % (pdfFileName, lpage)
                    with open(json_file, "w", encoding='utf-8') as file:
                        update_pages.append(lpage)
                        data = {"regions": regions[lpage]}
                        json.dump(data, file, indent=4, ensure_ascii=False)
        else:
            update_pages = [ i-1 if i > 0 else 0 for i in pages ]
            print("Using last regions for pages %s" % (" ".join(map(str, update_pages))) )


        out_str = {}
        update_pages.sort()
        for pagenum in update_pages:
            
            regions = load_bounding_boxes(pdfFileName, pagenum)
            page = pdf.pages[pagenum]
            cnt = 0
            for region in regions:
                #print(f"Extracted text from bbox {name} {box}:\n{text}")
                ptype = region.get('type', "Plain text")

                out_str["%s_%s" % (pagenum,cnt)] = PARSE_OPTIONS[ptype](page, region['boundaries'] )
                cnt += 1

        # Save the extracted data to a JSON file
        if len(out_str):
            json_file = "extracted_data.json"
            with open(json_file, "w", encoding='utf-8') as file:
                json.dump(out_str, file, indent=4, ensure_ascii=False)
                # Print the extracted data
                print("Extracted data written to %s" % json_file)
                















# Retrieve Faktura Name and address


