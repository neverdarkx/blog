#coding=utf8
import requests
import hashlib
import random

appId = '20171123000098924'
secretKey = 'Dlt3Slg4be9DSQ8IgxU6'
salt = random.randint(12345,61100)


def translate(text):
    sign = appId+text+str(salt)+secretKey
    m = hashlib.md5()
    m.update(sign.encode('utf-8'))
    sign = m.hexdigest()
    config = {'q': text,
              'from': 'zh', 'to': 'en',
              'appid': appId, 'salt': str(salt), 'sign': sign
    }
    r = requests.get('https://fanyi-api.baidu.com/api/trans/vip/translate',params=config)
    return print(r.json())
translate('苹果')
