#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request
import json
import requests
import pymongo

CHATBOT_URL = "http://localhost:5005/webhooks/rest/webhook"
MONGO_HOST = "mongodb://127.0.0.1:27017/"

app = Flask(__name__)
mongo_client = pymongo.MongoClient(host=MONGO_HOST)
mongo_rasa = mongo_client.rasa.conversations

@app.route('/send', methods=['POST'])
def send_message():
    """ 处理单个消息
    @param sender(str): 发送者id
    @param message(str): 消息内容
    """
    sender = request.form.get("sender", None)
    message = request.form.get("message", None)
    if not sender or not message:
        err_msg = "缺少关键参数"
        return error_return(err_msg)
    data = {"sender": sender, "message": message}
    r = requests.post(CHATBOT_URL, data=json.dumps(data))
    reply = [one["text"] for one in json.loads(r.content)]
    data = {
        "sender": sender,
        "messages": reply
    }
    return data_return(data)

@app.route('/conversations/<sender>', methods=['GET'])
def get_conversation(sender):
    """ 根据用户id，获取对话内容
    @param sender(str): 用户id
    """
    conversation = mongo_rasa.find_one({"sender_id":sender})
    if not conversation:
        err_msg = "找不到该用户的对话"
        return error_return(err_msg)
    events = conversation["events"]
    messages = get_messages_from_events(events)
    data = {"conversation": messages}
    return data_return(data)

@app.route('/conversations', methods=['GET'])
def get_conversations_list():
    """ 获取对话列表
    """
    data = [{"sender": one["sender_id"]} for one in mongo_rasa.find()]
    return data_return(data)
 
def get_messages_from_events(events):
    """ 从events中提取消息
    """
    result = []
    for item in events:
        text = item.get("text", None)
        if not text:
            continue
        result.append({"message": text, "sender": item["event"]})
    return result

def error_return(err_msg):
    """ 错误信息统一返回函数
    """
    err_code = 1
    return {"code": err_code, "data": err_msg}

def data_return(data):
    """ 数据统一返回函数
    """
    code = 0
    return {"code": code, "data":data}

if __name__ == '__main__':
    app.run()