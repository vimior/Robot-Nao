#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'vinman'

import httplib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging
logger = logging.getLogger()

def httpGet(*args):
    """
    发送Http GET请求
    """
    if len(args) < 2:
        return
    addr = args[0]
    if len(args) == 2:
        flag = args[1]
        addr += ':8080'
        requrl = addr + '?state=' + flag # 博联使用
    if len(args) == 3:
        methodName = args[1]
        requrl = addr + '/' + methodName + '/?' + args[2]
    httpClient = None
    print requrl
    try:
        httpClient = httplib.HTTPConnection(addr, timeout=60)
        httpClient.request(method='GET', url=requrl)
        response = httpClient.getresponse()
        logger.info(response.read())
    except Exception, e:
        logger.error(e)
    finally:
        if httpClient:
            httpClient.close()

class BoardLinkControlServiceModule():
    def __init__(self, session):
        pass

    def BoardLinkControl(self, *args):
        """
        博联控制,通过Http GET请求中转的安卓手机进而控制
        目前只是控制插座
        """
        httpGet(*args)

    @staticmethod
    def BoardLinkControl_1(*args):
        """
        博联控制,通过Http GET请求中转的安卓手机进而控制
        目前只是控制插座
        """
        httpGet(*args)

def test():
    BoardLinkControlServiceModule.BoardLinkControl_1('192.168.199.131:8080', 'off')

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    logger.addHandler(streamHandler)
    test()


