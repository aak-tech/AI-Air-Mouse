import cv2
import numpy as np
import handvolume as htm
import time
import autopy
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#########################
wCam, hCam = 640, 480
frameR = 125 # Frame Reduction
smoothening = 7
#########################

pTime = 0
plocX, plocY = 0, 0

clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1, detectionCon=0.7)
wScr, hScr = autopy.screen.size()
#print(wScr, hScr)

#pyCaw for volume control

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
maxVol = volRange[1]
minVol = volRange[0]









while True:
    # 1.find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)


    #2.get the tip of the index and middle fingers
    if len(lmList) !=0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # Filter based on size

        # find distance between index andd thumb


        # convert volume
        #Reduce Resolution to make it smoother
        #check fingers up
        #if pinky is down set the evolume
        #Drawing
        #Frame Rate



        # for volume finger
        x4, y4 = lmList[4][1], lmList[4][2]
        x5, y5 = lmList[8][1], lmList[8][2]
        # to get centerpoint
        cx, cy = (x4 + x5) // 2, (y4 + y5) // 2


        cv2.circle(img, (x4, y4), 10, (0, 255, 255), cv2.FILLED)
        cv2.circle(img, (x5, y5), 10, (0, 255, 255), cv2.FILLED)
        cv2.line(img, (x4, y4), (x5, y5), (0, 255, 255), 3)
        cv2.circle(img, (cx, cy), 10, (0, 255, 255), cv2.FILLED)

        # to find length of line
        length = math.hypot(x5 - x4, y5 - y4)
        print(length)

        #hand range = 50 - 250
        #volume range = -65 -0

        vol = np.interp(length, [20, 400], [maxVol, minVol])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (255, 255, 0), cv2.FILLED)





        #print(x1, y1, x2, y2)


        #3. check which finger are up
        fingers = detector.fingersUp()
        #print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        #4. only Index finger : Moving Mode
        if fingers[1]==1 and fingers[2]==0:
            # 5. convert coordinates
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))
            #6. smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            #7.Move Mouse
            autopy.mouse.move(wScr-clocX, clocY)
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        #8. BothIndex and  middle finger are up : clicking Modes
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print(length)
            # 10. click mouse if distance short
            if length < 30:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                #autopy.mouse.click()




    #11 frame rate
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    #12 display
    cv2.imshow("Image", img)
    cv2.waitKey(1)

