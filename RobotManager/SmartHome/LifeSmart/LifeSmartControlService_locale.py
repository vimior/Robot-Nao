#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'vinman'

import socket
import time
import datetime
import hashlib
import json
# import requests
import uuid
import struct
import threading



# LSID=A3MAAAAvAGEQNjQyNDAwNg
# MGAMOD=LSHI3518
# WLAN=NA
# NAME=?
# ('192.168.1.113', 12345)

# discoveryProtocol()


mode = 'OD_ROBITZERO_ZERO'
token = 'kcaK1LL6ucJ13mOBgp0k8g'

pkg_type_dict = {
    'GET': 1,
    'GET-REPLY': 2,
    'SET': 3,
    'SET_REPLY': 4,
    'ADD': 5,
    'ADD-REPLY': 6,
    'DELETE': 7,
    'DELETE-REPLY': 8,
    'NOTIFY': 9,
    'NOTIFY-REPLY': 10,
}

# def getSign(query):
#     token = 'kcaK1LL6ucJ13mOBgp0k8g'
#     args = query.get("args", None)
#     temp = ""
#     if args:
#         args = sorted(args.iteritems(), key=lambda d:d[0])
#         for i in args:
#             temp += str(i[0])+":"+str(i[1])+","
#     strr = "obj:"+query["obj"]+","+temp+"ts:"+str(query['sys']['ts'])+",model:"+query['sys']['model']+",token:"+token
#     print strr
#     m = hashlib.md5()
#     m.update(strr)
#     sign = m.hexdigest()
#     return sign

def getSign(query):
    """
    获取签名值
    """
    token = 'xxx'
    args = query.get("args", None)
    temp = ""
    if args:
        args = sorted(args.iteritems(), key=lambda d:d[0])
        for i in args:
            temp += str(i[0])+":"+str(i[1])+","
    strr = "obj:"+query["obj"]+","+temp+"ts:"+str(query['sys']['ts'])+",model:"+query['sys']['model']+",token:"+token
    print strr
    m = hashlib.md5()
    m.update(strr)
    sign = m.hexdigest()
    return sign

def getContent(obj, args):
    """
    把数据包的json格式转成字符串形式
    已签名
    """
    query = {
        'sys': {
            'ver': 1,
            'sign': '',
            'model': 'OD_ROBITZERO_ZERO', # 设备类型
            'ts': int(time.mktime(datetime.datetime.now().timetuple())), # UTC时间戳
        },
        'obj': obj, # 对象名
        'args': args,
        'id': 10086,
    }

    sign = getSign(query)
    query['sys']['sign'] = sign
    jsonStr = json.dumps(query, encoding='utf-8')
    return jsonStr

def tcpPackage(pkg_type, content):
    """
    数据包封装
    """
    header = "JL"   # 2 byte
    version = 0     # 2 byte h
    pkg_type = pkg_type_dict[pkg_type] # 2 byte
    pkg_size = len(content) # 4 byte I
    content = content
    fmt = "!2s2hI" + str(pkg_size) + "s"
    strr = struct.pack(fmt, header, version, pkg_type, pkg_size, content)
    return strr

def discoveryProtocol():
    """
    发现协议，需要一直监听广播包并回复，否则可能会在一定时间后无法使用下面的接口
    目的是为了通信双方认可对方，建立信任
    """
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sd.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sd.bind(('', 12345))

    data, new_addr = sd.recvfrom(1024)
    print data
    print new_addr
    # addr = (new_addr[0], 12345)
    addr = new_addr
    # BC34002105E0
    # \nAGT=A3MAAAAvAGEQNjQyNDAwNg\nURL=GL://*:8888
    if not data.startswith('Z-SEARCH'):
        return False
    sd.sendto('MOD=OD_ROBITZERO_ZERO\nSN=BC34002105E0\nNAME=ROBOTZERO', addr)
    # sd.sendto('find mga', addr)
    # data, new_addr = sd.recvfrom(1024)
    # print data
    # print new_addr
    sd.close()
    return addr[0]

def registerDevice(ip):
    """
    注册设备，上线后第一个操作必须是这个
    """
    args = {
        'sn': 'BC34002105E0',
        'swver': '11',
    }
    content = getContent('device', args)
    pkg_type = 'ADD'
    package = tcpPackage(pkg_type, content)
    # print len(package)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.settimeout(10)
    sd.bind(('', 12346))
    addr = (ip, 12348)
    sd.sendto(package, addr)
    data, new_addr = sd.recvfrom(1024)
    # print len(data)
    length = len(data)
    strr = struct.unpack("!2s2hI"+str(length-10)+"s", data)
    print strr[2]
    print strr[4]
    print new_addr
    # raw_input("=====")
    sd.close()

