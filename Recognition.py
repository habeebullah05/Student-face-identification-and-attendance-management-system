import time
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import mysql.connector

import attendance_calcualte

students = dict()

mydb = mysql.connector.connect(
    host="sql12.freesqldatabase.com",
    port=3306,
    user="sql12646209",
    password="cAv2bwbDPS",
    database="sql12646209"
)

# mydb = mysql.connector.connect(
#     host="sql6.freesqldatabase.com",
#     port=3306,
#     user="sql6630907",
#     password="g43S5mAz1Z",
#     database="sql6630907"
# )

print(mydb)

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM student")
myresult = mycursor.fetchall()
print(myresult)


def convert_float(char_list):
    char_number = ""
    en_list = []
    for word in char_list:
        for letter in word:
            if letter == "[" or letter == "]":
                continue
            else:
                char_number += letter
        number = float(char_number)
        en_list.append(number)
        char_number = ""
    return en_list



for x in myresult:
    print(x)
    print(len(x))
    print(x[4].split())
    print(len(x[4].split()))
    # print("+++++++++==========tis is break")
    # break
    encoded_list = convert_float(x[4].split())
    students[x[1]] = encoded_list

classNames = []
encodeListKnown = []
for key, value in students.items():
    classNames.append(key)
    encodeListKnown.append(value)


def markAttendance(name):
    now = datetime.now()
    date = now.strftime('%d-%m-%Y')
    month = now.strftime('%B')
    with open(f'Attendance_{month}.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            print("_______________this is line------------------")
            print(line)
            entry = line.split(',')
            nameList.append(entry[1])
            print("==========this is name list=================")
            print(nameList)
        if name not in nameList:
            time = now.strftime('%H:%M:%S')
            f.writelines(f'\n{date},{name},{time}, P')





cap = cv2.VideoCapture(0)
months = []
now = datetime.now()
month = now.strftime('%B')
if month not in months:
    print("month executed")
    months.append(month)
    with open(f'Attendance_{month}.csv', 'w') as f:
        f.writelines("Date,USN,Time,Attendance")
    if len(months) == 12:
        months = []
i = 0
while True:
    success, img = cap.read()
    # img = captureScreen()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name)

    cv2.imshow('Webcam', img)
    time.sleep(2)
    i += 1
    if i == 5:
        cv2.destroyAllWindows()
        attendance_calcualte.calculate_attendance()
        time.sleep(5)
        i = 0
    cv2.waitKey(1)
