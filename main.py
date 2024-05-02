import os
import cv2
import cvzone
from cvzone.PoseModule import PoseDetector

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

# Fixed aspect ratio of the T-shirt image
fixedRatio = 262 / 190  # widthOfShirt / widthOfPoint11to12
shirtRatioHeightWidth = 581 / 440

# Index to track the current T-shirt image being displayed
imageNumber = 0

# Load button images
imgButtonRight = cv2.imread("Resources/button.png", cv2.IMREAD_UNCHANGED)
imgButtonLeft = cv2.flip(imgButtonRight, 1)

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
        lm11 = lmList[11][1:3]  # Left shoulder
        lm12 = lmList[12][1:3]  # Right shoulder

        # Load and resize the current T-shirt image
        imgShirtPath = os.path.join(shirtFolderPath, listShirts[imageNumber])
        if os.path.exists(imgShirtPath):
            imgShirt = cv2.imread(imgShirtPath, cv2.IMREAD_UNCHANGED)
            widthOfShirt = int((lm11[0] - lm12[0]) * fixedRatio)

            # Resize the shirt image based on the calculated width
            if widthOfShirt > 0:
                imgShirtHeight = int(widthOfShirt * shirtRatioHeightWidth)
                imgShirt = cv2.resize(imgShirt, (widthOfShirt, imgShirtHeight))

                # Calculate offset to properly position the T-shirt on the body
                currentScale = (lm11[0] - lm12[0]) / 190
                offset = int(44 * currentScale), int(48 * currentScale)

                try:
                    img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
                except Exception as e:
                    print(f"Error overlaying shirt: {e}")

        # Display button overlays
        img = cvzone.overlayPNG(img, imgButtonRight, (int(cam_width * 0.9), int(cam_height * 0.1)))
        img = cvzone.overlayPNG(img, imgButtonLeft, (int(cam_width * 0.1), int(cam_height * 0.1)))

        # Button interaction logic
        if lmList[16][1] < 300:
            counterRight += 1
            cv2.ellipse(img, (139, 360), (66, 66), 0, 0,
                        counterRight * selectionSpeed, (0, 255, 0), 20)
            if counterRight * selectionSpeed > 360:
                counterRight = 0
                if imageNumber < len(listShirts) - 1:
                    imageNumber += 1
        elif lmList[15][1] > 900:
            counterLeft += 1
            cv2.ellipse(img, (1138, 360), (66, 66), 0, 0,
                        counterLeft * selectionSpeed, (0, 255, 0), 20)
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