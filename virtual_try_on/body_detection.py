import cv2
from pymsgbox import alert

# Initialize the video capture object
cap = cv2.VideoCapture(0)  # Use 0 for the default camera

# Initialize variables for storing previous frame and movement threshold
prev_frame = None
movement_threshold = 50000  # Adjust this value based on your environment

while True:
    # Read the current frame from the video stream
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale for processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)

    # Initialize the previous frame if it's None
    if prev_frame is None:
        prev_frame = gray_blur
        continue

    # Calculate the absolute difference between the current frame and the previous frame
    frame_diff = cv2.absdiff(prev_frame, gray_blur)

    # Apply a threshold to identify areas of movement
    _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

    # Find contours of the movement areas
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through the contours and draw rectangles around the movement areas
    for contour in contours:
        if cv2.contourArea(contour) > movement_threshold:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Display a message box when motion is detected
            alert(text='Motion Detected!', title='Motion Detection')

    # Display the frame with movement detection
    cv2.imshow('Movement Detection', frame)

    # Update the previous frame
    prev_frame = gray_blur

    # Check for 'q' key press to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
