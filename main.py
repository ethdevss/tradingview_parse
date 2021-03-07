from websocket import create_connection
import json
import random
import string
import re
import pandas as pd
import csv
import mongoengine
from datetime import datetime


def filter_raw_message(text):
    try:
        found1 = re.search('"m":"(.+?)",', text).group(1)
        found2 = re.search('"p":(.+?"}"])}', text).group(1)
        print(found1)
        print(found2)
        return found1, found2
    except AttributeError:
        print("error")


def generateSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(stringLength))
    return "qs_" + random_string


def generateChartSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(stringLength))
    return "cs_" + random_string


def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st


def constructMessage(func, paramList):
    # json_mylist = json.dumps(mylist, separators=(',', ':'))
    return json.dumps({
        "m": func,
        "p": paramList
    }, separators=(',', ':'))


def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))


def sendRawMessage(ws, message):
    ws.send(prependHeader(message))


def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))


def generate_csv(a):
    out = re.search('"s":\[(.+?)\}\]', a).group(1)
    x = out.split(',{\"')

    with open('data_file.csv', mode='w', newline='') as data_file:
        employee_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        employee_writer.writerow(['index', 'date', 'open', 'high', 'low', 'close', 'volume'])

        for xi in x:
            xi = re.split('\[|:|,|\]', xi)
            print(xi)
            ind = int(xi[1])
            ts = datetime.fromtimestamp(float(xi[4])).strftime("%Y/%m/%d, %H:%M:%S")
            employee_writer.writerow([ind, ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])


def parse_message(message):
    pass


# Initialize the headers needed for the websocket connection
headers = json.dumps({
    # 'Connection': 'upgrade',
    # 'Host': 'data.tradingview.com',
    'Origin': 'https://data.tradingview.com'
    # 'Cache-Control': 'no-cache',
    # 'Upgrade': 'websocket',
    # 'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    # 'Sec-WebSocket-Key': '2C08Ri6FwFQw2p4198F/TA==',
    # 'Sec-WebSocket-Version': '13',
    # 'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
    # 'Pragma': 'no-cache',
    # 'Upgrade': 'websocket'
})

# Then create a connection to the tunnel
ws = create_connection(
    'wss://data.tradingview.com/socket.io/websocket', headers=headers)

session = generateSession()
print("session generated {}".format(session))

chart_session = generateChartSession()
print("chart_session generated {}".format(chart_session))

# Then send a message through the tunnel
sendMessage(ws, "set_auth_token", ["eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxNzgwNTEzNiwiZXhwIjoxNjE1MTQ5Mzk0LCJpYXQiOjE2MTUxMzQ5OTQsInBsYW4iOiIiLCJleHRfaG91cnMiOjEsInBlcm0iOiIiLCJzdHVkeV9wZXJtIjoiUFVCO1RRdk45MFBCbHpnUm5iYnA4UHFwRHBpRW1nUGQ4eU9mIiwibWF4X3N0dWRpZXMiOjMsIm1heF9mdW5kYW1lbnRhbHMiOjAsIm1heF9jaGFydHMiOjF9.YBGJO6Jqh33P1eDX0z4qXSAuDJmrH-P6FJ8xiCZGQMh8pR-tsKwbBE_blGEvbdFPa_r1fS3zjPiJrVf4Hf36C-4d0wmunk8U_YRdT9GCCjg3cyZwK9Z85R3Dk5OGazfs97f2pmyDkuQfH9VZ-53-ZAzLJ1UVzAEhpODyJGxM-Sc"])
sendMessage(ws, "chart_create_session", [chart_session, ""])
sendMessage(ws, "quote_create_session", [session])
sendMessage(ws, "quote_set_fields",
            [session, "ch", "chp", "current_session", "description", "local_description", "language", "exchange", "fractional", "is_tradable", "lp", "lp_time",
             "minmov", "minmove2", "original_name", "pricescale", "pro_name", "short_name", "type", "update_mode", "volume", "currency_code", "rchp", "rtc"])
sendMessage(ws, "quote_add_symbols", [session, "BINANCE:BTCUSDTPERP", {"flags": ['force_permission']}])
sendMessage(ws, "quote_fast_symbols", [session, "BINANCE:BTCUSDTPERP"])

# st='~m~140~m~{"m":"resolve_symbol","p":}'
# p1, p2 = filter_raw_message(st)
sendMessage(ws, "resolve_symbol", [chart_session, "symbol_1", "={\"symbol\":\"BINANCE:BTCUSDTPERP\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", "15", 300])
sendMessage(ws, "create_study", [chart_session,"st3","st1","s1","Script@tv-scripting-101!",{
  "text": "F+B+pbi4f+KcYX2xwKXT+g==_4rFFadnZVUwzEwvhDWV1F8Jz2Gr17cIwajdewcGELMF7HTcWk5CectzvxR8CvKfi4xPbsyBaOJn/mBZONMlGCKUKEYZN9mT+9GV+rAy6AcILWYGCWb8jNscw3oUlpFxT9wvDatEOX+zuBOf18r8s5YmbV2gaR7Ymf21rHkTqYayW24ZeuKhC50rrYniK3UMdlbdpJLxgCLSJoPAKESgl6OMhlX6EMRj4AxwPikYaY+ThKtR/DHcwSTG50o/oVe3O2bx7q7mqNd3NEilUz/oSC3fUQ4+pVNSSvzPoV+C3nLrRrGzq9Er4o5+KxI/xnj0MINFy2OQZdEjs2juG1qw00vngt8fbT92mgWLodP4mvo64BAhC6fNRba0C7cTmo+Eupr7qQFFp8beIF2AAiw4TbCfHQuXTfWdh+apVpey53+KNI+LrfP5zTV3Eq+Iuf+Sh4sEY//A8ONxzU6wtjkn7RaV2JAw4gZXhtSZe4r07/wwdB+GQ7EAFVZMmq/OecOqqdkos1A2SiEVyYU96TimocZ8OiA3PRiK8U05/aAupWFEI8A+zWEQ8plLTteyWuS0kfAxrQibQm79USOiDnSY2RrGJdxSvxjIbQxGkX3YKPEKKnJCRc3HQnTfFIovzn2C7f8e6pHnZIfyi7yXJTAyOGYTmRcKVv+XXaU83HzUMArdhWwTBOpV0WmozpZ8S0FeDIx3o7liKaaPaY+tVAO8fhPYxfcJA8YV1S+ao7jXR1xy2XTfzJOPGSID4367mG33/0tHTu504QwmRPKPwujdiPxuNaICij17B5rI=",
  "pineId": "PUB;TQvN90PBlzgRnbbp8PqpDpiEmgPd8yOf",
  "pineVersion": "1.0",
  "in_0": {
    "v": 22,
    "f": True,
    "t": "integer"
  },
  "in_1": {
    "v": 20,
    "f": True,
    "t": "integer"
  },
  "in_2": {
    "v": 2,
    "f": True,
    "t": "float"
  },
  "in_3": {
    "v": 50,
    "f": True,
    "t": "integer"
  },
  "in_4": {
    "v": 0.85,
    "f": True,
    "t": "float"
  },
  "in_5": {
    "v": 1.01,
    "f": True,
    "t": "float"
  },
  "in_6": {
    "v": False,
    "f": True,
    "t": "bool"
  },
  "in_7": {
    "v": False,
    "f": True,
    "t": "bool"
  }
}])


# Printing all the result
a = ""
while True:
    try:
        result = ws.recv()
        print(result)
        a = a + result + "\n"
    except Exception as e:
        print(e)
        break

generate_csv(a)
