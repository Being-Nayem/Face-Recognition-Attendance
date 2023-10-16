import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-e68e1-default-rtdb.asia-southeast1.firebasedatabase.app/"
})



ref = db.reference('Students')

data = {
    "200217":
        {
            "name": "Nayem Sarwar",
            "major": "SWE",
            "start_year": 2022,
            "total_attendance": 6,
            "standing": "G",
            "year": 1,
            "last_attendance": "2023-10-16 10:00:00",
        },
        "321654":
        {
            "name": "Nadim Sarwar",
            "major": "EEE",
            "start_year": 2023,
            "total_attendance": 6,
            "standing": "G",
            "year": 1,
            "last_attendance": "2023-10-16 10:00:00",
        },
        "852741":
        {
            "name": "Antar Chandra",
            "major": "CSE",
            "start_year": 2021,
            "total_attendance": 6,
            "standing": "G",
            "year": 2,
            "last_attendance": "2023-10-16 10:00:00",
        },
        "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "start_year": 1976,
            "total_attendance": 6,
            "standing": "G",
            "year": 4,
            "last_attendance": "2023-10-16 10:00:00",
        },
}

for key, value in data.items():
    ref.child(key).set(value)
    print("Data added successfully") 