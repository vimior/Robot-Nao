#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import sys
import time
import datetime

from optparse import OptionParser
import re
import math

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

TouchEvent = None
memory = None

class TouchEventModule(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)

        global memory

        while True:
            try:
                memory = ALProxy("ALMemory")
                self.behavior = ALProxy("ALBehaviorManager")
                self.leds = ALProxy("ALLeds")
                self.flag = True
                break
            except:
                time.sleep(1)

        memory.subscribeToEvent("TouchChanged",
            "TouchEvent",
            "onTouchChanged")

    def onTouchChanged(self,strVarName,value):
        try:
            memory.unsubscribeToEvent("TouchChanged",
                "TouchEvent")
        except:
            print "Filename %s,     line: %d" %(sys._getframe().f_code.co_filename,sys._getframe().f_lineno)

        for sensor in value:
            if sensor[1] == True:
                if sensor[0] == "LFoot/Bumper/Left":
                    # self.speech.say("start")
                    self.leds.rotateEyes(0x0000ff, 0.5, 3)
                    self.leds.reset("AllLeds")
                    if self.behavior.isBehaviorRunning("hdl_topic_new") == False:
                        self.behavior.startBehavior("hdl_topic_new")


                elif sensor[0] == "RFoot/Bumper/Left" or sensor[0] == "RFoot/Bumper/Right":
                    self.leds.rotateEyes(0xff0000, 0.5, 3)
                    self.leds.reset("AllLeds")
                    if self.behavior.isBehaviorRunning("hdl_topic_new") == True:
                        self.behavior.stopBehavior("hdl_topic_new")


        memory.subscribeToEvent("TouchChanged",
            "TouchEvent",
            "onTouchChanged")





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

    global TouchEvent
    TouchEvent = TouchEventModule("TouchEvent")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
