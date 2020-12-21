from datetime import datetime

from transitions.extensions import GraphMachine

from helper import LineAPI


class TocMachine(GraphMachine):
    def __init__(self):
        self.sum = 0
        self.machine = GraphMachine(
            model=self,
            **{
                "states" : [
                    'init',
                    'options',
                    'question',
                    'summation',
                    'intermediate',
                    'graph',
                ],
                "transitions" : [
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
                "initial" : 'init',
                "auto_transitions" : False,
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
        LineAPI.send_reply_message(reply_token, f"[Question] Your problem is submitted at {datetime.now().__str__()}\n{text}")
        self.go_back_options(reply_token, text)

    def on_enter_summation(self, reply_token, text):
        LineAPI.send_reply_message(reply_token, "[Summation] Enter number to sum, if you reply non-digit number, you will be redirected to state: options")

    def on_enter_intermediate(self, reply_token, text):
        self.sum += int(text)
        LineAPI.send_reply_message(reply_token, f"[Intermediate] Summation value now is {self.sum}")
        self.go_back_summation(reply_token, text)

    def on_enter_graph(self, reply_token, text):
        TocMachine().get_graph().draw('fsm.png', prog='dot', format='png')
        LineAPI.send_fsm_graph(reply_token)
        self.go_back_options(reply_token, text)
