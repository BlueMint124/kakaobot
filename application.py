from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timezone, timedelta
import re

application = Flask(__name__)


@application.route("/", methods=["POST"])
def keyword():
    KST = timezone(timedelta(hours=9))
    time_record = datetime.now(KST)
    req = request.get_json()
    text_ck = req['userRequest']['utterance']
    text = '정보를 찾을 수 없습니다.'
    if str(text_ck).count('오늘 급식'):
        today = str(time_record)
        day = today[:4]+today[5:7]+today[8:10]
        url = 'https://open.neis.go.kr/hub/mealServiceDietInfo?' \
            'ATPT_OFCDC_SC_CODE=J10&SD_SCHUL_CODE' \
            '=7531046&MLSV_YMD={}'.format(day)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            t = soup.find_all('message')
            t = t[0].get_text()
            if t == '해당하는 데이터가 없습니다.':
                text = '급식이 데이터가 아직 없습니다.'
            else:
                d = soup.find_all('ddish_nm')
                d = d[0].get_text()
                diet = d.replace('<br/>', '\n').replace('.', '')
                diet = diet.replace('(', '').replace(')', '').replace('#', '')
                new_d = re.sub(r"[0-9]", "", diet)
                text = f'*오늘의급식*\n{new_d}'
    if str(text_ck).count('내일 급식'):
        tomorrow = str(time_record + timedelta(days=1))[:10]
        day = tomorrow[:4]+tomorrow[5:7]+tomorrow[8:10]
        url = 'https://open.neis.go.kr/hub/mealServiceDietInfo?' \
            'ATPT_OFCDC_SC_CODE=J10&SD_SCHUL_CODE' \
            '=7531046&MLSV_YMD={}'.format(day)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            t = soup.find_all('message')
            t = t[0].get_text()
            if t == '해당하는 데이터가 없습니다.':
                text = '급식이 데이터가 아직 없습니다.'
            else:
                d = soup.find_all('ddish_nm')
                d = d[0].get_text()
                diet = d.replace('<br/>', '\n').replace('.', '')
                diet = diet.replace('(', '').replace(')', '').replace('#', '')
                new_d = re.sub(r"[0-9]", "", diet)
                text = f'*내일의급식*\n{new_d}'
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text
                    }
                }
            ]
        }
    }
    return jsonify(res)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, threaded=True)