def trigger(ip, sid):
    """
    触发预设好的场景
    """
    args = {
        'params': 'O',
        # 'params': {
        #     'scale': 1.0,
        # },
        'sid': sid,
    }
    content = getContent('trigger', args)
    pkg_type = 'NOTIFY'
    package = tcpPackage(pkg_type, content)
    # print len(package)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.settimeout(10)
    sd.bind(('', 12346))
    addr = (ip, 12348)
    sd.sendto(package, addr)
    data, new_addr = sd.recvfrom(1024)
    # print len(data)
    length = len(data)
    strr = struct.unpack("!2s2hI"+str(length-10)+"s", data)
    print strr[2]
    print strr[4]
    print new_addr
    # raw_input("=====")
    sd.close()

def getEps(ip):
    """
    获取全部设备列表(包含有属性)
    """
    args = {}
    content = getContent('eps', args)
    pkg_type = 'GET'
    package = tcpPackage(pkg_type, content)
    # print len(package)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.settimeout(10)
    sd.bind(('', 12346))
    addr = (ip, 12348)
    sd.sendto(package, addr)
    data, new_addr = sd.recvfrom(1024)
    # print len(data)
    length = len(data)
    strr = struct.unpack("!2s2hI"+str(length-10)+"s", data)
    print strr[2]
    print strr[4]
    print new_addr
    # raw_input("=====")
    sd.close()

def getEp(ip, me):
    """
    获取单个设备属性
    """
    args = {
        'me': me,
    }
    content = getContent('ep', args)
    pkg_type = 'GET'
    package = tcpPackage(pkg_type, content)
    # print len(package)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.settimeout(10)
    sd.bind(('', 12346))
    addr = (ip, 12348)
    sd.sendto(package, addr)
    data, new_addr = sd.recvfrom(1024)
    # print len(data)
    length = len(data)
    strr = struct.unpack("!2s2hI"+str(length-10)+"s", data)
    print strr[2]
    print strr[4]
    print new_addr
    # raw_input("=====")
    sd.close()

def setEp(ip, me, val):
    """
    设置设备属性,
    args需要根据不同设备设置，当前是针对灯泡的
    """
    args = {
        'me': me,
        'idx': 'RGBW',
        'type': '0xff',
        'tag': 'm',
        'val': val
    }
    content = getContent('ep', args)
    pkg_type = 'SET'
    package = tcpPackage(pkg_type, content)
    # print len(package)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.settimeout(10)
    sd.bind(('', 12346))
    addr = (ip, 12348)
    sd.sendto(package, addr)
    data, new_addr = sd.recvfrom(1024)
    # print len(data)
    length = len(data)
    strr = struct.unpack("!2s2hI"+str(length-10)+"s", data)
    print strr[2]
    print strr[4]
    print new_addr
    # raw_input("=====")
    sd.close()

def setDopair(ip):
    """
    此函数用于向智慧中心发送请求，让智慧中心进入配对状态(20s后会退出)，此时需要手动让要添加的设备进入配对状态(如灯要进入快闪状态)
    为了避免20s内还不能手动让设备进入配对状态，可以让设备先进入配对状态，然后再调用该接口
    """
    args = {}
    content = getContent('dopair', args)
    pkg_type = 'SET'
    package = tcpPackage(pkg_type, content)
    # print len(package)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.settimeout(20)
    sd.bind(('', 12346))
    addr = (ip, 12348)
    sd.sendto(package, addr)
    data, new_addr = sd.recvfrom(1024)
    # print len(data)
    length = len(data)
    strr = struct.unpack("!2s2hI"+str(length-10)+"s", data)
    print strr[2]
    print strr[4]
    print new_addr
    # raw_input("=====")
    sd.close()

# ip = discoveryProtocol()
ip = "192.168.1.113"
# registerDevice(ip)

# trigger(ip,703)
    # 1(回家,目前默认是打开该智慧中心下的所有灯泡和灯带)
    # 2(离家,目前默认是关闭该智慧中心下的所有灯泡和灯带)
    # 7(打开所有灯)
    # 8(关闭所有灯)
    # 701(改变所有灯的颜色)
    # 702(灯泡调亮)
    # 703(灯泡调暗)

# getEps(ip)
    # {
    #     "msg":[
    #         {
    #             "stat":1,
    #             "data":{
    #                 "RGBW":{
    #                     "type":255,
    #                     "valts":1463734158815,
    #                     "val":65320
    #                 }
    #             },
    #             "agt":"A3MAAAAvAGEQNjQyNDAwNg",
    #             "devtype":"SL_LI_RGBW",
    #             "name":"智能灯泡",
    #             "me":"2713"
    #         }
    #     ],
    #     "code":0,
    #     "id":10086
    # }

# getEp(ip, '2713') # 271b
    # {
    #     "msg":{
    #         "stat":1,
    #         "data":{
    #             "RGBW":{
    #                 "type":255,
    #                 "valts":1463734158815,
    #                 "val":65320
    #             }
    #         },
    #         "agt":"A3MAAAAvAGEQNjQyNDAwNg",
    #         "devtype":"SL_LI_RGBW",
    #         "name":"智能灯泡",
    #         "me":"2713"
    #     },
    #     "code":0,
    #     "id":10086
    # }

setEp(ip, '271b', '0')

# setDopair(ip)

# content = getContent(obj, args)
# package = tcpPackage('ADD', content)
# print len(package)







