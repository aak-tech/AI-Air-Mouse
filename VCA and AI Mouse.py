import cv2
import numpy as np
import HandTrackingModule as htm



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
area = 0
colorvol = (255, 0, 0)









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
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        # print(area)
        if 250 < area < 1000:
            print("yes")








        # for volume finger
        length2, img, VInfo = detector.volumeDistance(4, 8, img)
        print(length2)

        #hand range = 50 - 250
        #volume range = -65 -0

        vol = np.interp(length2, [20, 400], [maxVol, minVol])
        print(int(length2), vol)

        #smoothening
        smoothness = 2
        vol = smoothness * round(vol / smoothness)

        #if pinky finger up set the volume
        Vfingers = detector.fingersUp()
        if Vfingers[4]:
            volume.SetMasterVolumeLevel(vol, None)
            cv2.circle(img, (VInfo[4], VInfo[5]), 15, (255, 255, 0), cv2.FILLED)
            colorvol = (0, 0, 255)
            time.sleep(0.10)
        else:
            colorvol = (255, 0, 0)






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
                autopy.mouse.click()

    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorvol, 3)

    #11 frame rate
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    #12 display
    cv2.imshow("Image", img)
    cv2.waitKey(1)

