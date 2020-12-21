import os

from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage
from linebot.exceptions import LineBotApiError


load_dotenv()
FSM_GRAPH_URL = os.environ.get("FSM_GRAPH_URL")
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))

def webhook_parser(webhook):
    event = webhook["events"][0]
    reply_token = event["replyToken"]
    user_id = event["source"]["userId"]
    message = event["message"]["text"]

    return reply_token, user_id, message


class LineAPI:
    @staticmethod
    def send_reply_message(reply_token, reply_msg):
        try:
            line_bot_api.reply_message(reply_token, TextSendMessage(text=reply_msg))
        except LineBotApiError as e:
            print(e)

    def send_fsm_graph(reply_token):
        try:
            # for demo, hard coded image url, line api only support image over https
            line_bot_api.reply_message(reply_token, ImageSendMessage(original_content_url=FSM_GRAPH_URL, preview_image_url=FSM_GRAPH_URL))
        except LineBotApiError as e:
            print(e)
