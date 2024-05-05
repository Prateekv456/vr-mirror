import os
import cv2
import cvzone
from cvzone.PoseModule import PoseDetector
import numpy as np

# Load video and pose detector
cap = cv2.VideoCapture(0)
detector = PoseDetector()

# Set camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Change to your desired width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Change to your desired height

# Get camera resolution
cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Path to the folder containing T-shirt images
shirtFolderPath = "Resources/Shirts"
listShirts = os.listdir(shirtFolderPath)

# Index to track the current T-shirt image being displayed
imageNumber = 0

# Load button images without alpha channel
imgButtonRight = cv2.imread("Resources/button.png", cv2.IMREAD_COLOR)
imgButtonRight = cv2.resize(imgButtonRight, (0, 0), fx=0.5, fy=0.5)  # Resize button
imgButtonLeft = cv2.flip(imgButtonRight, 1)

# Calculate positions of buttons
button_size = imgButtonRight.shape[:2]
button_margin = 20
button_top_offset = int(cam_height * 0.1)
button_right_pos = (cam_width - button_margin - button_size[1], button_top_offset)
button_left_pos = (button_margin, button_top_offset)

print("Button size:", button_size)
print("Button right position:", button_right_pos)
print("Button left position:", button_left_pos)

# Variables to control button interaction
counterRight = 0
counterLeft = 0
selectionSpeed = 10

while True:
    success, img = cap.read()
    if not success:
        break

    # Detect poses in the frame
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

    if lmList:
        # Extract key points for the left and right shoulders
        shoulder_left = lmList[11][1:3]  # Left shoulder
        shoulder_right = lmList[12][1:3]  # Right shoulder

        if all(shoulder_left) and all(shoulder_right):
            # Calculate the distance between the shoulder keypoints
            shoulder_distance = np.linalg.norm(np.array(shoulder_left) - np.array(shoulder_right))

            # Load and resize the current T-shirt image
            imgShirtPath = os.path.join(shirtFolderPath, listShirts[imageNumber])
            if os.path.exists(imgShirtPath):
                imgShirt = cv2.imread(imgShirtPath, cv2.IMREAD_UNCHANGED)

                # Calculate the scale factor based on shoulder distance
                scale_factor = shoulder_distance / 100.0  # Adjust this value as needed

                # Resize the shirt image based on the scale factor
                imgShirt = cv2.resize(imgShirt, None, fx=scale_factor, fy=scale_factor)

                # Calculate the position to overlay the T-shirt
                overlay_pos_x = int(shoulder_right[0] - imgShirt.shape[1] / 2)
                overlay_pos_y = int(shoulder_right[1] - imgShirt.shape[0] / 2)

                try:
                    # Ensure overlay position does not go beyond frame boundaries
                    overlay_pos_x = max(0, overlay_pos_x)
                    overlay_pos_y = max(0, overlay_pos_y)
                    img = cvzone.overlayPNG(img, imgShirt, (overlay_pos_x, overlay_pos_y))
                except Exception as e:
                    print(f"Error overlaying shirt: {e}")

        # Display button overlays
        img[button_right_pos[1]:button_right_pos[1] + button_size[0],
            button_right_pos[0]:button_right_pos[0] + button_size[1]] = imgButtonRight
        img[button_left_pos[1]:button_left_pos[1] + button_size[0],
            button_left_pos[0]:button_left_pos[0] + button_size[1]] = imgButtonLeft

        # Button interaction logic
        if lmList[16][1] < 300:
            counterRight += 1
            cv2.ellipse(img, (button_right_pos[0] + button_size[1] // 2, button_right_pos[1] + button_size[0] // 2), (30, 30), 0, 0,
                        counterRight * selectionSpeed, (0, 255, 0), 10)
            if counterRight * selectionSpeed > 360:
                counterRight = 0
                if imageNumber < len(listShirts) - 1:
                    imageNumber += 1
        elif lmList[15][1] > 900:
            counterLeft += 1
            cv2.ellipse(img, (button_left_pos[0] + button_size[1] // 2, button_left_pos[1] + button_size[0] // 2), (30, 30), 0, 0,
                        counterLeft * selectionSpeed, (0, 255, 0), 10)
            if counterLeft * selectionSpeed > 360:
                counterLeft = 0
                if imageNumber > 0:
                    imageNumber -= 1

    # Display the modified frame
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()
