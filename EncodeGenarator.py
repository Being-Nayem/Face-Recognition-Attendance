import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-e68e1-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "storageBucket": "faceattendancerealtime-e68e1.appspot.com"
})



# Importing the studens images
folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentIDs = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIDs.append(os.path.splitext(path)[0])
    
    filename = f"{folderPath}/{path}"
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
    

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        # convert the color to encode
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # encode the image
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIDs = [encodeListKnown, studentIDs]
print("Encoding Completed")

file = open('encodings.p', 'wb')
pickle.dump(encodeListKnownWithIDs, file)
file.close()
print("Encoding Saved")