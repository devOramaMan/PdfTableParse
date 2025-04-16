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



import selectinwindow

TABLE_NO_LINE_SETTINGS = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text"
}
#intersection_x_tolerance
#"join_x_tolerance": 15
#snap_x_tolerance
ENUMS = ['A', 'B', 'C']

def camelcase(cols, **kwargs):
    """
    input: "STRING IS FINE"
    output: "StringIsFine"
    """
    pass

def index(cols, **kwargs):
    """
    input: "1.3.4 234"
    output: "1.3.4"
    """

def integer(cols, **kwargs):
    """
    input: "1233 43342"
    output: "1233"
    """
    pass

def enums(cols, **kwargs):
    """
    input: B dfd
    output: B
    (if B is in inputed enum list)
    """
    pass

def identifier(cols, **kwargs):
    """
    input: G2.1 23
    output: G2.1
    """

def plain_text(cols, **kwargs):
    """
    input: "hello fdkj"
    output: "hello fdkj"
    """
    pass

TABLE_2 = []
TABLE_1 = [
    {
        "name":"index",
        "type": index
    },
    {
        "name":"num1",
        "type":integer
    },
    {
        "name":"num2",
        "type":integer
    },
    {
        "name":"property",
        "type":camelcase
    },
    {
        "name": "enum",
        "type": enums,
        "valid": ENUMS
    },
    {
        "name": "category",
        "type": identifier
    },
    {
        "name": "value",
        "type": integer
    },
    {
        "name": "description",
        "type": plain_text
    }
]

def table_1_to_json(page, bbox):
    """
    Convert table
    """

    data = table_no_line_to_json(page, bbox)



def table_no_line_to_json(page, bbox):
    """
    Convert the parsed table to a JSON format.
    """
    # Extract the table from the page using pdfplumber
    parsed_table = page.within_bbox(bbox).extract_table(TABLE_NO_LINE_SETTINGS)
    json_data = []
    if parsed_table is None:
        print("No table found")
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
        print("No table found")
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
    

OPTIONS = ["Table", "Table no lines", "Plain text"]

PARSE_OPTIONS = {
    "Table": table_to_json,
    "Table no lines": table_no_line_to_json,
    "Plain text": plain_text_to_json,
    "Keep blank text": keep_blank_text
}




DEFAULT_BOUNDING_BOX = \
{
    "regions": [ ]
}

def load_bounding_boxes(page):
    json_file = ".tmp/regions_%d.json" % page
    data = DEFAULT_BOUNDING_BOX
    if os.path.exists(json_file) is False:
        return data["regions"]
    
    with open(json_file, "r") as file:
        data = json.load(file)
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
            result.extend(range(start, end + 1))
        else:
            result.append(int(part))
    return result

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

    BOUNDING_BOXES = []#load_bounding_boxes()

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
            name = str(".tmp/page_image_%d.png" % page)
            if os.path.exists(name) == False:
                page_pdf = pdf.pages[page]
                # Visualize the page layout
                #box = bbox['boundaries']
                im = page_pdf.to_image()
                #im.draw_rect(box)  # Draw the bounding box
                im.save('%s' % (name))

                # Extract text from the bounding box
                #text = page.within_bbox(box).extract_text()
                #print(f"Extracted text from bbox {name} {box}:\n{text}")
            image_files.append(name)

        update_cnt = 0    

        #Select bounderies for each page
        if args.last is False or last is False:
            for f_image, page  in zip(image_files, pages):
                # Load the image saved from pdfplumber
                print(f"Processing image {f_image}")
                image = cv2.imread(f_image)
                
                # Load the bounding boxes from the JSON file
                regions = load_bounding_boxes(page)
                load_regions = False
                if len(regions):
                    load_regions = message_dialog("Last regions", "Do you want to use the last regions?", "Yes", "No")
                    if load_regions is True:
                        print("Loading regions")          
                        for region in regions:
                            wName = '%s (double click the rectangle to update the boundaries)' % f_image

                            #get the width and height of the image
                            imageHeight, imageWidth = image.shape[:2]

                            x1,y1,x2,y2 = region['boundaries']
                            width = (x2 - x1) if (x2 > x1) else (x1 - x2)
                            height = (y2 - y1) if (y2 > y1) else (y1 - y2)
                            rectI = selectinwindow.DragRectangle(image, wName, imageWidth, imageHeight)
                            rectI.outRect.setRegion(x1, y1, w= width, h= height)
                            cv2.namedWindow(rectI.wname)
                            cv2.setMouseCallback(rectI.wname, selectinwindow.dragrect, rectI)

                            # keep looping until rectangle finalized
                            if selectinwindow.run(rectI) is True:
                                print("Updated coordinates")
                                x1, y1, x2, y2 = rectI.outRect.x, rectI.outRect.y, rectI.outRect.x + rectI.outRect.w, rectI.outRect.y + rectI.outRect.h
                                region['boundaries'] = (x1, y1, x2, y2)
                                update_cnt += 1


                            if update_cnt > 0 or region.get("type", None) is None:
                                # Ask for the type of parsing
                                print("Select the type of parsing")
                                selection = dropdown_dialog("Select Type", list(PARSE_OPTIONS.keys()), "What kind of pdf parsing are you processing?")
                                if selection:
                                    print(f"Selected: {selection}")
                                    region['type'] = selection
                                else:
                                    print("Selection canceled")
                    
                add_region = message_dialog("Add region", "Do you want to add a new region?", "Yes", "No")
                if load_regions is False:
                    regions = []
                while add_region is True:
                    wName = '%s (double click the rectangle to add the boundaries)' % f_image
                    #get the width and height of the image
                    imageHeight, imageWidth = image.shape[:2]
                    rectI = selectinwindow.DragRectangle(image, wName, imageWidth, imageHeight)
                    cv2.namedWindow(rectI.wname)
                    cv2.setMouseCallback(rectI.wname, selectinwindow.dragrect, rectI)

                    # keep looping until rectangle finalized
                    region = {}
                    if selectinwindow.run(rectI) is True:
                        print("Updated coordinates")
                        x1, y1, x2, y2 = rectI.outRect.x, rectI.outRect.y, rectI.outRect.x + rectI.outRect.w, rectI.outRect.y + rectI.outRect.h
                        region['boundaries'] = (x1, y1, x2, y2)
                        regions.append(region)
                        selection = dropdown_dialog("Select Type", OPTIONS, "What kind of pdf parsing are you processing?")
                        if selection:
                            print(f"Selected: {selection}")
                            region['type'] = selection
                        else:
                            print("Selection canceled")
                        # Ask for the type of parsing
                        update_cnt += 1
                    add_region = message_dialog("Add region", "Do you want to add a new region?", "Yes", "No")
                    
                

                if update_cnt > 0:
                    json_file = ".tmp/regions_%d.json" % page
                    with open(json_file, "w", encoding='utf-8') as file:
                        data = {"regions": regions}
                        json.dump(data, file, indent=4, ensure_ascii=False)


        out_str = {}
        for pagenum in pages:
            
            regions = load_bounding_boxes(pagenum)
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
                















# Retrieve Faktura Name and address


