from flask import Flask, render_template, session, Response
from app import app
from user.models import User, Event
from bson import ObjectId
import cv2
from membercam import FaceRecognition_member
from tkinter import messagebox
import json
import webbrowser
import pymongo

myclient = pymongo.MongoClient("mongodb+srv://team17:TqZI3KaT56q6xwYZ@team17.ufycbtt.mongodb.net/")
mydb = myclient.test

global_name = None
result = 0

@app.route('/user/signup', methods=['POST'])
def signup():
    return User().signup()

@app.route('/user/signout')
def signout():
    return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
    return User().login()

@app.route('/user/update_user', methods=['POST'])
def update_user():
    return User().update_user()

@app.route('/user/update_user', methods=['POST'])
def update_user_route():
    user_obj = User()
    return user_obj.update_user()

@app.route("/admin", methods = ['GET'])
def get_all_member():
    #print("passed routes.py, reaching for User.get_all_member()")
    return User().get_all_member()

@app.route("/delete_member/<string:email>", methods = ['GET'])
def delete_member(email):
    #print("passed routes.py, reaching for User.get_all_member()")
    return User().delete_member(email)

@app.route("/get_member/<string:email>", methods = ['GET'])
def get_member(email):
    return User().get_member(email)

@app.route('/search', methods=['POST'])
def search():
    return  User().search()

@app.route('/event/<event_id>')
def event_details(event_id):
    return User().event_details(event_id)

@app.route("/add_event", methods = ['POST'])
def add_event():
    return Event().add_event()

@app.route("/eventlist", methods = ['GET'])
def get_all_event():
    return Event().get_all_event()

@app.route('/event/<event_id>/image')
def get_event_image(event_id):
    return Event().get_event_image(event_id)

@app.route("/delete_event/<string:title>", methods = ['GET'])
def delete_event(title):
    print("routes: delete event")
    return Event().delete_event(title)

@app.route("/get_event/<id>", methods = ['GET'])
def get_event(id):
    return Event().get_event(id)

@app.route('/ad_event/<event_id>')
def ad_event_details(event_id):
    return Event().ad_event_details(event_id)

@app.route('/modify_event/<event_id>', methods = ['GET','POST'])
def modify_details(event_id):
    return Event().modify_event(event_id)

@app.route('/event/<event_id>/ticket')
def event_ticket(event_id):
    return Event().event_ticket(event_id)

@app.route('/<event_id>/checkout', methods=['GET','POST'])
def checkout(event_id):
    return Event().checkout(event_id)

@app.route('/create_seat')
def create_seat():
    return Event().create_seat()

@app.route('/check_ticket_availability', methods=['GET'])
def check_ticket_availability():
    return Event().check_ticket_availability()

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    return Event().cancel_order()

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    return Event().update_order_status()

@app.route("/all_event", methods = ['GET'])
def all_event():
    return User().all_event()

@app.route('/membercam')
def membercam():
    user_json = session.get('user')  # Get user JSON from session
    user_data = json.loads(user_json)  # Parse JSON to dictionary
    name = user_data['name']
    print("這裡是setname")

    # 同時也設定全域變數 global_name
    global global_name
    global_name = name

    return render_template('membercam.html')

@app.route('/video_feed3')
def video_feed3():
    return Response(generate_frames_session(session), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames_session(session):
    fr = FaceRecognition_member()
    video_capture = cv2.VideoCapture(0)

    correct = 0
    fail = 0

    if not video_capture.isOpened():
        return 'Video source not found'
    count = 0

    while count < 5:
        ret, frame = video_capture.read()
        if not ret:
            break

        frame, recognized_name = fr.run_recognition(frame)
        recognized_name = recognized_name.split('(', 1)

        # 從 session 中獲取名字
        global session_name
        session_name = global_name
        print(session_name)
        print(recognized_name)
        # 比對辨識出來的名字和 session 中的名字是否一致
        if recognized_name[0] == session_name:
            print("辨識結果和 session 中的名字一致")
            #show_success_popup(session_name)
            correct += 1
            #return redirect(url_for('recognition_correct'))
            #flash("辨識結果和 session 中的名字一致", "success")
        else:
            print("辨識結果和 session 中的名字不一致")
            fail += 1
            #return redirect(url_for('recognition_fail.html'))
            #flash("辨識結果和 session 中的名字不一致", "error")

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        count += 1

    print(correct, fail)
    global result
    result = correct / (correct + fail)
    video_capture.release()


@app.route('/recognition_result')
def recognition_result():
    global result
    if result >= 0.75:
        print(result)
        #show_success_popup(session_name)
        return render_template('recognition_correct.html')
    elif result <0.75:
        print(result)
        #show_fail_popup(session_name)
        return render_template('recognition_fail.html')

@app.route('/recognition_correct', methods=['POST'])
def recognition_correct():
    user_json = session.get('user')
    user_data = json.loads(user_json)

    existing_order = mydb.orders.find_one({
        'user_name': user_data['name'],
        'order_status': 1
    },
        sort=[('order_created_at', pymongo.DESCENDING)])

    if existing_order:
        order_id = existing_order['order_id']

        # 在這裡添加更新訂單狀態的邏輯
        # 這是一個示例，你需要根據你的實際情況進行修改
        result = mydb.orders.update_one(
            {'order_id': order_id},
            {'$set': {'order_status': 2}}  # 將訂單狀態更改為 2，表示已確認驗證
        )

        if result.modified_count > 0:
            # 更新成功，返回成功的消息
            return render_template('recognition_correct.html')




@app.route('/recognition_fail')
def recognition_fail():
    print('成功進判斷式')
    print(result)
    return render_template('recognition_fail.html')

from flask import request, jsonify

@app.route('/confirm_verification', methods=['POST'])
def confirm_verification():
    return User.confirm_verification()


def show_success_popup(name):
    message = f"{name} 成功驗證為本人"
    messagebox.showinfo('Recognition Success', message)  # 訊息內容
    webbrowser.open('http://127.0.0.1:5000/recognition_correct')

def show_fail_popup(name):
    message = f"{name} 驗證失敗"
    messagebox.showwarning(title='Recognition Fail',  # 視窗標題
                        message=message)  # 訊息內容
    webbrowser.open('http://127.0.0.1:5000/recognition_fail')



