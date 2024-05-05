import cv2

def find_matching_resolution(target_width, target_height):
    # Open a temporary window
    cv2.namedWindow("temp", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("temp", target_width, target_height)
    
    # Get the actual resolution of the window
    actual_width = cv2.getWindowImageRect("temp")[2]
    actual_height = cv2.getWindowImageRect("temp")[3]
    
    # Close the temporary window
    cv2.destroyWindow("temp")
    
    return actual_width, actual_height

# Specify your desired resolution
target_width = 1540
target_height = 845

# Find the matching resolution
actual_width, actual_height = find_matching_resolution(target_width, target_height)

print("Actual resolution:", actual_width, "x", actual_height)




# Create a full screen window
cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Main loop
while True:
    # Your code for capturing and processing frames goes here
    pass
