from flask import Flask, send_from_directory, send_file
from app import app
from user.models import User, Event
from bson import ObjectId


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

@app.route('/buy')
def buy():
    return Event().buy()



