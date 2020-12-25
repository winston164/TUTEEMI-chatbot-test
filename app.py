import os
import json

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random

from helper import LineAPI, webhook_parser


load_dotenv()
app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'rUfXKmJWJA8555vm9KiPn3UOlL42FNjz')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
machines = {}

# Database declaration
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.String(50))
    name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False) # default=''
    bookings = db.relationship('Booking', backref='client', lazy=True)
    
    def __repr__(self):
        return f"Client('{self.name}', '{self.phone}')"

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timetree_id = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    picture = db.Column(db.String(100), unique=True)
    rating = db.Column(db.Integer)
    bookings = db.relationship('Booking', backref='tutor', lazy=True)

    def __repr__(self):
        return f"Tutor('{self.name}', '{self.rating}')"

    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable = False)
    tutor_id = db.Column(db.Integer,db.ForeignKey('tutor.id'), nullable = False)
    available = db.Column(db.Boolean, default=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))

    
    def __repr__(self):
        return f"Booking(tutor:'{self.tutor.name}', time:'{self.time}', '{'available' if self.available else 'booked' }' , client:'{self.client if self.client else ''}')"


from fsm import TocMachine

# Handle State Trigger
def handleTrigger(state, reply_token, user_id, text):
    print("Server Handling State : %s" % state)
    if state == "init":
        machines[user_id].advance(reply_token, text)
    if state == "options":
        machines[user_id].choose_options(reply_token, text)
    if state == "summation":
        machines[user_id].enter_number(reply_token, text)

@app.route('/', methods=['GET'])
def reply():
    return 'Hello, World!'


@app.route('/', methods=['POST'])
def receive():
    webhook = json.loads(request.data.decode("utf-8"))
    reply_token, user_id, message = webhook_parser(webhook)
    print(reply_token, user_id, message)

    if user_id not in machines:
        machines[user_id] = TocMachine()

    handleTrigger(machines[user_id].state, reply_token, user_id, message)
    return jsonify({})

@app.route('/timetreewebhook', methods=['POST'])
def timetreewebhook():
    webhook = json.loads(request.data.decode("utf-8"))
    print(webhook)
    return 'ok'



def populateDB():
    Tutors = []
    Clients = []
    Bookings = []

    db.create_all()

    Tutors.append(Tutor(
        name = 'Gabby', 
        picture='https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Gabby-e1600158148501.jpg',
        timetree_id = '9345',
        rating = 5,
        ))
    Tutors.append(Tutor(
        name = 'Roberto',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Roberto-e1600158347600.jpg',
        timetree_id = '9345',
        rating = 4
    ))
    Tutors.append(Tutor(
        name = 'Jorah',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Jorah-e1600158201256.jpg',
        timetree_id = '9345',
        rating = 5
    ))
    Tutors.append(Tutor(
        name = 'Karla',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Karla-e1600158232888.jpg',
        timetree_id = '9345',
        rating = 4
    ))
    Tutors.append(Tutor(
        name = 'Cynthia',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Cynthia-e1600158110336.jpg',
        timetree_id = '9345',
        rating = 5
    ))
    Tutors.append(Tutor(
        name = 'Alex',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Alex-scaled-e1600157952725.jpg',
        timetree_id = '9345',
        rating = 4
    ))
    Tutors.append(Tutor(
        name = 'Lana',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Lana-e1600158260172.jpg',
        timetree_id = '9345',
        rating = 5
    ))
    Tutors.append(Tutor(
        name = 'Sebastian',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Sebastian-e1600158440326.jpg',
        timetree_id = '9345',
        rating = 5
    ))
    Tutors.append(Tutor(
        name = 'Stephanie',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/09/TUTEEMI-Stephanie-scaled-e1600158513277.jpg',
        timetree_id = '9345',
        rating = 5
    ))
    Tutors.append(Tutor(
        name = 'Vincent',
        picture = 'https://tuteemi.com/wp-content/uploads/2020/10/Vincent-e1603093229621.jpg',
        timetree_id = '9345',
        rating = 4
    ))

    for tut in Tutors:
        db.session.add(tut)
    #Create 50 unique random times in the following month
    
    db.session.commit()
    
    today = datetime.utcnow().replace(minute=0,second=0,microsecond=0,hour=0)
    random.seed(int(datetime.utcnow().timestamp()))
    for i in range(150):
        day = random.randrange(0,31)
        hour = random.randrange(9,19)
        tutor_index = random.randrange(0,len(Tutors) - 1)
        date = (today + timedelta(days=day)).replace(hour=hour)
        Bookings.append(Booking(
           time = date,
           tutor_id = Tutors[tutor_index].id 
        ))
        pass
    
    for booking in Bookings:
        db.session.add(booking)

    db.session.commit() 
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host = '0.0.0.0', port = port)
