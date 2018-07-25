# -*- coding: utf-8 -*-
# __author__ = 'vinman

import urllib2
import urllib
import cookielib
import hashlib
import json
import time

# 设置cookie
# cookie = cookielib.CookieJar()
# opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
# urllib2.install_opener(opener)


url = 'http://homemate.orvibo.com/getDeviceDesc?source=ZhiJia365&lastUpdateTime=%s' % int(time.time())

headers = {
    'Accept-Encoding': 'gzip',
    'User-Agent': 'android-async-http/1.4.4 (http://loopj.com/android-async-http)',
    'Connection': 'Keep-Alive',
    'Host': 'homemate.orvibo.com',
}

req = urllib2.Request(url, headers=headers)
res = urllib2.urlopen(req).read()
print res

