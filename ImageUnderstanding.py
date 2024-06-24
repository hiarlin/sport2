import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client

appid ="bdd3b9ad"#填写控制台中获取的 APPID 信息
api_secret = "YjhkNzM3YTgxYWJjM2IxMjczMDQ5NTYw"#填写控制台中获取的 APISecret 信息
api_key ="10cde6bd84868eab0f7e5633893c813d"#填写控制台中获取的 APIKey 信息
imagedata = open("img_1.png",'rb').read()



imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"#云端环境的服务地址
text =[{"role": "user", "content": str(base64.b64encode(imagedata), 'utf-8'), "content_type":"image"}]
text2 = None


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, imageunderstanding_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(imageunderstanding_url).netloc
        self.path = urlparse(imageunderstanding_url).path
        self.ImageUnderstanding_url = imageunderstanding_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.ImageUnderstanding_url + '?' + urlencode(v)
        #print(url)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws,one,two):
    print(" ")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, question= ws.question ))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    #print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content,end ="")
        global answer
        answer += content
        # print(1)
        if status == 2:
            ws.close()


def gen_params(appid, question):
    """
    通过appid和用户的提问来生成请参数
    """

    data = {
        "header": {
            "app_id": appid
        },
        "parameter": {
            "chat": {
                "domain": "image",
                "temperature": 0.5,
                "top_k": 4,
                "max_tokens": 2028,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
}

    return data


def main(question):

    wsParam = Ws_Param(appid, api_key, api_secret, imageunderstanding_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    #ws.imagedata = imagedata
    ws.question = question
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def getText(role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def getText2(role, content, text2):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text2.append(jsoncon)
    return text2


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    #print("text-content-tokens:", getlength(text[1:]))
    while (getlength(text[1:])> 8000):
        del text[1]
    return text

def setImage(imagedata2):
    global text2
    text2 =[{"role": "user", "content": imagedata2, "content_type":"image"}]

def getAnswer(input):
    global answer
    question = checklen(getText2("user",input, text2))
    answer = ""
    print("答:",end = "")
    main(question)
    getText2("assistant", answer, text2)
    return answer


if __name__ == '__main__':

    #text.clear
    while(1):
        Input = input("\n" +"问:")
        question = checklen(getText("user",Input))
        answer = ""
        print("答:",end = "")
        main(question)
        getText("assistant", answer)
        # print(str(text))

