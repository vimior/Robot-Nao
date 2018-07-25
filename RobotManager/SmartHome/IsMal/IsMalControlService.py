# -*- coding: utf-8 -*-
# __author__ = 'vinman

import urllib2
import urllib
import cookielib
import hashlib
import json

class IsMal(object):
    def __init__(self, username, password, cookie=None):
        self.__username = username
        self.__password = password
        self.__cookie = cookie
        self.config_cookiejar()
        if self.__cookie is None:
            self.__cookie = ''
            try:
                with open('ismal_cookie.txt') as f:
                    data = f.read()
                json_data = json.loads(data, encoding='utf-8')
                self.__cookie = json_data['cookie']
                self.__userId = json_data['userId']
            except:
                self.login()

    def config_cookiejar(self):
        self.cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(opener)

    def login(self):
        url = 'http://api.ismal.cn:80/rest/casAuth/loginFromApp'
        params = {
            'account': self.__username,
            'password': hashlib.md5(self.__password).hexdigest(),
        }

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
        }

        req = urllib2.Request(url, json.dumps(params), headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"tgt":"TGT-126109-hqXRKy56xufPbSCvaZaEZdu1iwFvcVxt1r0q6kFgelBeneOSFn-jun-cas.ismal.cn","user":{"phone":"13428283393","nickname":"Vinman","userId":2072516779,"gender":"false","password":"84d750eb280350ae4ac301ea38ac5830"},"rc":0}
        json_data = json.loads(res, encoding='utf-8')
        if json_data['rc'] != 0:
            raise Exception('登录异常,请检查参数是否正确')
        self.__userId = json_data['user']['userId']
        for ck in self.cookie._cookies_for_request(req):
            self.__cookie += ck.name + '=' + ck.value + ';'
        data = {
            'userId': self.__userId,
            'cookie': self.__cookie,
        }
        with open('ismal_cookie.txt', 'wb') as f:
            f.write(json.dumps(data, encoding='utf-8'))

    def getUserInfo(self):
        """
        获取用户信息
        """
        url = 'http://api.ismal.cn:80/rest/casAuth/getUserInfo'
        params = {
            'userId': self.__userId,
        }

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, json.dumps(params), headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"user":{"phone":"13428283393","nickname":"Vinman","userId":2072516779,"gender":"false","password":"84d750eb280350ae4ac301ea38ac5830"},"rc":0}

    def getDevice(self):
        """
        获取当前用户的设备
        """
        url = 'http://api.ismal.cn:80/rest/api/device/get?userId=%s' % self.__userId

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"rc":0,"devices":[{"delete":false,"deviceGuid":"smal9820C201502000785","deviceName":"小智养生壶","deviceType":"9820C","ownerId":2072516779}]}

    def getTaggroupMode(self):
        url = 'http://api.ismal.cn:80/rest/api/mode/taggroup/get?deviceType=9820C'

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"rc":0,"modeTagGroups":[{"description":"","deviceType":"9820C","id":15,"name":"面板模式组","type":2},{"description":"","deviceType":"9820C","id":16,"name":"四季养生","type":1},{"description":"","deviceType":"9820C","id":17,"name":"特定功效","type":1}]}

    def getTagMode(self):
        url = 'http://api.ismal.cn:80/rest/api/mode/tag/get?deviceType=9820C'

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"rc":0,"modeTags":[{"description":"","iconUrl":"","id":61,"modeTagGroup":15,"name":"面板模式"},{"description":"","iconUrl":"","id":54,"modeTagGroup":16,"name":"春"},{"description":"","iconUrl":"","id":55,"modeTagGroup":16,"name":"夏"},{"description":"","iconUrl":"","id":56,"modeTagGroup":16,"name":"秋"},{"description":"","iconUrl":"","id":57,"modeTagGroup":16,"name":"冬"},{"description":"","iconUrl":"","id":58,"modeTagGroup":17,"name":"滋补养生"},{"description":"","iconUrl":"","id":59,"modeTagGroup":17,"name":"美容养颜"},{"description":"","iconUrl":"","id":60,"modeTagGroup":17,"name":"清热解毒"},{"description":"","iconUrl":"","id":62,"modeTagGroup":17,"name":"安神补气"},{"description":"","iconUrl":"","id":63,"modeTagGroup":17,"name":"气血调理"}]}

    def getPublicMode(self):
        """
        获取预设的模式信息
        """
        url = 'http://api.ismal.cn:80/rest/api/mode/public/get?deviceType=9820C'

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req).read()
        print res

    def getPrivateMode(self):
        """
        获取自定义模式信息
        """
        url = 'http://api.ismal.cn:80/rest/api/mode/private/get?userId=2072516779&deviceType=9820C'

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"rc":0,"modes":[{"boilLevel":2,"buyUrl":"","code":5052,"dechlorTime":0,"description":"60℃泡料30分钟、小火慢炖形式煲料120分钟、保温120分钟","detail":" <p><span style=\"color:#000000;font-family:arial, 宋体, sans-serif;font-size:14px;line-height:24px;background-color:#FFFFFF;\"><img src=\"http://ismal-img.oss-cn-hangzhou.aliyuncs.com/mode/detail/green-square.jpg\" alt=\"\" /><span style=\"font-size:16px;line-height:1.5;\"><strong>&nbsp; &nbsp; 您的自定义参数如下：</strong></span><br /></span> </p><p class=\"p1\"><span style=\"font-size:14px;line-height:1;\">&nbsp; &nbsp; &nbsp; &nbsp; 1.60℃泡料30分钟</span> </p><p class=\"p1\"><span style=\"font-size:14px;line-height:1;\">&nbsp; &nbsp; &nbsp; &nbsp; 2.小火慢炖形式煲料120分钟</span> </p><p class=\"p1\"><span style=\"font-size:14px;line-height:1;\">&nbsp; &nbsp; &nbsp; &nbsp; 3.保温120分钟</span> </p>","deviceType":"9820C","eachStewLevel":0,"eachStewRestTime":15,"eachStewTime":10,"index":0,"isBoil":true,"isHintFeed":false,"isKeepWarm":true,"keepWarmTime":120,"largeIconUrl":"http://ismal-img.oss-cn-hangzhou.aliyuncs.com/mode/custom-large.png","mediumIconUrl":"http://ismal-img.oss-cn-hangzhou.aliyuncs.com/mode/custom-medium.png","modeTags":[],"name":"test","purifyTime":0,"smallIconUrl":"http://ismal-img.oss-cn-hangzhou.aliyuncs.com/mode/custom-small.png","soakTem":60,"soakTime":30,"stewTime":120,"subcribeTime":"","targetTem":60,"type":3}]}

    def getModeParams_by_modeCode(self, modeCode):
        """
        获取指定自定义模式的参数
        """
        url = 'http://api.ismal.cn:80/rest/api/mode/params/get?modeCode=%s' % modeCode

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"rc":0,"mode":{"boilLevel":2,"buyUrl":"","code":5052,"dechlorTime":0,"description":"60℃泡料30分钟、小火慢炖形式煲料120分钟、保温120分钟","detail":" <p><span style=\"color:#000000;font-family:arial, 宋体, sans-serif;font-size:14px;line-height:24px;background-color:#FFFFFF;\"><img src=\"http://ismal-img.oss-cn-hangzhou.aliyuncs.com/mode/detail/green-square.jpg\" alt=\"\" /><span style=\"font-size:16px;line-height:1.5;\"><strong>&nbsp; &nbsp; 您的自定义参数如下：</strong></span><br /></span> </p><p class=\"p1\"><span style=\"font-size:14px;line-height:1;\">&nbsp; &nbsp; &nbsp; &nbsp; 1.60℃泡料30分钟</span> </p><p class=\"p1\"><span style=\"font-size:14px;line-height:1;\">&nbsp; &nbsp; &nbsp; &nbsp; 2.小火慢炖形式煲料120分钟</span> </p><p class=\"p1\"><span style=\"font-size:14px;line-height:1;\">&nbsp; &nbsp; &nbsp; &nbsp; 3.保温120分钟</span> </p>","deviceType":"9820C","eachStewLevel":0,"eachStewRestTime":15,"eachStewTime":10,"index":0,"isBoil":true,"isHintFeed":false,"isKeepWarm":true,"keepWarmTime":120,"largeIconUrl":"http://ismal-img.oss-cn-hangzhou.aliyuncs.com/mode/custom-large.png","mediumIconUrl":"http://ismal-img.oss-cn-hangzhou.aliyuncs.com/mode/custom-medium.png","modeTags":[],"name":"test","purifyTime":0,"smallIconUrl":"http://ismal-img.oss-cn-hangzhou.aliyuncs.com/mode/custom-small.png","soakTem":60,"soakTime":30,"stewTime":120,"subcribeTime":"","targetTem":60,"type":3}}

    def addPrivateMode(self, params):
        """
        增加自定义模式
        """
        url = 'http://api.ismal.cn:80/rest/api/mode/private/add'
        params.update({'userId': self.__userId})
        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, json.dumps(params), headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"rc":0,"modeCode":5949}

    def deletePrivateMode_by_modeCode(self, modeCode):
        """
        删除自定义模式
        """
        url = 'http://api.ismal.cn:80/rest/api/mode/delete'

        params = {
            'userId': self.__userId,
            'modeCode': modeCode,
        }

        headers = {
            'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 1.7; .NET CLR 1.1.4322; CIBA; .NET CLR 2.0.50727)',
            'Connection': 'Keep-Alive',
            'Host': 'api.ismal.cn:80',
            'Cookie': self.__cookie,
        }

        req = urllib2.Request(url, json.dumps(params), headers=headers)
        res = urllib2.urlopen(req).read()
        print res
        # {"rc":0}



# ismal = IsMal('xxxxxx', 'xxxxxx')

# ismal.login()
# ismal.getUserInfo()
# ismal.getDevice()
# ismal.getTaggroupMode()
# ismal.getTagMode()
# ismal.getPublicMode()
# ismal.getPrivateMode()
# ismal.getModeParams_by_modeCode(140)

# params = {
#     "name": "测试模式",         # 模式名称
#     "isHintFeed": False,    #
#     "isKeepWarm": False,    # 是否保温
#     "keepWarmTime": 0,      # 保温时长
#     "targetTem": 60,        # 保温温度
#     "isBoil": True,         #
#     "eachStewLevel": 0,     # 1     1   2
#     "eachStewTime": 0,      # 15    15  15
#     "eachStewRestTime": 0,  # 10    5   5
#     "purifyTime": 0,        #

#     "soakTem": 60,          # 泡料温度
#     "soakTime": 0,          # 泡料时长
#     "dechlorTime": 0,       #
#     "stewTime": 10,         # 煲料时长
#     "boilLevel": 2,
#     # "userId": 2072516779,
#     "deviceType": "9820C",
#     "type": 0,
#     "code": 0,
# }
# ismal.addPrivateMode(params)

# ismal.deletePrivateMode_by_modeCode(5949)
