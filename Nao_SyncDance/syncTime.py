#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

# 同步时间的脚本，可以单独运行，也可以使用开机自动运行
# 注：需要root权限，可以通过修改一个su的配置文件来修改免输密码切换root用户，也可以修改/etc/sudoers修改普通用户可以运行/usr/sbin/ntpdate，推荐后者

from naoqi import ALProxy
import os
import sys

# 这里是切换root用户，如果不需要可以去除
if os.geteuid():
	args = [sys.executable] + sys.argv
	os.execlp('su', 'su', '-c', ' '.join(args))
    
cmd = "/usr/sbin/ntpdate -u ntp.api.bz | awk -F ' ' '{print $10}'"
while True:
	delayTime = os.popen(cmd).read()
	delayTime = float(delayTime)
	if abs(delayTime) < 0.01:
		break
print delayTime
memory = ALProxy("ALMemory", "127.0.0.1", 9559)
memory.insertData("DelayTime", delayTime)
