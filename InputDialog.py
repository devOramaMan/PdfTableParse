import cv2
import numpy as np

def input_dialog(title, message="Enter your input:", default_text=""):
    """
    Create an input field dialog using OpenCV.
    
    Args:
        title: Window title
        message: Prompt message
        default_text: Default text in the input field
        
    Returns:
        The entered text or None if canceled.
    """
    # Constants
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 200
    INPUT_BOX_WIDTH = 400
    INPUT_BOX_HEIGHT = 40
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 40
    
    # State variables
    input_text = default_text
    confirm_clicked = False
    canceled = False
    
    # Create base image
    img = np.ones((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8) * 240
    
    # Draw title and message
    #cv2.putText(img, title, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, message, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    # Input box position
    input_x = (WINDOW_WIDTH - INPUT_BOX_WIDTH) // 2
    input_y = 70
    
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
    try:
        cv2.namedWindow(title)
    except cv2.error:
        print("Error creating window. It might already exist.")
        
    cv2.setMouseCallback(title, mouse_callback)
    
    # Main loop
    while not (confirm_clicked or canceled):
        # Create a fresh copy of the background
        display = img.copy()
        
        # Draw input box
        cv2.rectangle(display, (input_x, input_y), 
                     (input_x + INPUT_BOX_WIDTH, input_y + INPUT_BOX_HEIGHT), 
                     (255, 255, 255), -1)
        cv2.rectangle(display, (input_x, input_y), 
                     (input_x + INPUT_BOX_WIDTH, input_y + INPUT_BOX_HEIGHT), 
                     (0, 0, 0), 1)
        
        # Draw the current input text
        cv2.putText(display, input_text, 
                   (input_x + 10, input_y + INPUT_BOX_HEIGHT - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # Draw buttons
        cv2.rectangle(display, (confirm_x, buttons_y), 
                     (confirm_x + BUTTON_WIDTH, buttons_y + BUTTON_HEIGHT), 
                     (150, 200, 150), -1)
        cv2.putText(display, "Confirm", 
                   (confirm_x + 15, buttons_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        cv2.rectangle(display, (cancel_x, buttons_y), 
                     (cancel_x + BUTTON_WIDTH, buttons_y + BUTTON_HEIGHT), 
                     (200, 150, 150), -1)
        cv2.putText(display, "Cancel", 
                   (cancel_x + 25, buttons_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # Show the dialog
        cv2.imshow(title, display)
        key = cv2.waitKey(30)
        
        # Handle key input
        if key == 27:  # ESC key
            canceled = True
        elif key == 8:  # Backspace
            input_text = input_text[:-1]
        elif key == 13:  # Enter key
            confirm_clicked = True
        elif key != -1:  # Any other key
            input_text += chr(key)

        if cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) < 1:
            print("Window closed by user.")
            return None
    
    cv2.destroyWindow(title)
    
    if confirm_clicked:
        return input_text
    return None