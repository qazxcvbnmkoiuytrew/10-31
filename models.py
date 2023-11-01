from flask import Flask, jsonify, request, render_template, session, redirect, Response, url_for, send_file, flash
import pymongo
import json
import re
from bson import json_util
from passlib.hash import pbkdf2_sha256
from bson.objectid import ObjectId
from gridfs import GridFS
import io

myclient = pymongo.MongoClient("mongodb+srv://team17:TqZI3KaT56q6xwYZ@team17.ufycbtt.mongodb.net/")
mydb = myclient.test
fs = GridFS(mydb)

class User:

    def start_session(self, user):
        del user['password']
        user_json = json_util.dumps(user)
        session['logged_in'] = True
        session['user'] = user_json
        session['name'] = user['name']
        return user_json

    def signup(self):

        if request.form.get('password') != request.form.get('password_confirm'):
            return jsonify({"error": "Confirm Password must match"}), 401

        user = {
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "phone": request.form.get('phone'),
            "address": request.form.get('address'),
            "gender": request.form.get('gender'),
            "birthday": request.form.get('birthday')
        }
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        user_json = json_util.dumps(user)

        if not mydb.users.find_one({"email": user['email']}):
            mydb.users.insert_one(user)
            return self.start_session(user)

        elif mydb.users.find_one({"email": user['email']}):
            return jsonify({"error": "email address already exist"}), 400

        else:
            return jsonify({"error": "something's wrong..."}), 400


    def signout(self):
        session.clear()
        return redirect('/')

    def login(self):
        print("login方法已啟動")
        user = mydb.users.find_one({
            "email": request.form.get('email')
        })

        if not user:
            return jsonify({"error": "email not found"}), 401

        elif not pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return jsonify({"error": "password incorrect"}), 401

        elif user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.start_session(user)

        return jsonify({"error": "Something's wrong..."}), 401
        # return jsonify({ "error": "Invalid" }), 401

    def update_user(self):
        user_json = session.get('user')  # Get user JSON from session
        user_data = json.loads(user_json)  # Parse JSON to dictionary
        user_email = user_data['email']

        if not user_email:
            return jsonify({"error": "Email not found in session"}), 400

        update_data = {
            "name": request.form.get('name'),
            "password": pbkdf2_sha256.encrypt(request.form.get('password')),
            "phone": request.form.get('phone'),
            "address": request.form.get('address'),
            "gender": request.form.get('gender'),
            "birthday": request.form.get('birthday')
        }
        for field in ['name', 'phone', 'address', 'gender', 'birthday']:
            new_value = request.form.get(field)
            if new_value:
                update_data[field] = new_value

        # Handle password separately to hash it before updating
        new_password = request.form.get('password')
        if new_password:
            update_data['password'] = pbkdf2_sha256.encrypt(new_password)

        if not update_data:
            return jsonify({"error": "No fields to update"}), 400

        # Update the user information
        result = mydb.users.update_one(
            {"email": user_email},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            # Fetch and return the updated user
            updated_user = mydb.users.find_one({"email": user_email})
            del updated_user['password']

            # Update the session with the new user data
            session['user'] = json_util.dumps(updated_user)

            return json_util.dumps(updated_user)

        return jsonify({"error": "Update failed"}), 400

    def get_all_member(self):
        try:
            members = mydb.users.find({}, {"name": 1, "email": 1})
            # print("passed models.py, reaching for db")
            return render_template('admin.html', members=members)
        except Exception as e:
            print("error in models.py")
            return json_util.dumps({'error': str(e)})

    def delete_member(self, email):
        try:
            # 使用你的数据库客户端对象来执行删除操作
            mydb.users.delete_one({"email": email})
            return redirect('/admin')
        except Exception as e:
            print("Error deleting member:", str(e))
            return {'error': str(e)}

    # 個別會員的資料
    def get_member(self, email):
        try:
            members = mydb.users.find({}, {"name": 1, "email": 1})

            try:
                member_info = mydb.users.find_one({"email": email}, {"_id": 0, "password": 0})
                # test_member_json = json_util.dumps(test_member)
                print(member_info)
                return render_template('admin.html', members=members, member_info=member_info)

            except Exception as e:
                print("Error (inside) get member info: ", str(e))
                return json_util.dumps({'error': str(e)})

        except Exception as e:
            print("Error (outside) get all member: ", str(e))
            return json_util.dumps({'error': str(e)})

    def search(self):
        if request.method == 'POST':
            keyword = request.form['keyword']
            # 使用正则表达式进行模糊搜索，查询多个字段
            regex = re.compile(f'.*{keyword}.*', re.IGNORECASE)

            # 使用 $or 运算符来构建查询条件，以同时搜索 "name" 和 "email" 字段
            query = {
                "$or": [
                    {"title": regex},  # 搜索 "name" 字段
                    {"description": regex}  # 搜索 "email" 字段
                ]
            }

            results = list(mydb.events.find(query))  # 将结果转换为列表
            return render_template('search.html', results=results)

    def event_details(self, event_id):
        # 使用 event_id 检索事件的详细信息，然后将详细信息传递给模板
        event = mydb.events.find_one({"_id": ObjectId(event_id)})  # 假设您的事件具有唯一的 _id
        return render_template('event.html', event=event)

class Event:
    def add_event(self):

        event = {
            "title": request.form.get('title'),
            "category": request.form.get('category'),
            "time": request.form.get('time'),
            "ticket_time": request.form.get('ticket_time'),
            "ticket_price": request.form.get('ticket_price'),
            "ticket_amount": request.form.get('ticket_amount'),
            "description": request.form.get('description'),
            "notices": request.form.get('notices')
        }

        # 保存事件到数据库
        if not mydb.events.find_one({"title": event['title']}):
            event_id = mydb.events.insert_one(event).inserted_id
            # 提取上传的文件
            photo = request.files.get('photo')
            if photo:

                # 使用事件的ID作为图片文件名
                photo_filename = f"{event_id}.jpg"
                try:
                    photo_id = fs.put(photo.read(), filename=photo_filename)
                    print(f"Photo saved with ID: {photo_id}")
                except Exception as e:
                    print(f"Error saving photo: {str(e)}")
            return jsonify({"success": "event added!"}), 200
        else:
            return jsonify({"error": "title already exists"}), 400

    def get_all_event(self):
        try:
            events = mydb.events.find({}, {"_id": 1, "title": 1, "time": 1, "category": 1})
            return render_template('eventlist.html', events=events)
        except Exception as e:
            print("Error getting all event")
            return json_util.dumps({'error': str(e)})

    def get_event_image(self, event_id):
        # 构建图片文件名
        image_filename = f"{event_id}.jpg"

        # 从GridFS中获取图片
        grid_out = fs.find_one({"filename": image_filename})

        if grid_out is not None:
            # 将图片发送给浏览器
            response = send_file(io.BytesIO(grid_out.read()), mimetype='image/jpeg', as_attachment=False)
            return response

        # 如果找不到图片，可以返回默认图片或其他适当的响应
        return "Image not found", 404

    def delete_event(self, title):
        try:
            mydb.events.delete_one({"title": title})
            return redirect('/eventlist')
        except Exception as e:
            print("Error deleting event:", str(e))
            return {'error': str(e)}

        # 個別活動的資料

    def get_event(self, id):
        try:
            events = mydb.events.find({}, {"_id": 0, "title": 1, "time": 1, "category": 1})

            try:
                # 根据id查找特定活动的信息
                event_info = mydb.events.find_one({"_id": ObjectId(id)}, {"_id": 0})
                print(event_info)
                return render_template('eventlist.html', events=events, event_info=event_info)

            except Exception as e:
                print("Error (inside) get event info: ", str(e))
                return json_util.dumps({'error': str(e)})

        except Exception as e:
            print("Error (outside) get all event: ", str(e))
            return json_util.dumps({'error': str(e)})

    def ad_event_details(self, event_id):
        # 使用 event_id 检索事件的详细信息，然后将详细信息传递给模板
        event = mydb.events.find_one({"_id": ObjectId(event_id)})  # 假设您的事件具有唯一的 _id
        return render_template('ad_event.html', event=event)

    def modify_event(self, event_id):
        if request.method == "POST":
            # 处理 POST 请求，更新活动信息
            new_title = request.form.get("title")
            new_time = request.form.get("time")
            # 还可以添加其他需要更新的字段

            # 进行数据库更新操作，假设你的数据库集合名称为 "events"
            result = mydb.events.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": {"title": new_title, "time": new_time}}
            )

            if result.modified_count > 0:
                # 更新成功，可以进行相应的操作，如重定向或显示成功消息
                flash("Event updated successfully", "success")
                return jsonify({"success": "event changed!"}), 200
            else:
                # 更新失败
                flash("Event update failed", "error")

        # 获取活动信息以在表单中显示
        event_info = mydb.events.find_one({"_id": ObjectId(event_id)})

        return render_template("modify_event.html", event=event_info)
