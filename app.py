from flask import Flask, request, abort
import requests
from bs4 import BeautifulSoup
import sys
import time
import datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials as SAC

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('hSpzNVPF13Q+Z4QMtnLGFLjA8qA50qf6Ams1sxmpe7xgUdu6jN0KzzOtndsPxvhm/Ab0PuJrEHBCGr6rUPDqCWAwETowTgqnBSVJE43bKOGKytkgUQi2J4MZ6D++pXEyMwagUIZ2g/mpa3+ZfMlvVwdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('0f5d6c06d4e427e280edc315fcca4595')


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def google_sheet():	
	GDriveJSON = 'PythonUpload.json'
	GSpreadSheet = 'UploadByPython'
	WaitSecond = 10
	print('將資料記錄在試算表' ,GSpreadSheet , '每' ,WaitSecond ,'秒')
	print('按下 Ctrl-C中斷執行')
	count = 1
	while True:
		try:
			scope = ['https://spreadsheets.google.com/feeds',
					 'https://www.googleapis.com/auth/drive']
			key = SAC.from_json_keyfile_name(GDriveJSON, scope)
			gc = gspread.authorize(key)
			worksheet = gc.open(GSpreadSheet).sheet1
		except Exception as ex:
			return ex
			#print('無法連線Google試算表', ex)
			sys.exit(1)
		worksheet.append_row(( str(datetime.datetime.now()), count))
		count = count+1
		return '新增一列資料到試算表'
		#print('新增一列資料到試算表' ,GSpreadSheet)
		time.sleep(WaitSecond)


def news():
	res = requests.get("https://tw.appledaily.com/hot/daily")
	soup = BeautifulSoup(res.text,'html.parser')
	output = ""
	for i, line in enumerate(soup.select('.aht_board li a'),0):
		if i == 10 :
			break
		output += '{}\n{}\n\n'.format(line['title'], line['href'])
		#output += line['title'] + " " + "\n" + line['href'] + "\n\n"
	return output
	
	
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	
	if event.message.text == "新聞" :
		message = TextSendMessage(news())
		line_bot_api.reply_message(
			event.reply_token,
			message)
	elif event.message.text == "sheet" :
		message = TextSendMessage(google_sheet())
		line_bot_api.reply_message(
			event.reply_token,
			message)
	
	else : 
		message = TextSendMessage(text=event.message.text)
		#text=event.message.text
		line_bot_api.reply_message(
			event.reply_token,
			message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)	
	
	
