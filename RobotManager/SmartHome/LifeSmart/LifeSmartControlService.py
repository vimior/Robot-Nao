#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'vinman'

import urllib
import urllib2
import time
import datetime
import hashlib
import json

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging
logger = logging.getLogger()

def authorize():
    """
    获取授权
    返回元组
        (True, json_data) # 授权成功
        (False, json_data) # 授权失败
        (False, 'Error') # 异常
    """
    try:
        data = {
            "uid": 'xxxx',
            "pwd": 'xxxx',
            "appkey": "a8o2ZLxmn3fmB2NiaPnkLA",
        }
        url = 'http://api.ilifesmart.com/app/auth.login'
        request = urllib2.Request(url, data=urllib.urlencode(data))
        req = urllib2.urlopen(request)
        response = req.read()
        json_data = json.loads(response, encoding='utf-8')
        token = json_data['token']

        data = {
            "userid": "xxx",
            "appkey": "xxx",
            "token": token
        }
        url = 'http://api.ilifesmart.com/app/auth.do_auth'
        request = urllib2.Request(url, data=urllib.urlencode(data))
        req = urllib2.urlopen(request)
        response = req.read()
        json_data = json.loads(response, encoding='utf-8')
        # 授权失败返回False, json_data
        if json_data['code'] != 'success':
            logger.error('授权失败')
            return False, json_data
        # 授权成功返回True,json_data,并把结果response并写到文件
        with open('LifeSmart_Authorize.txt', 'w') as f:
            f.write(response)
        return True, json_data
    except Exception, e:
        logger.error(e)
        return False, 'Error'

def refreshtoken(flag=False):
    """
    刷新usertoken
    flag 是标志位,判断根据配置文件的信息的时间信息是否过期来刷新
    默认是False,就是根据时间信息来刷新,时间不过期就不刷新
    返回元组
        (True, json_data)
        (False, json_data)
        (False, 'Error')
    """
    try:
        # 读取配置文件获得配置信息
        with open('LifeSmart_Authorize.txt', 'r') as f:
            data = f.read()
        json_data = json.loads(data, encoding='utf-8')
        expiredtime = json_data['expiredtime'] if json_data.has_key('expiredtime') else 0
        currenttime = int(time.time())
        # 是否根据根据配置文件的信息的时间信息是否过期来刷新
        if flag is False:
            if expiredtime - currenttime > 3600 * 24 * 2:
                return True, json_data
    except:
        # 如果没有配置文件或者配置信息是错的就重新授权
        status, json_data = authorize()
        if status is False:
            return status, json_data

    appkey = "xxx"
    apptoken = "xxx"
    message_id = 10086
    userid = json_data['userid']
    usertoken = json_data['usertoken'] if json_data.has_key('usertoken') else json_data['token']
    url = "http://api.ilifesmart.com/app/auth.refreshtoken"
    t = int(time.mktime(datetime.datetime.now().timetuple()))
    strr = "appkey="+str(appkey)+"&time="+str(t)+"&userid="+str(userid)+"&apptoken="+str(apptoken)+"&usertoken="+str(usertoken)
    m = hashlib.md5()
    m.update(strr)
    sign = m.hexdigest()

    query = {
        "appkey":    appkey,
        "time":    t,
        "userid":    userid,
        "sign":    sign,
        "id":    message_id
    }
    try:
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('encoding', 'utf-8')
        response = urllib2.urlopen(req, json.dumps(query,ensure_ascii=False)).read()
        json_data = json.loads(response, encoding='utf-8')
        code = int(json_data['code'])
        # 刷新失败
        if code != 0:
            # 签名非法、没有授权、授权超时就重新授权
            if code == 10004 or code == 10005 or code == 10006:
                return authorize()
        else:
            with open('LifeSmart_Authorize.txt', 'w') as f:
                f.write(json.dumps(json_data, encoding='utf-8'))
            return status, json_data
    except Exception, e:
        logger.error(e)
        return False, 'Error'

