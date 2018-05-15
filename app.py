from oauth2client.service_account import ServiceAccountCredentials as SAC
from flask import Flask, request, abort
from bs4 import BeautifulSoup
import re
import requests
import sys
import gspread

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
line_bot_api = LineBotApi('')
# Channel Secret
handler = WebhookHandler('')


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

#輸入文字分析,目前針對新聞功能
#回傳數量(quantity)、主題(theme)、目的(target) 
def text_analysis(str1):
	output = {'quantity':10, 'theme':"", 'target':""}
	
	#從數字後一位開始分析
	nstr = re.sub("[^0-9]", "", str1)            #挑出數字
	if nstr != '':
		output['quantity'] = nstr
	begin_tag = str1.index(nstr) + len(nstr)     #查找起始位置
	arr = get_gsheet('UploadByPython')
	
	#從詞彙庫尋找關鍵字
	for i in range(begin_tag, len(str1)):        
		target = str1[i-1]+str1[i]
			
		for j in range(len(arr)):
			try :
				a = arr[j].index(target)
				output[arr[j][0]] = arr[j][a]
			except ValueError:
				continue
	return output
	
def get_gsheet(sname):
	GDriveJSON = 'PythonUpload.json'
	GSpreadSheet = sname
	#開啟google sheet
	try:
		scope = ['https://spreadsheets.google.com/feeds',
				 'https://www.googleapis.com/auth/drive']
		key = SAC.from_json_keyfile_name(GDriveJSON, scope)
		gc = gspread.authorize(key)
		worksheet = gc.open(GSpreadSheet).sheet1
	except Exception as ex:
		print('無法連線Google試算表', ex)
		sys.exit(1)
	
	return worksheet.get_all_values()


def news( num , th = "" ):
	
	res = requests.get("https://tw.appledaily.com/hot/daily")
	soup = BeautifulSoup(res.text,'html.parser')
	output = ""
	for i, line in enumerate(soup.select('.aht_board li a'),0):
		if i == num :
			break
		output += '{}\n{}\n\n'.format(line['title'], line['href'])
		#output += line['title'] + " " + "\n" + line['href'] + "\n\n"
	return output
	
	
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	input = text_analysis(event.message.text)
	
	if input['target'] == "新聞" :
		message = TextSendMessage(news(int(input['quantity']), input['theme']))
		line_bot_api.reply_message(
			event.reply_token,
			message)
	else : 
		#input = text_analysis(event.message.text)
		message = TextSendMessage(text=event.message.text)
		line_bot_api.reply_message(
			event.reply_token,
			message)
	
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)	
	
	
