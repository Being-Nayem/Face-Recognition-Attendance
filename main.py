import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-e68e1-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "storageBucket": "faceattendancerealtime-e68e1.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.png")

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load the encoding file
print("Loading Encode file...")

file = open('encodings.p', 'rb')
encodeListKnownWithIDs = pickle.load(file)
file.close()

# estract the encodings and the Student IDs
encodeListKnown, studentsIDs = encodeListKnownWithIDs

print("Encode  file Loaded")
   
modeType = 0
counter = 0
id = -1
imgStudent = []
   
   
while True:
    success, img = cap.read()
    
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    faceCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    # print("Face Locations:", faceCurFrame)
    # print("Face Encodings:", encodesCurFrame)

    
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodesCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                # print(faceLoc)
                imgBackground = cvzone.cornerRect(imgBackground, (faceLoc[3] + 55, faceLoc[0] + 162, faceLoc[1] - faceLoc[3], faceLoc[2] - faceLoc[0]), 20, rt=0)
                # cv2.putText(imgBackground, studentsIDs[matchIndex], (faceLoc[3] + 55, faceLoc[0] + 162 - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                id = studentsIDs[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "LOADING", (275, 400))
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter !=0:
            
            if counter == 1:
                # Get the data
                studentInfo = db.reference(f'Students/{id}').get()
                # print(studentInfo)

                # Get the image from the storage
                blob = bucket.blob(f"Images/{id}.jpg")
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGR2RGB)   
                
                # Update the data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance'], "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now()-datetimeObject).total_seconds()
                # print(secondElapsed)
                if secondElapsed>=30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                else:
                    modeType=3
                    counter=0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                
            if modeType!=3:
            
                if 10<counter<=20:
                    modeType = 2
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    
                if counter<=10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.8, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.8, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['start_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.8, (100, 100, 100), 1)
                    
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    imgStudent_resized = cv2.resize(imgStudent, (216, 216))
                    imgBackground[175:175+216, 909:909+216] = imgStudent_resized
            
                counter += 1
                
                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo= []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    
    else:
        counter = 0
        modeType = 0

    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)