def smartAppApi(query):
    """
    # 智能应用API
    返回元组
        (True, json_data)
        (False, json_data)
        (False, 'Error')
    """
    # 实际是从配置文件获取的
    status, json_data = refreshtoken()
    if status is False:
        return False, json_data

    usertoken = json_data['usertoken'] if json_data.has_key('usertoken') else json_data['token']
    logger.info('usertoken: %s' % usertoken)
    preUrl = query["method"]
    url = "http://api.ilifesmart.com/app/api."+preUrl
    appkey = "xxx"
    apptoken = "xxx"
    msg_id = query["id"]
    userid = json_data['userid']
    currentTime = int(time.mktime(datetime.datetime.now().timetuple()))
    params = query.get("params", None)
    temp = ""
    if params != None:
        params = sorted(params.iteritems(), key=lambda d:d[0])
        for i in params:
            temp += str(i[0])+":"+str(i[1])+","
    strr = "method:"+query["method"]+","+temp+"time:"+str(currentTime)+",userid:"+str(userid)+",usertoken:"+str(usertoken)+",appkey:"+str(appkey)+",apptoken:"+str(apptoken)
    m = hashlib.md5()
    m.update(strr)
    sign = m.hexdigest()
    # logger.info(sign)
    query["system"]["userid"] = json_data['userid']
    query["system"]["time"] = currentTime
    query["system"]["sign"] = sign
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('encoding', 'utf-8')
    try:
        res = urllib2.urlopen(req, json.dumps(query,ensure_ascii=False))
        response = res.read()
        json_data = json.loads(response, encoding='utf-8')
        code = int(json_data['code'])
        if code != 0:
            if code == 10004: # 签名非法
                status, json_data = refreshtoken(True)
                if status is True:
                    return smartAppApi(query)
            elif code == 10005 or code == 10006: # 没有授权或授权过期
                status, json_data = authorize()
                if status is True:
                    return smartAppApi(query)
            return False, "Error"
        else:
            return True, json_data

    except Exception, e:
        logger.error(e)
        return False, e

def controlLight(light_type, val):
    """
    控制胶囊灯泡
    """
    appkey = "xxxx"
    msg_id = 10086
    # userid = "7428812"
    query = {
        "id":    msg_id,
        "method":    "EpSet",
        "system":    {
            "ver":    "1.0",
            "sign":    "", # 这个值在后面经过计算后才补上
            "appkey":    appkey,
            "time":    0,
            "userid":    "", # 实际上没用到这个值,这个字段的值从配置文件获取
            "lang":    "en"
        },
        "params":    {
            "val":    val,
            "tag":    "m",
            "agt":    "A3MAAAAvAGEQNjQyNDAwNg",
            "me":    "271b",
            "idx":    "RGBW",
            "type":    light_type # 0x80开关灯泡,0xff设置颜色并开灯,0xfe设置颜色并关灯
        }
    }

    status, data = smartAppApi(query)
    logger.info('controlLight: %s' % status)
    logger.info('controlLight: %s' % data)

def getAllDevice():
    appkey = "xxxx"
    msg_id = 10086
    # userid = "7428812"
    query = {
        "id":    msg_id,
        "method":    "EpGetAll",
        "system":    {
            "ver":    "1.0",
            "sign":    "", # 这个值在后面经过计算后才补上
            "appkey":    appkey,
            "time":    0,
            "userid":    "", # 实际上没用到这个值,这个字段的值从配置文件获取
            "lang":    "en"
        }
    }

    status, data = smartAppApi(query)
    logger.info('getAll: %s' % status)
    logger.info('getAll: %s' % data)

def getDeviceInfo():
    """
    获取设备的信息
    只针对灯
    """
    appkey = "xxxx"
    msg_id = 10086
    query = {
        "id":    msg_id,
        "method":    "EpGet",
        "system":    {
            "ver":    "1.0",
            "sign":    "", # 这个值在后面经过计算后才补上
            "appkey":    appkey,
            "time":    0,
            "userid":    "", # 实际上没用到这个值,这个字段的值从配置文件获取
            "lang":    "en"
        },
        "params":    {
            "agt":    "A3MAAAAvAGEQNjQyNDAwNg",
            "me":    "2713",
        }
    }

    status, data = smartAppApi(query)
    print data
    if status != True:
        logger.error('Get Device Info Failed!')
        return False
    print 'is online: ',data['message']['stat']
    print 'type: ', data['message']['data']['RGBW']['type']
    print 'val: ', data['message']['data']['RGBW']['val']
    return status

class LifeSmartControlServiceModule():
    def __init__(self, session):
        pass

    def LifeSmartLightControl(self, light_type, val):
        controlLight(light_type, val)

    def GetLifeSmartLightInfo(self):
        getDeviceInfo()

    @staticmethod
    def LifeSmartLightControl_1(light_type, val):
        controlLight(light_type, val)

    @staticmethod
    def GetLifeSmartLightInfo_1():
        getDeviceInfo()

def test():
    # LifeSmartControlServiceModule.LifeSmartLightControl_1('0x80', 1)
    # LifeSmartControlServiceModule.GetLifeSmartLightInfo_1()
    # LifeSmartControlServiceModule.LifeSmartLightControl_1('0xff', '0xffff00')
    getAllDevice()

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    logger.addHandler(streamHandler)
    test()
