import cv2
import mediapipe as mp
import time
import math
import serial  # Import library for Serial communication

class poseDetector():
    def __init__(self, mode=False, smooth=True, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.pTime = 0

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=self.mode,
                                smooth_landmarks=self.smooth,
                                min_detection_confidence=self.detectionCon,
                                min_tracking_confidence=self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, 
                                           self.mpPose.POSE_CONNECTIONS)
        return img

    def getPosition(self, img):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
        return self.lmList

    def showFps(self, img):
        cTime = time.time()
        fbs = 1 / (cTime - self.pTime)
        self.pTime = cTime
        cv2.putText(img, str(int(fbs)), (70, 80), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)

    def findAngle(self, img, p1, p2, p3, draw=True):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
        return angle


def main():
    detector = poseDetector()
    cap = cv2.VideoCapture(0)

    score = 0
    up_left = False
    down_left = False
    up_right = False
    down_right = False

    # Open serial communication to ESP8266
    ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with your port name

    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        lmList = detector.getPosition(img)

        if len(lmList) > 0:
            # Detect left arm: left shoulder (11), left elbow (13), left wrist (15)
            angle_left = detector.findAngle(img, 11, 13, 15)
            int_angle_left = int(angle_left)

            # Detect right arm: right shoulder (12), right elbow (14), right wrist (16)
            angle_right = detector.findAngle(img, 12, 14, 16)
            int_angle_right = int(angle_right)

            # Check if both arms are raised
            if int_angle_left < 30 and int_angle_right < 30:
                up_left = True
                up_right = True
                down_left = False
                down_right = False

            # Check if both arms are lowered after being raised
            elif int_angle_left > 30 and int_angle_right > 30 and up_left and up_right:
                score += 1
                up_left = False
                up_right = False
                down_left = True
                down_right = True
                print(f"Score: {score}")

                # Send signal to ESP8266 to control servo
                ser.write(b'1')  # Send '1' to rotate servo

                time.sleep(0.5)  # Delay to prevent score incrementing too quickly

        detector.showFps(img)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
