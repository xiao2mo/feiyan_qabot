import json
import requests
import falcon
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message, create_reply
from wechatpy import WeChatClient

from utils.base_function import save_voice

client = WeChatClient('wx77796abb5a66c716', '72188f7a5e3a95e8ece4856e47f2ec3a')
CHATBOT_URL = "http://localhost:5005/webhooks/rest/webhook"
VOICE_PATH = 'voices/'


class Connect(object):

    def on_get(self, req, resp):
        query_string = req.query_string
        query_list = query_string.split('&')
        b = {}
        for i in query_list:
            b[i.split('=')[0]] = i.split('=')[1]

        try:
            check_signature(
                token='chatbot', signature=b['signature'], timestamp=b['timestamp'], nonce=b['nonce'])
            resp.body = (b['echostr'])
        except InvalidSignatureException:
            pass
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        xml = req.stream.read()
        msg = parse_message(xml)
        if msg.type != 'text' and msg.type!= 'voice':
            return
        if msg.type == 'text':
            if "收到不支持的消息类型" in msg.content:
                return
            received_text = msg.content
        elif msg.type == 'voice':
            voice = client.media.download(msg.media_id)
            save_voice(voice.content, VOICE_PATH)
            received_text = msg.recognition
        data = {"sender": msg.source, "message": received_text}
        r = requests.post(CHATBOT_URL, data=json.dumps(data))
        reply = [one["text"] for one in json.loads(r.content)]
        answer = "\n".join(reply)
        if msg.type == 'text':
            text_reply = create_reply(answer, message=msg)
        elif msg.type == 'voice':
            text_reply = create_reply("问：{}\n\n答：{}".format(received_text, answer), message=msg)
        xml = text_reply.render()
        resp.body = (xml)
        resp.status = falcon.HTTP_200

app = falcon.API()
connect = Connect()
app.add_route('/connect', connect)
