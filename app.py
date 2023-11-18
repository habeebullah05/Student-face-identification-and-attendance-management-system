from flask import Flask, render_template, Response, request, redirect, flash
import cv2
import os
import mysql.connector
import time
import faceFeatures

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
#     password="cAv2bwbDPS",
#     database="sql6630907"
# )

print(mydb)
print("Connected to:", mydb.get_server_info())
mycursor = mydb.cursor()

# make shots directory to save pics
try:
    os.mkdir('./shots')
except OSError as error:
    pass

global capture, switch, name
capture = 0
switch = 1

# instantiate flask app
app = Flask(__name__)
app.secret_key = "abc"
camera = cv2.VideoCapture(0)


def gen_frames():  # generate frame by frame from camera
    global capture
    while True:
        success, frame = camera.read()
        if success:
            if capture:
                capture = 0
                p = os.path.sep.join(["shots", f"{name}.png"])
                cv2.imwrite(p, frame)
                features_list = str(faceFeatures.user())
                print(features_list)
                sql = "INSERT INTO student (name, usn, email, password, features) VALUES (%s, %s, %s, %s, %s)"
                val = (name, usn, email, password, features_list)
                mycursor.execute(sql, val)

                mydb.commit()

                print(mycursor.rowcount, "record inserted.")

            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/teacherLogin', methods=['POST', "GET"])
def teacherLogin():
    if request.method == 'POST':
        if request.form.get('register'):
            return redirect('teacherRegister')

        elif request.form.get('login'):
            login_details = dict()
            login_id = request.form.get('id')
            login_password = request.form.get('password')

            sql = "SELECT teacher_id FROM teacher"
            mycursor.execute(sql)
            id_list = []
            result = mycursor.fetchall()
            for x in result:
                id_list.append(x[0])

            sql = "SELECT password FROM teacher"
            mycursor.execute(sql)
            password_list = []
            result = mycursor.fetchall()
            for x in result:
                password_list.append(x[0])

            for i in range(len(id_list)):
                login_details[id_list[i]] = password_list[i]

            while True:
                if login_id in id_list and login_password in password_list:
                    if login_details[login_id] == login_password:
                        sql = "select * from student"
                        mycursor.execute(sql)
                        data = mycursor.fetchall()
                        flash("you are successfuly logged in")
                        return render_template('table.html', value=data)
                    else:
                        flash("Invalid password")
                        return redirect('teacherLogin')
                else:
                    flash("Invalid details")
                    return redirect('teacherLogin')
    return render_template('TeacherLogin.html')


@app.route('/teacherRegister', methods=['POST', 'GET'])
def teacherRegister():
    if request.form.get('SubmitTeacher'):
        if request.method == 'POST':
            global name, id, email, password
            if request.form.get('SubmitTeacher'):
                name = request.form.get('name')
                id = request.form.get('id')
                email = request.form.get('email')
                password = request.form.get('password')
                while True:
                    conform_password = request.form.get('conform_password')
                    if conform_password == password:
                        sql = "INSERT INTO teacher (teacher_id, name, email, password) VALUES (%s, %s, %s, %s)"
                        val = (id, name, email, password)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        print(mycursor.rowcount, "record inserted.")
                        flash("Registered Sucessfully")
                        break
        return render_template('TeacherLogin.html')
    return render_template('TeacherRegister.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('register'):
            return redirect('register')

        elif request.form.get('login'):
            login_details = dict()
            login_usn = request.form.get('usn')
            login_password = request.form.get('password')
            print(login_usn, login_password)

            sql = "SELECT usn FROM student"
            mycursor.execute(sql)
            usn_list = []
            result = mycursor.fetchall()
            for x in result:
                usn_list.append(x[0])

            sql = "SELECT password FROM student"
            mycursor.execute(sql)
            password_list = []
            result = mycursor.fetchall()
            for x in result:
                password_list.append(x[0])

            for i in range(len(usn_list)):
                login_details[usn_list[i]] = password_list[i]

            while True:
                if login_usn in usn_list and login_password in password_list:
                    if login_details[login_usn] == login_password:
                        sql = f"select * from student where usn = '{login_usn}'"
                        mycursor.execute(sql)
                        data = mycursor.fetchall()
                        # print("this is data of student ++++++++++++++++++++")
                        # print(data.append(10))
                        flash("you are successfuly logged in")
                        return render_template('table.html', value=data)
                    else:
                        flash("Invalid Password")
                        return redirect('login')
                else:
                    flash("Invalid details")
                    return redirect('login')

    return render_template('student_login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        global name, usn, email, password
        if request.form.get('photo'):
            name = request.form.get('name')
            usn = request.form.get('usn')
            email = request.form.get('email')
            password = request.form.get('password')
            while True:
                conform_password = request.form.get('conform_password')
                if conform_password == password:
                    flash("Registered Sucessufully")
                    break
                else:
                    return redirect("register")
            return redirect('camera')
    return render_template('student_register.html')


@app.route('/camera')
def camera_capture():
    return render_template('camera.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests', methods=['POST', 'GET'])
def tasks():
    global switch, camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture = 1
            time.sleep(5)
            capture = 0
            switch = 0
            camera.release()
            cv2.destroyAllWindows()
            return render_template('student_login.html')
        elif request.form.get('stop') == 'Stop/Start':
            if switch == 1:
                switch = 0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(0)
                switch = 1

    elif request.method == 'GET':
        return render_template('camera.html')
    return render_template('camera.html')


# start Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

camera.release()
cv2.destroyAllWindows()
