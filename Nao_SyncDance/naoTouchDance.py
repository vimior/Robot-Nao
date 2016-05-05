#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

#!/bin/bash
# ntpdate -u ntp.api.bz
# ntpdate 0.pool.ntp.org
# /usr/sbin/ntpdate -u ntp.api.bz
# /sbin/hwclock -w

import sys
import time
import datetime

from optparse import OptionParser
import re
import math

# 循环仅仅用于个别用途
while True:
    try:
        from naoqi import ALProxy
        from naoqi import ALModule
        from naoqi import ALBroker
        break
    except:
        time.sleep(1)


NAO_IP = "127.0.0.1"
NAO_PORT = 9559

TouchDance = None
memory = None

class TouchDanceModule(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)

        global memory

        # 循环仅仅用于个别用途
        while True:
            try:
                memory = ALProxy("ALMemory")
                self.speech = ALProxy("ALTextToSpeech")
                self.behavior = ALProxy("ALBehaviorManager")
                self.motion = ALProxy("ALMotion")
                self.leds = ALProxy("ALLeds")
                self.flag = False # 用于防止误触碰触发事件
                break
            except:
                time.sleep(1)
        
        memory.subscribeToEvent("TouchChanged",
            "TouchDance",
            "onTouchChanged")

    def onTouchChanged(self,strVarName,value):
        try:
            memory.unsubscribeToEvent("TouchChanged",
                "TouchDance")
        except:
            print "Filename %s,     line: %d" %(sys._getframe().f_code.co_filename,sys._getframe().f_lineno)

        for sensor in value:
            if sensor[1] == True:
                # 左脚脚趾触碰事件,需要触碰两次才可以
                if sensor[0] == "LFoot/Bumper/Left":
                    # self.speech.say("start")
                    if self.flag == False:
                        self.leds.rotateEyes(0x00ff00, 0.5, 2)
                        self.leds.reset("AllLeds")
                        self.flag = True
                        self.motion.wakeUp()
                        self.speech.post.say("Ready")
                    else:
                        self.leds.rotateEyes(0x0000ff, 0.5, 2)
                        self.leds.reset("AllLeds")
                        self.flag = False
                        self.motion.wakeUp()
                        self.speech.post.say("Start")
                        # 预加载舞蹈程序jtw
                        self.behavior.preloadBehavior("jtw")

                        self.dev_time = memory.getData("DelayTime")
                        # print self.dev_time

                        # 等待秒数为0才执行事件处理函数
                        while True:
                            if datetime.datetime.now().second == 0:
                                self.runBehavior()
                                break
                # 右脚脚趾触碰事件，主要用于把误碰左脚脚趾的事件标志flag置为False
                elif sensor[0] == "RFoot/Bumper/Left" or sensor[0] == "RFoot/Bumper/Right":
                    # self.speech.say("over")
                    self.leds.rotateEyes(0xff0000, 0.5, 2)
                    self.leds.reset("AllLeds")
                    self.flag = False
                    self.motion.rest()
                    self.speech.post.say("Over")
                    # self.flag = False
                    # self.speech.post.say("over")
                    
        memory.subscribeToEvent("TouchChanged",
            "TouchDance",
            "onTouchChanged")
        
    def runBehavior(self):
        # 延时"2s+时间偏移"
        time.sleep(2+self.dev_time)
        self.speech.say("下面进行舞蹈表演")
        self.behavior.runBehavior("jtw")

    
        

def main():
    global NAO_IP
    global NAO_PORT

    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=NAO_PORT)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port

    global TouchDance
    TouchDance = TouchDanceModule("TouchDance")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
