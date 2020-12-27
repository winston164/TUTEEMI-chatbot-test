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


from fsm import chatClientFSM

# Handle State Trigger
def handleTrigger(state, reply_token, user_id, text):
    print("Server Handling State : %s" % state)
    if state == "init":
        machines[user_id].advance(reply_token, text)
    if state == "options":
        machines[user_id].choose_options(reply_token, text)
    if state == "summation":
        machines[user_id].enter_number(reply_token, text)


def transitionState(reply_token, user_id, text):
    # get machine
    m = machines[user_id]
    # get state
    state = m.state

    # see possible state transitions
    triggers = m.machine.get_triggers(state)

    if text in triggers:
        m.trigger(text, reply_token)
    else:
        # TODO: loop back to current state
        m.trigger('to_' + state, reply_token)
        pass

# TODO: dictionary mapping user texts to trigger words
userText_to_trigger = {
    "more tutors": 're_sample',
    "book a class": 'schedule',
    "main":'main',
    "tutors": 'tutors',
    "prices": 'price_query',
    "book class": 'schedule',
    "this week": 'week',
    "more times": 're_sample',
    "log in": 'log_in',
    "go back": 'go_back'
}

@app.route('/', methods=['GET'])
def reply():
    return 'Hello, World!'

@app.route('/graphs/<path:path>')
def graph(path):
    return send_from_directory('graphs', path)


@app.route('/', methods=['POST'])
def receive():
    webhook = json.loads(request.data.decode("utf-8"))
    reply_token, user_id, message, isDate = webhook_parser(webhook)
    print(reply_token, user_id, message)

    if user_id not in machines:
        machines[user_id] = chatClientFSM()
        machines[user_id].lineId = user_id

    if message == 'SHOW_FSM':
        # machines[user_id].get_graph().draw('graphs/'+user_id +'.png', prog='dot', format='png')
        machines[user_id].send_fsm_graph(reply_token)
        return jsonify({})

    if machines[user_id].state == 'set_class':
        if message != 'Log in' :
            machines[user_id].userName = message
            message = 'name'
    
    if machines[user_id].state == 'registered_client':
        if message.isnumeric():
            current_client = Client.query.filter(Client.phone == message).first()
            if current_client : 
                machines[user_id].userName = current_client.name
                machines[user_id].phoneNumber = message
                message = 'log_success'

            else : 
                machines[user_id].to_registered_client(reply_token, True)
                return jsonify({})

    if machines[user_id].state == 'main':   
        if message.lower() == 'my schedule':
            client = Client.query.filter(Client.line_id == user_id).first()
            if client: message = 'registered'
            else: message = 'not_registered'

    if machines[user_id].state == 'query_schedule':
        if message.isnumeric():
            current_client = Client.query.filter(Client.phone == message).first()
            if current_client and current_client.line_id == user_id: 
                machines[user_id].userName = current_client.name
                machines[user_id].phoneNumber = message
                message = 'confirmed'
            
            else : 
                machines[user_id].to_query_schedule(reply_token, True)
                return jsonify({})           
                
       
                
    if machines[user_id].state == 'get_phone':
        if message.isnumeric():
            machines[user_id].phoneNumber = message
            message = 'phone'
        else:
            machines[user_id].to_get_phone(reply_token, True)
            return jsonify({})

    if 'SET_BOOKING' in message:
        machines[user_id].current_booking = Booking.query.get(int(message.split()[1]))
        message = 'set'

    # handleTrigger(machines[user_id].state, reply_token, user_id, message)
    message = message.lower()
    if message in userText_to_trigger.keys():
        message = userText_to_trigger[message]
    
    if isDate:
        date = datetime.fromisoformat(message)
        print(date)
        machines[user_id].dateQuery = date.replace(minute=0, second= 0)
        message = 'date'
    
    
    transitionState(reply_token=reply_token, user_id = user_id, text = message)
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
        posibleCopy = any( booking.tutor_id == Tutors[tutor_index].id and  booking.time.day == day and booking.time.hour == hour for booking in Bookings)
        while(posibleCopy):
            day = random.randrange(0,31)
            hour = random.randrange(9,19)
            tutor_index = random.randrange(0,len(Tutors) - 1)
            date = (today + timedelta(days=day)).replace(hour=hour)   
            print(posibleCopy)
            posibleCopy = any( booking.tutor_id == Tutors[tutor_index].id and  booking.time.day == day and booking.time.hour == hour for booking in Bookings)

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
