import cv2
import numpy as np

def dropdown_dialog(title, options, message="Select an option:", default_index=0):
    """
    Create a dropdown selection dialog using OpenCV
    
    Args:
        title: Window title
        options: List of string options for the dropdown
        message: Prompt message
        default_index: Default selected option index
        
    Returns:
        Selected option or None if canceled
    """
    # Constants
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 400
    DROPDOWN_WIDTH = 300
    DROPDOWN_HEIGHT = 40
    OPTION_HEIGHT = 30
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 40
    
    # State variables
    dropdown_open = False
    selected_index = default_index
    confirm_clicked = False
    canceled = False
    
    # Create base image
    img = np.ones((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8) * 240
    
    # Draw title and message
    cv2.putText(img, title, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, message, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    # Draw dropdown box area
    dropdown_x = (WINDOW_WIDTH - DROPDOWN_WIDTH) // 2
    dropdown_y = 100
    
    # Draw confirmation buttons
    confirm_x = WINDOW_WIDTH // 4 - BUTTON_WIDTH // 2
    cancel_x = 3 * WINDOW_WIDTH // 4 - BUTTON_WIDTH // 2
    buttons_y = WINDOW_HEIGHT - BUTTON_HEIGHT - 30
    
    # Mouse callback function
    def mouse_callback(event, x, y, flags, param):
        nonlocal dropdown_open, selected_index, confirm_clicked, canceled
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if click is in dropdown header
            if dropdown_x <= x <= dropdown_x + DROPDOWN_WIDTH and dropdown_y <= y <= dropdown_y + DROPDOWN_HEIGHT:
                dropdown_open = not dropdown_open
            
            # Check if click is in dropdown options (when open)
            elif dropdown_open and dropdown_x <= x <= dropdown_x + DROPDOWN_WIDTH:
                option_y = dropdown_y + DROPDOWN_HEIGHT
                for i, _ in enumerate(options):
                    if option_y <= y <= option_y + OPTION_HEIGHT:
                        selected_index = i
                        dropdown_open = False
                        break
                    option_y += OPTION_HEIGHT
            
            # Check if click is on confirm button
            elif confirm_x <= x <= confirm_x + BUTTON_WIDTH and buttons_y <= y <= buttons_y + BUTTON_HEIGHT:
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
        
        # Draw dropdown header
        cv2.rectangle(display, (dropdown_x, dropdown_y), 
                     (dropdown_x + DROPDOWN_WIDTH, dropdown_y + DROPDOWN_HEIGHT), 
                     (180, 180, 180), -1)
        
        # Draw selected option in header
        selected_text = options[selected_index]
        cv2.putText(display, selected_text, 
                   (dropdown_x + 10, dropdown_y + DROPDOWN_HEIGHT - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # Draw dropdown arrow
        arrow_pts = np.array([
            [dropdown_x + DROPDOWN_WIDTH - 20, dropdown_y + 15],
            [dropdown_x + DROPDOWN_WIDTH - 10, dropdown_y + 25],
            [dropdown_x + DROPDOWN_WIDTH - 30, dropdown_y + 25]
        ])
        cv2.fillPoly(display, [arrow_pts], (0, 0, 0))
        
        # Draw dropdown options if open
        if dropdown_open:
            option_y = dropdown_y + DROPDOWN_HEIGHT
            for i, option in enumerate(options):
                # Highlight selected option
                bg_color = (220, 220, 255) if i == selected_index else (220, 220, 220)
                
                cv2.rectangle(display, (dropdown_x, option_y), 
                             (dropdown_x + DROPDOWN_WIDTH, option_y + OPTION_HEIGHT), 
                             bg_color, -1)
                cv2.rectangle(display, (dropdown_x, option_y), 
                             (dropdown_x + DROPDOWN_WIDTH, option_y + OPTION_HEIGHT), 
                             (180, 180, 180), 1)
                cv2.putText(display, option, 
                           (dropdown_x + 10, option_y + OPTION_HEIGHT - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                option_y += OPTION_HEIGHT
        
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
        if key == 27:  # ESC key
            canceled = True
            
        if cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) < 1:
            print("Window closed by user.")
            canceled = True
    try:
        cv2.destroyWindow(title)
    except:
        pass
    
    if confirm_clicked:
        return options[selected_index]
    return None