import cv2
from DropdownDialog import dropdown_dialog

class Button:
    def __init__(self, x, y, w, h, label):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.show = True
        self.pressed = False  # Add pressed state

    def draw(self, image):
        if not self.show:
            return
        
        if self.pressed:
        # Create a filled rectangle with gray color
            cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), (200, 200, 200), -1)
        else:
            # Create a filled rectangle with white color
            cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), (255, 255, 255), -1)

        #cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 255, 0), -1)
        cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 0, 0), 2)
        #cv2.putText(image, self.label, (self.x + 10, self.y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(image, self.label, (self.x + 5, self.y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

    def is_clicked(self, x, y):
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h
    
    def setVisible(self, visible):
        self.show = visible
        #cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 0, 0), -1)
        #cv2.putText(image, " " * len(self.label), (self.x + 10, self.y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        #cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 0, 0), -1)
        #cv2.putText(image, " " * len(self.label), (self.x + 3, self.y + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

class TextInput:
    def __init__(self, x, y, w, h, label, value="1"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.value = value
        self.active = False
        self.show = True

    def draw(self, image, value=None):
        if value is not None:
            self.value = str(value)
        if not self.show:
            return
        # Draw label
        cv2.putText(image, self.label, (self.x - 50, self.y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
        
        # Draw input box
        box_color = (0, 120, 255) if self.active else (0, 0, 0)
        cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), box_color, 2)
        
        # Draw value
        cv2.putText(image, self.value, (self.x + 5, self.y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

    def is_clicked(self, x, y):
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h
    
class Rect:
    x = None
    y = None
    w = None
    h = None

    def printit(self):
        print(str(self.x) + ',' + str(self.y) + ',' + str(self.w) + ',' + str(self.h))

    def setRegion(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


def resize_to_fit_screen(image, max_width=1920, max_height=1080):
    """
    Resize an image to fit within the specified dimensions while maintaining
    the aspect ratio.
    
    Args:
        image: The input image
        max_width: Maximum width of the screen (default 1920)
        max_height: Maximum height of the screen (default 1080)
        
    Returns:
        Resized image that fits within the specified dimensions
    """
    height, width = image.shape[:2]
    
    # Calculate the ratio of the width and height to the max dimensions
    width_ratio = max_width / width
    height_ratio = max_height / height
    
    # Use the smaller ratio to ensure the image fits within both dimensions
    ratio = min(width_ratio, height_ratio)
    
    # Don't upscale small images
    if ratio > 1:
        return image
        
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    
    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return resized_image


class DragRectangle:
    # Limits on the canvas
    keepWithin = Rect()
    # To store rectangle
    outRect = Rect()
    # To store rectangle anchor point
    # Here the rect class object is used to store
    # the distance in the x and y direction from
    # the anchor point to the top-left and the bottom-right corner
    anchor = Rect()
    # Selection marker size
    sBlk = 4
    # Whether initialized or not
    initialized = False

    # Image
    image = None

    # Window Name
    wname = ""

    # Return flag
    returnflag = False

    # FLAGS
    # Rect already present
    active = False
    # Drag for rect resize in progress
    drag = False
    # Marker flags by positions
    TL = False
    TM = False
    TR = False
    LM = False
    RM = False
    BL = False
    BM = False
    BR = False
    hold = False
    exit = False

    def __init__(self, Img, windowName, windowWidth, windowHeight, pageNum=1, options=["Text", "Table", "Image"]):
        # Image
        self.image = Img
        self.pageNum = pageNum
        self.options = options
        # Window name
        self.wname = windowName

        self.cnt = 0

        # Limit the selection box to the canvas
        self.keepWithin.x = 0
        self.keepWithin.y = 0
        self.keepWithin.w = windowWidth
        self.keepWithin.h = windowHeight

        # Set rect to zero width and height
        self.outRect.x = 0
        self.outRect.y = 0
        self.outRect.w = 0
        self.outRect.h = 0

        self.addRegion = Button(10, 2, 100, 20, "Add Region")
        self.prevPage = Button(120, 2, 50, 20, "Prev")
        self.pageInput = TextInput(180, 2, 50, 20, "", str(pageNum))
        self.nextPage = Button(240, 2, 50, 20, "Next")
        self.doneButton = Button(300, 2, 50, 20, "Done")  # Added Done button
        self.buttons = {1: self.addRegion, 2: self.prevPage, 3: self.pageInput, 4: self.nextPage, 5: self.doneButton}
        self.getPageFunc = None
        self.regions = {}
        self.selectedEvent = None

    def setRenderPtr(self, renderPtr):
        self.getPageFunc = renderPtr


    def drawButtons(self, img=None):
        if img is None:
            img = self.image
        self.addRegion.draw(img)
        self.nextPage.draw(img)
        self.prevPage.draw(img)
        self.pageInput.draw(img, self.pageNum)
        self.doneButton.draw(img)  # Draw Done button

    def pointInWidgetRect(self, x, y):
        if self.addRegion.is_clicked(x, y):
            return 1
        elif self.prevPage.is_clicked(x, y):
            return 2
        elif self.pageInput.is_clicked(x, y):
            return 3
        elif self.nextPage.is_clicked(x, y):
            return 4
        elif self.doneButton.is_clicked(x, y):  # Handle Done button
            return 5
        return 0

    def handleWidgetDown(self, event):
        if event not in self.buttons:
            return
        # Set the pressed state of the button to True
        self.buttons[event].pressed = True
        self.buttons[event].draw(self.image)
        tmp = self.image.copy()
        cv2.rectangle(tmp, (self.outRect.x, self.outRect.y),
                  (self.outRect.x + self.outRect.w,
                   self.outRect.y + self.outRect.h), (0, 255, 0), 2)
        cv2.imshow(self.wname, tmp)

        self.selectedEvent = event

    def handleWidgetUp(self, event):
        if self.selectedEvent not in self.buttons:
            return
        
        # Reset the pressed state of the button
        self.buttons[self.selectedEvent].pressed = False
        self.buttons[self.selectedEvent].draw(self.image)

        tmp = self.image.copy()
        cv2.rectangle(tmp, (self.outRect.x, self.outRect.y),
                  (self.outRect.x + self.outRect.w,
                   self.outRect.y + self.outRect.h), (0, 255, 0), 2)
        cv2.imshow(self.wname, tmp)

        if event == self.selectedEvent:
            self.selectedEvent = None
            return self.handleWidgetEvent(event)


    def handleWidgetEvent(self, event):
        if event == 1:
            x1, y1, x2, y2 = self.outRect.x, self.outRect.y, self.outRect.x + self.outRect.w, self.outRect.y + self.outRect.h
            
            if (x1, y1, x2, y2) == (0, 0, 0, 0):
                print("No region selected")
                return None
            
            region = {}
            region['boundaries'] = (x1, y1, x2, y2)
            selection = dropdown_dialog("Select Type", self.options, "What kind of pdf parsing are you processing?")
            if selection:
                print(f"Selected: {selection}")
                region['type'] = selection
                if self.pageNum in self.regions:
                    # Append to existing regions if the boundaries then remove the old one
                    for i, r in enumerate(self.regions[self.pageNum]):
                        if r['boundaries'] == region['boundaries']:
                            self.regions[self.pageNum].pop(i)
                            break
                    self.regions[self.pageNum].append(region)
                else:
                    self.regions[self.pageNum] = [ region ]
                #Add a text to the upper left corner of the rectangle with the type of region bold and blue 
                #First draw a white rectangle background for only for the text
                (text_width, text_height), baseline = cv2.getTextSize(selection, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)

                # Add padding (optional)
                padding_x = 10
                padding_y = 5
                txt_w = text_width + padding_x * 2
                txt_h = text_height + padding_y * 2 + baseline
                cv2.rectangle(self.image, (self.outRect.x, self.outRect.y),
                        (self.outRect.x + txt_w,
                        self.outRect.y + txt_h), (255, 255, 255), -1)
                cv2.putText(self.image, selection, (self.outRect.x + 5, self.outRect.y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 0), 1)
                cv2.rectangle(self.image, (self.outRect.x, self.outRect.y),
                        (self.outRect.x + self.outRect.w,
                        self.outRect.y + self.outRect.h), (255, 0, 0), 2)
                cv2.imshow(self.wname, self.image)
                self.outRect.x, self.outRect.y, self.outRect.w, self.outRect.h = (0, 0, 0, 0)
                self.active = False
            else:
                cv2.imshow(self.wname, self.image)
                self.outRect.x, self.outRect.y, self.outRect.w, self.outRect.h = (0, 0, 0, 0)
                self.active = False
                print("Selection canceled")
            return "addRegion"
        elif event == 2:
            if self.getPageFunc is None and self.pageNum > 0:
                return None

            f_image = self.getPageFunc(self.pageNum - 1)
            if f_image is None:
                return None
            self.pageNum -= 1
            print(f"Processing image {f_image}")
            self.image = cv2.imread(f_image)
            imageHeight, imageWidth = self.image.shape[:2]
            #self.wname = f"Page {self.pageNum}"
            self.keepWithin.w = imageWidth
            self.keepWithin.h = imageHeight
            cv2.imshow(self.wname, self.image)
            self.drawButtons()
            self.active = False

            return "prevPage"
        elif event == 3:
            self.pageInput.active = True
            self.active = False
            return "pageInput"
        elif event == 4:
            if self.getPageFunc is None:
                return None

            f_image = self.getPageFunc(self.pageNum + 1)
            if f_image is None:
                return None
            self.pageNum += 1
            print(f"Processing image {f_image}")
            self.image = cv2.imread(f_image)
            imageHeight, imageWidth = self.image.shape[:2]
            self.keepWithin.w = imageWidth
            self.keepWithin.h = imageHeight
            #self.wname = f"Page {self.pageNum}"
            cv2.imshow(self.wname, self.image)
            self.drawButtons()
            self.active = False
            return "nextPage"
        
        elif event == 5:
            self.exit = True
            cv2.destroyWindow(self.wname)
            print("Done button pressed. Exiting.")
            self.returnflag = True
            return "done"
        else:
            return None


def dragrect(event, x, y, flags, dragObj):
    if x < dragObj.keepWithin.x:
        x = dragObj.keepWithin.x
    if y < dragObj.keepWithin.y:
        y = dragObj.keepWithin.y
    if x > (dragObj.keepWithin.x + dragObj.keepWithin.w - 1):
        x = dragObj.keepWithin.x + dragObj.keepWithin.w - 1
    if y > (dragObj.keepWithin.y + dragObj.keepWithin.h - 1):
        y = dragObj.keepWithin.y + dragObj.keepWithin.h - 1

    if event == cv2.EVENT_LBUTTONDOWN:
        #print("Mouse down")
        mouseDown(x, y, dragObj)
    if event == cv2.EVENT_LBUTTONUP:
        #print("Mouse up")
        mouseUp(x, y, dragObj)
    if event == cv2.EVENT_MOUSEMOVE:
        #print("Mouse move %d %d" % (x, y))
        mouseMove(x, y, dragObj)
    if event == cv2.EVENT_LBUTTONDBLCLK:
        #print("Mouse double click")
        mouseDoubleClick(x, y, dragObj)


def pointInRect(pX, pY, rX, rY, rW, rH):
    if rX <= pX <= (rX + rW) and rY <= pY <= (rY + rH):
        return True
    else:
        return False


def mouseDoubleClick(eX, eY, dragObj):
    event =  dragObj.pointInWidgetRect(eX, eY)
    if event > 0:
        dragObj.handleWidgetEvent(event)
        return
    if dragObj.active:
        if pointInRect(eX, eY, dragObj.outRect.x, dragObj.outRect.y, dragObj.outRect.w, dragObj.outRect.h):
            #dragObj.returnflag = True
            #cv2.destroyWindow(dragObj.wname)
            dragObj.handleWidgetEvent(1)
        


def mouseDown(eX, eY, dragObj):
    event = dragObj.pointInWidgetRect(eX, eY)
    if event > 0:
        dragObj.handleWidgetDown(dragObj.pointInWidgetRect(eX, eY))
        return
    if dragObj.active:
        if pointInRect(eX, eY, dragObj.outRect.x - dragObj.sBlk,
                       dragObj.outRect.y - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.TL = True
            return
        if pointInRect(eX, eY, dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk,
                       dragObj.outRect.y - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.TR = True
            return
        if pointInRect(eX, eY, dragObj.outRect.x - dragObj.sBlk,
                       dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.BL = True
            return
        if pointInRect(eX, eY, dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk,
                       dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.BR = True
            return

        if pointInRect(eX, eY, dragObj.outRect.x + dragObj.outRect.w / 2 - dragObj.sBlk,
                       dragObj.outRect.y - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.TM = True
            return
        if pointInRect(eX, eY, dragObj.outRect.x + dragObj.outRect.w / 2 - dragObj.sBlk,
                       dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.BM = True
            return
        if pointInRect(eX, eY, dragObj.outRect.x - dragObj.sBlk,
                       dragObj.outRect.y + dragObj.outRect.h / 2 - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.LM = True
            return
        if pointInRect(eX, eY, dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk,
                       dragObj.outRect.y + dragObj.outRect.h / 2 - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.RM = True
            return

        # This has to be below all of the other conditions
        if pointInRect(eX, eY, dragObj.outRect.x, dragObj.outRect.y, dragObj.outRect.w, dragObj.outRect.h):
            dragObj.anchor.x = eX - dragObj.outRect.x
            dragObj.anchor.w = dragObj.outRect.w - dragObj.anchor.x
            dragObj.anchor.y = eY - dragObj.outRect.y
            dragObj.anchor.h = dragObj.outRect.h - dragObj.anchor.y
            dragObj.hold = True

            return

    else:
        dragObj.outRect.x = eX
        dragObj.outRect.y = eY
        dragObj.drag = True
        dragObj.active = True
        return


def mouseMove(eX, eY, dragObj):
    
    if dragObj.drag & dragObj.active:
        dragObj.outRect.w = eX - dragObj.outRect.x
        dragObj.outRect.h = eY - dragObj.outRect.y
        clearCanvasNDraw(dragObj)
        return

    if dragObj.hold:
        dragObj.outRect.x = eX - dragObj.anchor.x
        dragObj.outRect.y = eY - dragObj.anchor.y

        if dragObj.outRect.x < dragObj.keepWithin.x:
            dragObj.outRect.x = dragObj.keepWithin.x
        if dragObj.outRect.y < dragObj.keepWithin.y:
            dragObj.outRect.y = dragObj.keepWithin.y
        if (dragObj.outRect.x + dragObj.outRect.w) > (dragObj.keepWithin.x + dragObj.keepWithin.w - 1):
            dragObj.outRect.x = dragObj.keepWithin.x + dragObj.keepWithin.w - 1 - dragObj.outRect.w
        if (dragObj.outRect.y + dragObj.outRect.h) > (dragObj.keepWithin.y + dragObj.keepWithin.h - 1):
            dragObj.outRect.y = dragObj.keepWithin.y + dragObj.keepWithin.h - 1 - dragObj.outRect.h

        clearCanvasNDraw(dragObj)
        return

    if dragObj.TL:
        dragObj.outRect.w = (dragObj.outRect.x + dragObj.outRect.w) - eX
        dragObj.outRect.h = (dragObj.outRect.y + dragObj.outRect.h) - eY
        dragObj.outRect.x = eX
        dragObj.outRect.y = eY
        clearCanvasNDraw(dragObj)
        return
    if dragObj.BR:
        dragObj.outRect.w = eX - dragObj.outRect.x
        dragObj.outRect.h = eY - dragObj.outRect.y
        clearCanvasNDraw(dragObj)
        return
    if dragObj.TR:
        dragObj.outRect.h = (dragObj.outRect.y + dragObj.outRect.h) - eY
        dragObj.outRect.y = eY
        dragObj.outRect.w = eX - dragObj.outRect.x
        clearCanvasNDraw(dragObj)
        return
    if dragObj.BL:
        dragObj.outRect.w = (dragObj.outRect.x + dragObj.outRect.w) - eX
        dragObj.outRect.x = eX
        dragObj.outRect.h = eY - dragObj.outRect.y
        clearCanvasNDraw(dragObj)
        return

    if dragObj.TM:
        dragObj.outRect.h = (dragObj.outRect.y + dragObj.outRect.h) - eY
        dragObj.outRect.y = eY
        clearCanvasNDraw(dragObj)
        return
    if dragObj.BM:
        dragObj.outRect.h = eY - dragObj.outRect.y
        clearCanvasNDraw(dragObj)
        return
    if dragObj.LM:
        dragObj.outRect.w = (dragObj.outRect.x + dragObj.outRect.w) - eX
        dragObj.outRect.x = eX
        clearCanvasNDraw(dragObj)
        return
    if dragObj.RM:
        dragObj.outRect.w = eX - dragObj.outRect.x
        clearCanvasNDraw(dragObj)
        return


def mouseUp(x, y, dragObj):
    event = dragObj.pointInWidgetRect(x, y)
    if event > 0:
        dragObj.handleWidgetUp(event)
        return
    dragObj.drag = False
    disableResizeButtons(dragObj)
    straightenUpRect(dragObj)
    if dragObj.outRect.w == 0 or dragObj.outRect.h == 0:
        dragObj.active = False

    clearCanvasNDraw(dragObj)


def disableResizeButtons(dragObj):
    dragObj.TL = dragObj.TM = dragObj.TR = False
    dragObj.LM = dragObj.RM = False
    dragObj.BL = dragObj.BM = dragObj.BR = False
    dragObj.hold = False


def straightenUpRect(dragObj):
    """
    Make sure x, y, w, h of the Rect are positive
    """
    if dragObj.outRect.w < 0:
        dragObj.outRect.x = dragObj.outRect.x + dragObj.outRect.w
        dragObj.outRect.w = -dragObj.outRect.w
    if dragObj.outRect.h < 0:
        dragObj.outRect.y = dragObj.outRect.y + dragObj.outRect.h
        dragObj.outRect.h = -dragObj.outRect.h


def startupDraw(dragObj):
    tmp = dragObj.image.copy()
    cv2.rectangle(tmp, (dragObj.outRect.x, dragObj.outRect.y),
                  (dragObj.outRect.x + dragObj.outRect.w,
                   dragObj.outRect.y + dragObj.outRect.h), (0, 255, 0), 2)
    drawSelectMarkers(tmp, dragObj)
    cv2.imshow(dragObj.wname, tmp)
    dragObj.drawButtons()

def clearCanvasNDraw(dragObj):
    # Draw
    if dragObj.exit is True:
        return
    tmp = dragObj.image.copy()
    cv2.rectangle(tmp, (dragObj.outRect.x, dragObj.outRect.y),
                  (dragObj.outRect.x + dragObj.outRect.w,
                   dragObj.outRect.y + dragObj.outRect.h), (0, 255, 0), 2)
    #dragObj.drawButtons(tmp)
    drawSelectMarkers(tmp, dragObj)
    cv2.imshow(dragObj.wname, tmp)
    if dragObj.cnt > 0:
        return
    dragObj.cnt += 1
    key = cv2.waitKey()
    dragObj.exit = True
    return key


def drawSelectMarkers(image, dragObj):
    """
    Draw markers on the dragged rectangle
    """
    # Top-Left
    cv2.rectangle(image, (dragObj.outRect.x - dragObj.sBlk,
                          dragObj.outRect.y - dragObj.sBlk),
                  (dragObj.outRect.x - dragObj.sBlk + dragObj.sBlk * 2,
                   dragObj.outRect.y - dragObj.sBlk + dragObj.sBlk * 2),
                  (0, 255, 0), 2)
    # Top-Rigth
    cv2.rectangle(image, (dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk,
                          dragObj.outRect.y - dragObj.sBlk),
                  (dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk + dragObj.sBlk * 2,
                   dragObj.outRect.y - dragObj.sBlk + dragObj.sBlk * 2),
                  (0, 255, 0), 2)
    # Bottom-Left
    cv2.rectangle(image, (dragObj.outRect.x - dragObj.sBlk,
                          dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk),
                  (dragObj.outRect.x - dragObj.sBlk + dragObj.sBlk * 2,
                   dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk + dragObj.sBlk * 2),
                  (0, 255, 0), 2)
    # Bottom-Right
    cv2.rectangle(image, (dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk,
                          dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk),
                  (dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk + dragObj.sBlk * 2,
                   dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk + dragObj.sBlk * 2),
                  (0, 255, 0), 2)

    # Top-Mid
    cv2.rectangle(image, (dragObj.outRect.x + int(dragObj.outRect.w / 2) - dragObj.sBlk,
                          dragObj.outRect.y - dragObj.sBlk),
                  (dragObj.outRect.x + int(dragObj.outRect.w / 2) - dragObj.sBlk + dragObj.sBlk * 2,
                   dragObj.outRect.y - dragObj.sBlk + dragObj.sBlk * 2),
                  (0, 255, 0), 2)
    # Bottom-Mid
    cv2.rectangle(image, (dragObj.outRect.x + int(dragObj.outRect.w / 2) - dragObj.sBlk,
                          dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk),
                  (dragObj.outRect.x + int(dragObj.outRect.w / 2) - dragObj.sBlk + dragObj.sBlk * 2,
                   dragObj.outRect.y + dragObj.outRect.h - dragObj.sBlk + dragObj.sBlk * 2),
                  (0, 255, 0), 2)
    # Left-Mid
    cv2.rectangle(image, (dragObj.outRect.x - dragObj.sBlk,
                          dragObj.outRect.y + int(dragObj.outRect.h / 2) - dragObj.sBlk),
                  (dragObj.outRect.x - dragObj.sBlk + dragObj.sBlk * 2,
                   dragObj.outRect.y + int(dragObj.outRect.h / 2) - dragObj.sBlk + dragObj.sBlk * 2),
                  (0, 255, 0), 2)
    # Right-Mid
    cv2.rectangle(image, (dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk,
                          dragObj.outRect.y + int(dragObj.outRect.h / 2) - dragObj.sBlk),
                  (dragObj.outRect.x + dragObj.outRect.w - dragObj.sBlk + dragObj.sBlk * 2,
                   dragObj.outRect.y + int(dragObj.outRect.h / 2) - dragObj.sBlk + dragObj.sBlk * 2),
                  (0, 255, 0), 2)
    
    dragObj.drawButtons(image)
    
# obj dragObj
def run(obj):
    ret = False
    wName = obj.wname
    if obj.outRect.w != 0 and obj.outRect.h != 0:
      
        obj.active = True
        key = clearCanvasNDraw(obj)
        if obj.returnflag:
            ret = True
    else:
        obj.drawButtons()
    while obj.exit is False:
        # display the image
        cv2.imshow(wName, obj.image)
        key = cv2.waitKey(1) & 0xFF

        # Check if the ESC key is pressed
        if key == 27:  # ESC key
            print("Window closed with ESC key.")
            break
        
        # if returnflag is True, break from the loop
        if obj.returnflag:
            ret = True
            break

        # Check if the OpenCV window is closed by the user
        if cv2.getWindowProperty(wName, cv2.WND_PROP_VISIBLE) < 1:
            print("Window closed by user.")
            break

    obj.exit = True
    return ret