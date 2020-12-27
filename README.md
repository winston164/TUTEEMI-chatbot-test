# TUTTEMI booking chatbot

Tuteemi is a company dedicated to booking bilingual tutors with users.

## Features
Some of the features are:
* Find out more about prices and tutors
* Book a class with a tutor in the following week or a specific date
* Look at your schedule

## Graph 
The finite state machine looks as follows:
![FSM Graph](https://tuteemi-test.herokuapp.com/graphs/Ucb9b7f4e1986ecc6e013bd1b6f314293.png)

## How to start
1. Make a .env file in the base directory with the following variables
    * LINE_CHANNEL_ACCESS_TOKEN= (your line access token from line console)
    * LINE_CHANNEL_SECRET= (your line channel secret from line console)
    * FLASK_ENV=development
    * SECRET_KEY=(secret key for your database, any random key is ok)
2. Install graphviz on your system 
3. Install requirements with "pip install -r requirtements.txt"
4. Use populateDB funciton in app to populate the database with dummy data
5. Download and use ngrok to tunnel port 5000
6. Run "python app.py"



## Author
Winston Bendana