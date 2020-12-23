import os
import json

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory

from helper import LineAPI, webhook_parser
from fsm import TocMachine


load_dotenv()
app = Flask(__name__, static_url_path='')
machines = {}


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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host = '0.0.0.0', port = port)
