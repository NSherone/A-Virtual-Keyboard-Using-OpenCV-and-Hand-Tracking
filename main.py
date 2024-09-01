import cv2
from cvzone.HandTrackingModule import HandDetector
import math
from time import sleep
from pynput.keyboard import Controller, Key

# Initialize the camera and set its properties
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width (increased for bigger screen)
cap.set(4, 720)   # Height (increased for bigger screen)

def calculateDistance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

# Initialize the HandDetector with a detection confidence threshold
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Define the keys layout with backspace and space keys
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["Space", "Backspace"]]

finalText = ""

keyboard = Controller()

def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 234), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
    return img

class Button:
    def __init__(self, pos, text, size=[85, 85]):  # Increased button size
        self.pos = pos
        self.size = size
        self.text = text

# Create a list of Button instances
buttonList = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        if key == "Space":
            buttonList.append(Button([j * 100 + 100, i * 100 + 50], key, size=[300, 85]))
        elif key == "Backspace":
            buttonList.append(Button([j * 100 + 500, i * 100 + 50], key, size=[150, 85]))
        else:
            buttonList.append(Button([j * 100 + 50, i * 100 + 50], key))  # Adjusted spacing and positioning

while True:
    success, img = cap.read()  # Capture a frame from the camera
    if not success:
        break
    
    img = cv2.flip(img, 1)  # Flip the image horizontally

    hands, img = detector.findHands(img)  # Detect hands in the frame
    
    # Draw all buttons on the image
    img = drawAll(img, buttonList)
    
    if hands:
        hand = hands[0]  # Get the first detected hand
        lmList = hand["lmList"]  # List of 21 landmarks
        if lmList:
            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                
                # Landmark 8 is the tip of the index finger
                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

                    # Check if the landmarks are valid
                    l = calculateDistance(lmList[8], lmList[12])  # Distance between index and middle fingers
                    if l < 35:
                        # Change button to green and display the text
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 60), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

                        # Render the change before executing the key press
                        cv2.imshow("Image", img)
                        cv2.waitKey(10)

                        # Handle the key press
                        if button.text == "Space":
                            keyboard.press(Key.space)
                            finalText += " "
                        elif button.text == "Backspace":
                            keyboard.press(Key.backspace)
                            finalText = finalText[:-1]
                        else:
                            keyboard.press(button.text)
                            finalText += button.text
                        
                        sleep(0.5)  # Reduced sleep to make it more responsive
                        
    cv2.rectangle(img, (50, 550), (1230, 650), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 630), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)  # Smaller font for final text
    
    cv2.imshow("Image", img)  # Display the frame
    
    key = cv2.waitKey(1) & 0xFF  # Adjust the delay, 1ms for near real-time response
    if key == ord('q'):  # Press 'q' to exit the loop
        break

cap.release()  # Release the camera
cv2.destroyAllWindows()  # Close all OpenCV windows
