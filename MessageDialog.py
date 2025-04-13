import cv2
import numpy as np

def message_dialog(title, message="", confirm_label="OK", cancel_label="Cancel"):
    """
    Create a simple message dialog using OpenCV.
    
    Args:
        title: Window title
        message: Message to display
        confirm_label: Text for confirm button
        cancel_label: Text for cancel button
        
    Returns:
        True if confirmed, False if canceled.
    """
    # Constants
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 180
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 40
    
    # State variables
    confirm_clicked = False
    canceled = False
    
    # Create base image
    img = np.ones((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8) * 240
    
    # Draw title and message
    cv2.putText(img, title, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Split message into multiple lines if needed (max 40 chars per line)
    y_offset = 70
    if message:
        words = message.split()
        line = ""
        for word in words:
            if len(line + word) + 1 > 40:  # +1 for the space
                cv2.putText(img, line, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                y_offset += 25
                line = word
            else:
                if line:
                    line += " " + word
                else:
                    line = word
        
        # Don't forget the last line
        if line:
            cv2.putText(img, line, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    # Draw confirmation buttons
    confirm_x = WINDOW_WIDTH // 4 - BUTTON_WIDTH // 2
    cancel_x = 3 * WINDOW_WIDTH // 4 - BUTTON_WIDTH // 2
    buttons_y = WINDOW_HEIGHT - BUTTON_HEIGHT - 30
    
    # Mouse callback function
    def mouse_callback(event, x, y, flags, param):
        nonlocal confirm_clicked, canceled
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if click is on confirm button
            if confirm_x <= x <= confirm_x + BUTTON_WIDTH and buttons_y <= y <= buttons_y + BUTTON_HEIGHT:
                confirm_clicked = True
            
            # Check if click is on cancel button
            elif cancel_x <= x <= cancel_x + BUTTON_WIDTH and buttons_y <= y <= buttons_y + BUTTON_HEIGHT:
                canceled = True
    
    # Create window and register callback
    cv2.namedWindow(title)
    cv2.setMouseCallback(title, mouse_callback)
    
    # Main loop
    while not (confirm_clicked or canceled):
        # Create a fresh copy of the background
        display = img.copy()
        
        # Draw buttons
        cv2.rectangle(display, (confirm_x, buttons_y), 
                     (confirm_x + BUTTON_WIDTH, buttons_y + BUTTON_HEIGHT), 
                     (150, 200, 150), -1)
        cv2.putText(display, confirm_label, 
                   (confirm_x + 35, buttons_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        cv2.rectangle(display, (cancel_x, buttons_y), 
                     (cancel_x + BUTTON_WIDTH, buttons_y + BUTTON_HEIGHT), 
                     (200, 150, 150), -1)
        cv2.putText(display, cancel_label, 
                   (cancel_x + 25, buttons_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # Show the dialog
        cv2.imshow(title, display)
        key = cv2.waitKey(30)
        
        # Handle key input
        if key == 27:  # ESC key
            canceled = True
        elif key == 13:  # Enter key
            confirm_clicked = True
            
        # Check if window was closed
        if cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) < 1:
            canceled = True
            return confirm_clicked
    
    cv2.destroyWindow(title)
    
    return confirm_clicked