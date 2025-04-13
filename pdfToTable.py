import argparse
import os
import pdfplumber

import cv2
import json

from textwrap import wrap
from DropdownDialog import dropdown_dialog 
from InputDialog import input_dialog
from MessageDialog import message_dialog



import selectinwindow

def table_to_json(parsed_table):
    """
    Convert the parsed table to a JSON format.
    """
    json_data = []
    if parsed_table is None:
        return

    for row in parsed_table:
        json_row = {}
        for i, cell in enumerate(row):
            json_row[f"col_{i}"] = cell
        json_data.append(json_row)
    return json_data

def table_header_to_json(parsed_table):
    """
    Convert the parsed table with header to a JSON format.
    """
    if parsed_table is None:
        return {}
    json_data = {}
    header = parsed_table[0]
    for i, cell in enumerate(header):
        json_data[cell] = []
    
    for row in parsed_table[1:]:
        for i, cell in enumerate(row):
            json_data[header[i]].append(cell)
    
    return json_data

def header_to_json(parsed_str):
    """
    Convert the parsed header to a JSON format.
    """
    json_data = {}
    json_data["header"] = parsed_str
    return json_data
    

OPTIONS = ["Table", "Table w Header", "Header"]

PARSE_OPTIONS = {
    "Table": table_to_json,
    "Table w Header": table_header_to_json,
    "Header": header_to_json
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
    args = parser.parse_args()

    BOUNDING_BOXES = []#load_bounding_boxes()

    #if tmp folder doesn't exist then make it
    if os.path.exists(".tmp") == False:
        os.mkdir(".tmp")

    image_files = []




    pages = args.pages


    if pages is None:
        # Get last page number used
        last_page = "1-3"
        if os.path.exists(".tmp/last_page"):
            with open(".tmp/last_page", "r") as file:
                last_page = file.read()
        
        pages = input_dialog("Select pages", "Enter the pages to process (e.g., 1,2,3 or 1-3):", last_page)
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
        for f_image, page  in zip(image_files, pages):
            # Load the image saved from pdfplumber
            print(f"Processing image {f_image}")
            image = cv2.imread(f_image)
            
            # Load the bounding boxes from the JSON file
            regions = load_bounding_boxes(page)  
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
                            selection = dropdown_dialog("Select Type", OPTIONS, "What kind of pdf parsing are you processing?")
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
                ptype = region.get('type', header_to_json)
                pstr = ""
                if ptype.find("Table") != -1:
                    pstr = page.within_bbox(region['boundaries']).extract_table()
                else:
                    pstr = page.within_bbox(region['boundaries']).extract_text()

                out_str["%s_%s" % (pagenum,cnt)] = PARSE_OPTIONS[ptype](pstr)
                cnt += 1

        # Save the extracted data to a JSON file
        if len(out_str):
            json_file = "extracted_data.json"
            with open(json_file, "w", encoding='utf-8') as file:
                json.dump(out_str, file, indent=4, ensure_ascii=False)
                















# Retrieve Faktura Name and address


