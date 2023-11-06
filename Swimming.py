import requests
import json
import os
import sys
import time
from configparser import ConfigParser
import datetime
conf = ConfigParser()
conf.read("1.config",encoding='utf-8')

username = conf.get('mysql', 'username')
password = conf.get('mysql', 'password')
date = conf.get('mysql', 'date')
c=conf.get('mysql', 'course')
phone=conf.get('mysql', 'phone')
speed=conf.get('mysql', 'speed')
if(username=='' or password=='' or date==''or c==''or phone==''):
    print("配置不全，无法运行")
    while True:
        pass
print(username,date,c)

s=requests.Session()
def login(username,password):

    url='https://gym.sztu.edu.cn/api/users/auth'
    headers={
        'accept':'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
        'Referer':'https://gym.sztu.edu.cn/',
        'origin': 'https: // gym.sztu.edu.cn',
        'content-type':'application/json;charset=UTF-8'
    }
    data={
        'username':username,
        'password':password
    }
    res=requests.post(url=url,data=json.dumps(data),headers=headers)
    token=json.loads(res.text)
    try:
        token=token['data']['token']
        print("登陆成功")
        return token
    except:
        print("登陆失败，请重新运行")
        while True:
            pass
def getcourseid(token):
    url = 'https://gym.sztu.edu.cn/api/field/place/reserve?venue=26&project=7&date='+date
    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
        'Referer': 'https://gym.sztu.edu.cn/confirmOrder',
        'content-type': 'application/json;charset=UTF-8',
        'authorization':'JWT '+token,
        'cookie':token
    }
    res=requests.get(url=url,headers=headers)
    res=json.loads(res.text)
    try:
        res=res['data'][0]['pricing']
        course=[]
        for item in res:
            course.append(item['id'])
        print("取场次成功 "+str(course))
        return course
    except:
        print("取场次失败，检查一下日期")
def getStatus(token):
    url = 'https://gym.sztu.edu.cn/api/field/place/reserve?venue=26&project=7&date=' + date
    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
        'Referer': 'https://gym.sztu.edu.cn/confirmOrder',
        'content-type': 'application/json;charset=UTF-8',
        'authorization': 'JWT ' + token,
        'cookie': token
    }
    res = requests.get(url=url, headers=headers)
    res = json.loads(res.text)
    res = res['data'][0]['pricing']
    status = []
    for item in res:
        status.append(item['reservation_status'])
    return status

def getUserInfo(token):
    url = 'https://gym.sztu.edu.cn/api/users/user-info'
    headers = {
         'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
        'Referer': 'https://gym.sztu.edu.cn/confirmOrder',
        'content-type': 'application/json;charset=UTF-8',
        'authorization':'JWT '+token,
        'cookie':token
    }
    res = requests.get(url=url,headers=headers)
    res = json.loads(res.text)
    res = res['data']
    print("取信息成功")
    return res
def orderSubmit(token,userinfo,course):
    #print(token)
    url = 'https://gym.sztu.edu.cn/api/order/order'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
        'Referer': 'https://gym.sztu.edu.cn/confirmOrder',
        'content-type': 'application/json;charset=UTF-8',
        'authorization':'JWT '+token,
        'cookie':token
    }

    if(userinfo['phone']==''):
        userinfo['phone'] = phone
    data = {
        "booker": userinfo['cn'],
        "phone": phone,
        "remarks": "",
        "attendees_num": 1,
        "payment_method": 2,
        "items": [
            {
            "pricing": course[int(c)]
            }
    ]
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers)
    res = json.loads(res.text)
    try:
        #print(res['code'])
        if(res['code']=="200"):
            #print(res['data']['order_sn'])
            print("预订成功，尝试支付中....")
            sn=res['data']['order_sn']
            return sn
        else:
            #print(res)
            return(False)
    except:
        return("出错啦")
def payOrder(ordersn,token):
    url='https://gym.sztu.edu.cn/api/order/order/pay'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
        'Referer': 'https://gym.sztu.edu.cn/confirmOrder',
        'content-type': 'application/json;charset=UTF-8',
        'authorization': 'JWT ' + token,
        'cookie': token
    }
    data={
        "order_sn": ordersn,
        "pay_method": 4,
        "card_id": 4
    }
    res=requests.post(url=url,headers=headers,data=json.dumps(data))
    res = json.loads(res.text)
    print("预订状态为："+res['msg'])
def start():
    token = login(username, password)
    userinfo = getUserInfo(token)
    course = getcourseid(token)
    sn = orderSubmit(token, userinfo, course)
    #print(sn)
    if (sn == False ):
        print("您已进入余票监控模式，系统将每{}秒刷新一次余票".format(speed))
        cnt = 1
        while(sn == False ):
            sn = orderSubmit(token, userinfo, course)
            cnt += 1
            sys.stdout.write("\r已监控{}次，状态:{}".format(cnt, sn))
            sys.stdout.flush()
            time.sleep(int(speed)/10)
    payOrder(sn,token)
    main = "weixin.exe"
    r_v = os.system(main)
    print (r_v)

def set_time():
    startTime = datetime.datetime(2022, 9, 27, 17, 59, 58)
    print('Program not starting yet...')
    while datetime.datetime.now() < startTime:
        time.sleep(1)

if __name__ == '__main__':
    set_time()
    token = login(username, password)
    userinfo = getUserInfo(token)
    course = getcourseid(token)
    cnt=0
    while True:
        try:
            sn = orderSubmit(token, userinfo, course)
            cnt += 1
            if(sn != False):
                payOrder(sn, token)
            sys.stdout.write("\r已监控{}次，状态:{}".format(cnt, sn))
            sys.stdout.flush()
        except:
            pass
