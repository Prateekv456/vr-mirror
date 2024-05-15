import os
import cv2
import cvzone
from cvzone.PoseModule import PoseDetector
import numpy as np

def find_matching_resolution(target_width, target_height):

    cv2.namedWindow("temp", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("temp", target_width, target_height)
    
    actual_width = cv2.getWindowImageRect("temp")[2]
    actual_height = cv2.getWindowImageRect("temp")[3]
    
    cv2.destroyWindow("temp")
    
    return actual_width, actual_height


cap = cv2.VideoCapture(0)
detector = PoseDetector()

target_width = 1540
target_height = 845


actual_width, actual_height = find_matching_resolution(target_width, target_height)

print("Actual resolution:", actual_width, "x", actual_height)


cap.set(cv2.CAP_PROP_FRAME_WIDTH, actual_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, actual_height)


cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


shirtFolderPath = "Resources/Shirts"
listShirts = os.listdir(shirtFolderPath)


imageNumber = 0


imgButtonRight = cv2.imread("Resources/button.png", cv2.IMREAD_COLOR)
imgButtonRight = cv2.resize(imgButtonRight, (0, 0), fx=0.5, fy=0.5)  
imgButtonLeft = cv2.flip(imgButtonRight, 1)


button_size = imgButtonRight.shape[:2]
button_margin = 20
button_top_offset = int(cam_height * 0.1)
button_right_pos = (cam_width - button_margin - button_size[1], button_top_offset)
button_left_pos = (button_margin, button_top_offset)


font = cv2.FONT_HERSHEY_TRIPLEX  
heading_text = "Smart Mirror"
text_color = (255, 255, 255)  
text_size = 3  
text_thickness = 5
text_position = (int((cam_width - cv2.getTextSize(heading_text, font, text_size, text_thickness)[0][0]) / 2), int(cam_height * 0.1))  # Centered position

print("Button size:", button_size)
print("Button right position:", button_right_pos)
print("Button left position:", button_left_pos)


counterRight = 0
counterLeft = 0
selectionSpeed = 10


cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    if not success:
        break

    
    cv2.putText(img, heading_text, text_position, font, text_size, text_color, text_thickness, cv2.LINE_AA)

    
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

    if lmList:
        
        shoulder_left = lmList[11][1:3]  # Left shoulder
        shoulder_right = lmList[12][1:3]  # Right shoulder
        hip_left = lmList[23][1:3]  # Left hip
        hip_right = lmList[24][1:3]  # Right hip
        neck = lmList[28][1:3]  # Neck

        # Visualize shoulder points
        cv2.circle(img, (int(shoulder_left[0]), int(shoulder_left[1])), 5, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (int(shoulder_right[0]), int(shoulder_right[1])), 5, (0, 255, 0), cv2.FILLED)

        if all(shoulder_left) and all(shoulder_right) and all(hip_left) and all(hip_right) and all(neck):
           
            upper_body_width = max(shoulder_left[0], shoulder_right[0], hip_left[0], hip_right[0]) - min(shoulder_left[0], shoulder_right[0], hip_left[0], hip_right[0])
            upper_body_height = max(shoulder_left[1], shoulder_right[1], neck[1]) - min(hip_left[1], hip_right[1], neck[1])

            
            imgShirtPath = os.path.join(shirtFolderPath, listShirts[imageNumber])
            if os.path.exists(imgShirtPath):
                imgShirt = cv2.imread(imgShirtPath, cv2.IMREAD_UNCHANGED)

                
                scale_factor_x = upper_body_width / imgShirt.shape[1] * 0.9  # Reducing size by 10%
                scale_factor_y = upper_body_height / imgShirt.shape[0] * 0.9  # Reducing size by 10%

                
                if scale_factor_x > 0 and scale_factor_y > 0:
                    # Resize the T-shirt image
                    imgShirt = cv2.resize(imgShirt, None, fx=scale_factor_x, fy=scale_factor_y)

                    # Calculate the overlay position for the T-shirt image
                    overlay_pos_x = min(shoulder_left[0], shoulder_right[0]) - (upper_body_width - imgShirt.shape[1]) // 2
                    overlay_pos_y = min(shoulder_left[1], shoulder_right[1], neck[1]) - imgShirt.shape[0]

                    # Ensure the overlay position is within the frame boundaries
                    overlay_pos_x = max(0, overlay_pos_x)
                    overlay_pos_y = max(0, overlay_pos_y)

                    # Overlay the T-shirt image on the frame
                    try:
                        img = cvzone.overlayPNG(img, imgShirt, (overlay_pos_x, overlay_pos_y))
                    except Exception as e:
                        print(f"Error overlaying shirt: {e}")

        
        img[button_right_pos[1]:button_right_pos[1] + button_size[0],
            button_right_pos[0]:button_right_pos[0] + button_size[1]] = imgButtonRight
        img[button_left_pos[1]:button_left_pos[1] + button_size[0],
            button_left_pos[0]:button_left_pos[0] + button_size[1]] = imgButtonLeft

       
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

    
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
