import os

from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction, CarouselTemplate, CarouselColumn, TemplateSendMessage
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
    def send_reply_message(reply_token, reply_msg, quickReply=None):
        repply = TextSendMessage(text=reply_msg, quick_reply=quickReply)
        try:
            line_bot_api.reply_message(reply_token, repply)
        except LineBotApiError as e:
            print(e)

    @staticmethod
    def makeQuickReplyTexts(texts):
        replyButtons = []
        for item in texts:
            act = MessageAction(item, item)
            replyButtons.append(QuickReplyButton(action=act))

        reply = QuickReply(items=replyButtons)
        return reply

    @staticmethod
    def makeCarouselElement(pictureURI:str, name:str, rating:int, reply_on_click: str = None):
        act = None
        if reply_on_click:
            act = MessageAction(text=reply_on_click)
        return CarouselColumn(title=name, thumbnail_image_url=pictureURI, text=("Raiting: " + str(rating)), default_action= act) 

    @staticmethod
    def sendCarousel(reply_token, elements: list):

        carousel = CarouselTemplate(elements)
        try:
            line_bot_api.reply_message(reply_token=reply_token,messages=carousel )
        except LineBotApiError  as e:
            print(e)

    def send_fsm_graph(self, reply_token):
        try:
            # for demo, hard coded image url, line api only support image over https
            line_bot_api.reply_message(reply_token, ImageSendMessage(
                original_content_url=FSM_GRAPH_URL, preview_image_url=FSM_GRAPH_URL))
        except LineBotApiError as e:
            print(e)


