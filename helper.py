import os

from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import ButtonsTemplate, TemplateSendMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction, CarouselTemplate, CarouselColumn, DatetimePickerAction, PostbackAction
from linebot.exceptions import LineBotApiError


load_dotenv()
FSM_GRAPH_URL = os.environ.get("FSM_GRAPH_URL")
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))


def webhook_parser(webhook):
    event = webhook["events"][0]
    reply_token = event["replyToken"]
    user_id = event["source"]["userId"]
    isDate = False
    if "message" in event.keys(): 
        message = event["message"]["text"]
    elif "postback" in event.keys(): 
        if "data" in event["postback"]:
            message = event["postback"]["data"]
        if "params" in event["postback"]:
            message = event["postback"]["params"]["datetime"]
            isDate = True
            
    return reply_token, user_id, message, isDate


class LineAPI:
    replyTkn = None
    messages = []

    @staticmethod
    def addMessage(reply_token, message):
        LineAPI.messages.append(message)
        LineAPI.replyTkn = reply_token
    
    @staticmethod
    def commitMessages():
        try:
            line_bot_api.reply_message(LineAPI.replyTkn, LineAPI.messages)
            LineAPI.messages.clear()
        except LineBotApiError as e:
            print(e)

    @staticmethod
    def send_reply_message(reply_token, reply_msg, quickReply=None):
        repply = TextSendMessage(text=reply_msg, quick_reply=quickReply)
        try:
            LineAPI.addMessage(reply_token, repply)
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
    def makeCarouselElement(pictureURI:str, text:str, label:str, trigger:str = "none"):
        act = None
        if trigger != "none":
            act = PostbackAction(data = trigger, label = label)
        else:
            act = PostbackAction(data= label, label = label)
        return CarouselColumn( thumbnail_image_url=pictureURI, text=text, default_action= act, actions=[act]) 

    @staticmethod
    def sendCarousel(reply_token, elements: list):

        carousel = CarouselTemplate(elements)
        try:
            LineAPI.addMessage(reply_token, TemplateSendMessage(alt_text = "Tutor Imabes", template = carousel) )
        except LineBotApiError  as e:
            print(e)
    
    @staticmethod
    def makeDatetimePickerAction(label:str):
        return DatetimePickerAction(label, "date","datetime")
    
    @staticmethod
    def sendButtons(reply_token, buttons: list = [], txt = ""):
        actions = []
        for button in buttons:
            if type(button) is str:
                actions.append(MessageAction(button,button))
            else:
                actions.append(button)
        template = ButtonsTemplate(txt,actions=actions)
        LineAPI.addMessage(reply_token, TemplateSendMessage("button menu", template))

    @staticmethod
    def sendImageWithURL(reply_token, url:str):
        message = ImageSendMessage(url,url)
        LineAPI.addMessage(reply_token, message)

    def send_fsm_graph(self, reply_token):
        try:
            # for demo, hard coded image url, line api only support image over https
            LineAPI.addMessage(reply_token, ImageSendMessage(
                original_content_url=FSM_GRAPH_URL, preview_image_url=FSM_GRAPH_URL))
        except LineBotApiError as e:
            print(e)


