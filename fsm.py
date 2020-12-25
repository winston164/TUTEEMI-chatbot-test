from datetime import datetime

from transitions.extensions import GraphMachine

from helper import LineAPI 
from app import Tutor

class TocMachine(GraphMachine):
    def __init__(self):
        self.sum = 0
        self.machine = GraphMachine(
            model=self,
            **{
                "states": [
                    'init',
                    'options',
                    'question',
                    'summation',
                    'intermediate',
                    'graph',
                ],
                "transitions": [
                    {
                        'trigger': 'advance',
                        'source': 'init',
                        'dest': 'options',
                    },
                    {
                        'trigger': 'choose_options',
                        'source': 'options',
                        'dest': 'question',
                        'conditions': 'is_question'
                    },
                    {
                        'trigger': 'choose_options',
                        'source': 'options',
                        'dest': 'summation',
                        'conditions': 'is_summation'
                    },
                    {
                        'trigger': 'choose_options',
                        'source': 'options',
                        'dest': 'graph',
                        'conditions': 'is_graph'
                    },
                    {
                        'trigger': 'go_back_options',
                        'source': 'graph',
                        'dest': 'options',
                    },
                    {
                        'trigger': 'go_back_options',
                        'source': 'question',
                        'dest': 'options',
                    },
                    {
                        'trigger': 'enter_number',
                        'source': 'summation',
                        'dest': 'intermediate',
                        'conditions': 'is_num',
                    },
                    {
                        'trigger': 'enter_number',
                        'source': 'summation',
                        'dest': 'options',
                        'conditions': 'is_not_num',
                    },
                    {
                        'trigger': 'go_back_summation',
                        'source': 'intermediate',
                        'dest': 'summation',
                    },
                ],
                "initial": 'init',
                "auto_transitions": False,
            }
        )

    # conditions
    def is_question(self, reply_token, text):
        lines = text.splitlines()
        return lines and lines[0].strip().lower() == "toc"

    def is_summation(self, reply_token, text):
        return text == "2"

    def is_num(self, reply_token, text):
        try:
            int(text)
            return True
        except ValueError:
            return False

    def is_not_num(self, reply_token, text):
        try:
            int(text)
            return False
        except ValueError:
            return True

    def is_graph(self, reply_token, text):
        return text == "3"

    # states
    def on_enter_options(self, reply_token, text):
        options_str = (
            "[Options] This bot provides two functions\n" +
            "1. To ask question about the project, please write down and send your question in required format\n" +
            "   For instance:\n\n" +
            "       TOC\n" +
            "       姓名學號：\n" +
            "       系統環境：\n" +
            "       系統版本：\n" +
            "       套件版本：\n" +
            "       在哪一個步驟遇到的問題：\n" +
            "       詳述問題：\n" +
            "       完整的錯誤訊息：\n" +
            "       已經試過的解決方法：\n" +
            "       在這個問題上已經花費的時間：\n\n" +
            "   If the question you submitted is legal, I will reply a copy of your question.\n\n" +
            "2. Simple summation machine\n" +
            "   Just reply 2 to enter summation machine.\n\n" +
            "3. Show current chatbot fsm graph\n" +
            "   Just reply 3 to see fsm graph."
        )
        LineAPI.send_reply_message(reply_token, options_str)


    def on_enter_question(self, reply_token, text):
        LineAPI.send_reply_message(
            reply_token, f"[Question] Your problem is submitted at {datetime.now().__str__()}\n{text}")
        self.go_back_options(reply_token, text)

    def on_enter_summation(self, reply_token, text):
        LineAPI.send_reply_message(
            reply_token, "[Summation] Enter number to sum, if you reply non-digit number, you will be redirected to state: options")

    def on_enter_intermediate(self, reply_token, text):
        self.sum += int(text)
        LineAPI.send_reply_message(
            reply_token, f"[Intermediate] Summation value now is {self.sum}")
        self.go_back_summation(reply_token, text)

    def on_enter_graph(self, reply_token, text):
        TocMachine().get_graph().draw('fsm.png', prog='dot', format='png')
        LineAPI.send_fsm_graph(reply_token)
        self.go_back_options(reply_token, text)


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
            'rate_class'
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
            }

        ],
        "initial": 'main',
        "auto_transitions": False,
    }

    def __init__(self):
        self.machine = GraphMachine(model=self, **chatClientFSM.fsm_definition)
    
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
        "-My schedule\n" +
        "-Rate class\n" 
    )
 
    def on_enter_main(self, reply_token):
        quick_reply = LineAPI.makeQuickReplyTexts([
            'Prices',
            'Tutors',
            'Book class',
            'My schedule',
            'Rate class'
        ])
        LineAPI.send_reply_message(reply_token, main_menu_text, quickReply=quick_reply)
    
    price_text = (
        "Our current prices are as follows:\n" +
        "One class for 1000NTD\n" +
        "10 classes for 10000NTD\n" +
        "(Responses :\n" +
        "-Main\n" +
        "-Tutors\n" +
        ")\n" 
    )
    def on_enter_price(self, reply_token):
        quick_reply = LineAPI.makeQuickReplyTexts([
            'Tutors'
            'Main'
        ])
        LineAPI.send_reply_message(reply_token,reply_msg=price_text,quickReply=quick_reply)

    def on_enter_tutors_sample(self,reply_token):
        LineAPI.send_reply_message(reply_token, reply_msg="These are some of our tutors:")
        
        #Send carousel of 5 random tutors:
        Tutor.query()
        
        

if __name__ == '__main__':
    mach = chatClientFSM()
    mach.get_graph().draw('fsm_test.png', prog='dot', format='png')
