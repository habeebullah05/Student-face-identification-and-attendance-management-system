import pandas as pd
from datetime import datetime
import mysql.connector


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

mycursor = mydb.cursor()

print(mydb)

now = datetime.now()
date = now.strftime('%d-%m-%Y')
month = now.strftime('%B')

final_attendance = dict()


def calculate_attendance():
    attendance_data = pd.read_csv(f"Attendance_{month}.csv")
    print("this is attendance data+++++++++++++++")
    print(attendance_data)
    usns = attendance_data["USN"].to_list()
    for usn in usns:
        if usn not in final_attendance:
            final_attendance[usn] = 1
        else:
            final_attendance[usn] += 1
    print(final_attendance)

    for usn, no_classes in final_attendance.items():
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++)")
        print("my cousor row count")
        print(mycursor.rowcount)
        if mycursor.rowcount < 1:
            print('hello')
            sql = "update student SET no_classes =(%s) where usn =(%s)"
            val = (no_classes, usn)
            print(";;;;;;;;;;;;;;;;;;;;;;;;;;;")
            print(usn, no_classes)
            mycursor.execute(sql, val)
            mydb.commit()
        else:
            print("world")
            # sql = "INSERT INTO attendance (usn, no_classes) VALUES (%s, %s)"
            sql = "update student SET no_classes =(%s) where usn =(%s)"
            val = (no_classes, usn)
            print("::::::::::::::::::::::::::::::")
            print(usn, no_classes)
            mycursor.execute(sql, val)
            mydb.commit()
    print(mycursor.rowcount, "record inserted.")

