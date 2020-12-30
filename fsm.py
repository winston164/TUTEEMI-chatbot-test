from datetime import datetime, timedelta

from transitions.extensions import GraphMachine
import random

from helper import LineAPI
from timetreeapi import getAccessToken, create_event


class chatClientFSM(object):
    """
    docstring
    """
    fsm_definition = {
        "states": [
            'main',
            'price',
            'tutors_sample',
            'schedule_class',
            'sample_week',
            'available_tutors',
            'set_class',
            'get_phone',
            'confirm_data',
            'book_class',
            'query_schedule',
            'show_schedule',
            'registered_client',
            'not_user'
            'all_bookings'
        ],

        "transitions": [
            {
                'trigger': 'price_query',
                'source': 'main',
                'dest': 'price'
            },
            {
                'trigger': 'tutors',
                'source': 'price',
                'dest': 'tutors_sample'
            },
            {
                'trigger': 're_sample',
                'source': 'tutors_sample',
                'dest': 'tutors_sample'
            },
            {
                'trigger': 'tutors',
                'source': 'main',
                'dest': 'tutors_sample'
            },
            {
                'trigger': 'schedule',
                'source': 'tutors_sample',
                'dest': 'schedule_class'
            },
            {
                'trigger': 'week',
                'source': 'schedule_class',
                'dest': 'sample_week'
            },
            {
                'trigger': 'date',
                'source': 'schedule_class',
                'dest': 'available_tutors'
            },
            {
                'trigger': 're_sample',
                'source': 'sample_week',
                'dest': 'sample_week'
            },
            {
                'trigger': 'set',
                'source': 'sample_week',
                'dest': 'set_class'
            },
            {
                'trigger': 'date',
                'source': 'sample_week',
                'dest': 'available_tutors'
            },
            {
                'trigger': 're_sample',
                'source': 'available_tutors',
                'dest': 'available_tutors'
            },
            {
                'trigger': 'date',
                'source': 'available_tutors',
                'dest': 'available_tutors'
            },
            {
                'trigger': 'set',
                'source': 'available_tutors',
                'dest': 'set_class'
            },
            {
                'trigger': 'name',
                'source': 'set_class',
                'dest': 'get_phone'
            },
            {
                'trigger': 'not_phone',
                'source': 'get_phone',
                'dest': 'get_phone'
            },
            {
                'trigger': 'phone',
                'source': 'get_phone',
                'dest': 'confirm_data'
            },
            {
                'trigger': 'no',
                'source': 'confirm_data',
                'dest': 'set_class'
            },
            {
                'trigger': 'yes',
                'source': 'confirm_data',
                'dest': 'book_class'
            },
            {
                'trigger': 'main',
                'source': '*',
                'dest': 'main'
            },
            {
                'trigger': 'schedule',
                'source': 'main',
                'dest': 'schedule_class'
            },
            {
                'trigger': 'log_in',
                'source': 'set_class',
                'dest': 'registered_client'
            },
            {
                'trigger': 'log_success',
                'source': 'registered_client',
                'dest': 'confirm_data'
            },
            {
                'trigger': 'log_failed',
                'source': 'registered_client',
                'dest': 'registered_client'
            },
            {
                'trigger': 'go_back',
                'source': 'registered_client',
                'dest': 'set_class'
            },
            {
                'trigger': 'registered',
                'source': 'main',
                'dest': 'query_schedule'
            },
            {
                'trigger': 'not_registered',
                'source': 'main',
                'dest': 'not_user'
            },
            {
                'trigger': 'confirmed',
                'source': 'query_schedule',
                'dest': 'show_schedule'
            },
            {
                'trigger': 'all_schedule',
                'source': 'main',
                'dest': 'all_bookings'
            }
        ],
        "initial": 'main',
    }

    def __init__(self):
        self.machine = GraphMachine(model=self, **chatClientFSM.fsm_definition)
        self.dateQuery = datetime.utcnow()
        self.current_booking = None
        self.userName = ""
        self.phoneNumber = ""
        self.lineId = ""

    main_menu_text = (
        "Welcome to TUTEEMI booking system!\n" +
        "How may we serve you today?\n" +
        "You can always go back to this menu by writing 'Main' \n" +
        "in as your answer\n" +
        "(Please write any of the following options)\n" +
        "Main\n" +
        "-Prices\n"
        "-Tutors\n" +
        "-Book class\n" +
        "-My schedule\n"
    )

    def on_enter_main(self, reply_token):
        quick_reply = LineAPI.makeQuickReplyTexts([
            'Prices',
            'Tutors',
            'Book class',
            'My schedule'
        ])
        LineAPI.send_reply_message(
            reply_token, chatClientFSM.main_menu_text, quickReply=quick_reply)
        LineAPI.commitMessages()

    price_text = (
        "Our current prices are as follows:\n" +
        "One class for 1000NTD\n" +
        "Sample class 500NTD\n" +
        "(Responses :\n" +
        "-Main\n" +
        "-Tutors\n" +
        ")\n"
    )

    def on_enter_price(self, reply_token):
        quick_reply = LineAPI.makeQuickReplyTexts([
            'Tutors',
            'Main'
        ])
        LineAPI.send_reply_message(
            reply_token, reply_msg=chatClientFSM.price_text, quickReply=quick_reply)
        LineAPI.commitMessages()

    def on_enter_tutors_sample(self, reply_token):
        from app import Tutor
        LineAPI.send_reply_message(
            reply_token, reply_msg="These are some of our tutors:")

        # Send carousel of 5 random tutors:
        tutor_profiles = Tutor.query.all()
        tutor_profiles = random.sample(tutor_profiles, 5)
        elements = [LineAPI.makeCarouselElement(tutor.picture, tutor.name, ('Rating: ' + str(tutor.rating)))
                    for tutor
                    in tutor_profiles]
        LineAPI.sendCarousel(reply_token, elements)

        quick_reply = LineAPI.makeQuickReplyTexts([
            'More Tutors',
            'Book a class',
            'Main'
        ])
        LineAPI.send_reply_message(
            reply_token, reply_msg="Time to book a class?", quickReply=quick_reply)
        LineAPI.commitMessages()

    schedule_class_text = {
        "Great! Do you want a class this week?\n" +
        "Or maybe you want to pick some specific date?\n"
    }

    def on_enter_schedule_class(self, reply_token):
        datePicker = LineAPI.makeDatetimePickerAction("Pick a date")
        LineAPI.sendButtons(
            reply_token,
            [datePicker, "This week"],
            'When do you want your class?'
        )
        LineAPI.commitMessages()

    def on_enter_sample_week(self, reply_token):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        plusOneWeek = today + timedelta(days=7)
        from app import Booking
        availableBookings = Booking.query.filter(today < Booking.time).filter(
            Booking.time < plusOneWeek).filter(Booking.available).all()
        availableBookings = random.sample(availableBookings, 5 if len(
            availableBookings) > 5 else (len(availableBookings) - 1))
        elements = []
        for booking in availableBookings:
            elements.append(LineAPI.makeCarouselElement(
                booking.tutor.picture,
                f"Tutor {booking.tutor.name} \nDate (MM/DD):{booking.time.month}/{booking.time.day} \nTime: {booking.time.hour}:00",
                "Schedule now",
                f"SET_BOOKING {booking.id}"
            ))

        if len(elements) > 0:
            LineAPI.sendCarousel(reply_token=reply_token, elements=elements)
        else:
            LineAPI.send_reply_message(
                reply_token, "Sorry, no tutors available at the moment")
        LineAPI.sendButtons(reply_token, [
            LineAPI.makeDatetimePickerAction("Pick a date"),
            'More times',
            'Main'
        ], 'More Options:')
        LineAPI.commitMessages()

    def on_enter_available_tutors(self, reply_token):
        from app import Booking
        fromTime = self.dateQuery - timedelta(hours=3)
        toTime = self.dateQuery + timedelta(hours=3)
        availableBookings = Booking.query.filter(fromTime < Booking.time).filter(
            Booking.time < toTime).filter(Booking.available).order_by(Booking.time).all()
        availableBookings = availableBookings[0:(5 if len(
            availableBookings) > 5 else len(availableBookings))]
        elements = []
        for booking in availableBookings:
            elements.append(LineAPI.makeCarouselElement(
                booking.tutor.picture,
                f"Tutor {booking.tutor.name} \nDate (MM/DD):{booking.time.month}/{booking.time.day} \nTime: {booking.time.hour}:00",
                "Schedule now",
                f"SET_BOOKING {booking.id}"
            ))
        if len(elements) > 0:
            LineAPI.sendCarousel(reply_token=reply_token, elements=elements)
        else:
            LineAPI.send_reply_message(
                reply_token, "Sorry, no tutors available at the moment")
        LineAPI.sendButtons(reply_token, [
            LineAPI.makeDatetimePickerAction("Pick other date"),
            'Main'
        ], 'More Options:')
        LineAPI.commitMessages()

    def on_enter_set_class(self, reply_token):
        LineAPI.send_reply_message(reply_token,
                                   "Great, now we just need some info to book your " +
                                   "personal class with one of our best tutors!")
        LineAPI.sendButtons(reply_token, ['Log in'], 'Booked a class before?')

        LineAPI.send_reply_message(
            reply_token, "How do we call you? (Write your name please)")
        LineAPI.commitMessages()

    def on_enter_get_phone(self, reply_token, invalid: bool = False):
        if invalid:
            LineAPI.send_reply_message(
                reply_token, "How do we contact you? (Please insert a valid phone number")
        else:
            LineAPI.send_reply_message(
                reply_token, "How do we contact you? (Please insert your phone number")
        LineAPI.commitMessages()

    def on_enter_registered_client(self, reply_token, repeated: bool = False):
        if repeated:
            LineAPI.send_reply_message(
                reply_token, '(Wrong input or not registered before)')
        LineAPI.send_reply_message(reply_token, 'Please write your phone number',
                                   LineAPI.makeQuickReplyTexts([
                                       'go back'
                                   ]))
        LineAPI.commitMessages()
        pass

    def on_enter_confirm_data(self, reply_token):
        LineAPI.send_reply_message(reply_token,
                                   "You've entered the following contact info: \n" +
                                   f"Name: {self.userName} \n" +
                                   f"Phone number: {self.phoneNumber}"
                                   )
        qr = LineAPI.makeQuickReplyTexts([
            "Yes",
            "No"
        ])
        LineAPI.send_reply_message(reply_token, "Is this correct?", qr)
        LineAPI.commitMessages()

    def on_enter_query_schedule(self, reply_token, reEntering: bool = False):
        from app import Client
        client = Client.query.filter(Client.line_id == self.lineId).first()
        LineAPI.send_reply_message(reply_token,
                                   f"Hi {client.name}, to confirm your identity please input your phone number."
                                   )
        if reEntering : LineAPI.send_reply_message(reply_token, "(Wrong number)")
        LineAPI.commitMessages()
    
    def on_enter_show_schedule(self,reply_token):
        from app import Client
        client = Client.query.filter(Client.line_id == self.lineId).first()
        message = ""
        bookings = client.bookings
        for booking in bookings:
            message = message + f"Class with tutor {booking.tutor.name} at {booking.time.hour}:00  on the {booking.time.month}/{booking.time.day}.\n"
        LineAPI.send_reply_message(reply_token, message, LineAPI.makeQuickReplyTexts([
            'Main'
        ]))
        LineAPI.commitMessages()

    def on_enter_not_user(self, reply_token):
        LineAPI.send_reply_message(reply_token, "Sorry you're not a user yet, book a class to become a registered user",
        LineAPI.makeQuickReplyTexts([
            'Main'
        ]))
    
    def on_enter_book_class(self, reply_token):
        # TODO: Add booking logic
        # Add client to the database table
        from app import Client, Booking, db
        client = Client.query.filter(Client.line_id == self.lineId).first()
        if not client:
            client = Client(line_id=self.lineId, name=self.userName,
                            phone=self.phoneNumber)
        db.session.add(client)
        db.session.commit()

        booking = Booking.query.get(self.current_booking.id)

        booking.client_id = client.id
        booking.available = False
        db.session.commit()

        # Send event to TimeTree
        token = getAccessToken("250",
                               booking.tutor.timetree_id)
        print(token)
        res = create_event(token,
                           f"{booking.tutor.name}'s class with {client.name}",
                           booking.time,
                           (booking.time + timedelta(hours=1)),
                           f"Scheduled class with {client.name}\n" +
                           "Contact info: \n" +
                           f"Phone number: {client.phone}")
        print(res)

        # Send response to Client
        LineAPI.send_reply_message(reply_token,
                                   "Thanks for trusting us with your learning. \n" +
                                   f"{booking.tutor.name} will soon " +
                                   "be contacting you for setting up the meeting. \n" +
                                   "Have a nice day.",
                                   LineAPI.makeQuickReplyTexts([
                                       'Main'
                                   ]))
        LineAPI.commitMessages()

    def on_enter_all_bookings(self, reply_token):
        from app import Booking
        bookings = Booking.query.all()
        message = ""
        for i, booking in enumerate(bookings):
            if i < 10:
                message = (message + 
                    f"Booking id: {booking.id}, tutor {booking.tutor.name} with {booking.client.name}\n")
        LineAPI.send_reply_message(reply_token,message)
        LineAPI.commitMessages()

    def send_fsm_graph(self, reply_token):
        LineAPI.sendImageWithURL(reply_token, "https://tuteemi-test.herokuapp.com/graphs/Ucb9b7f4e1986ecc6e013bd1b6f314293.png")
        LineAPI.commitMessages()



if __name__ == '__main__':
    mach = chatClientFSM()
    mach.get_graph().draw('fsm_test.png', prog='dot', format='png')
