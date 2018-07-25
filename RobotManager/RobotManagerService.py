#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'vinman'

import time
import os
import sys
import re
import urllib2
import logging

while True:
    try:
        import qi
        break
    except:
        time.sleep(1)

reload(sys)
sys.setdefaultencoding('utf8')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler('debug.log')
file_handler_fmt = '[%(asctime)s] [%(levelname)s] [%(filename)s] [%(funcName)s] [%(lineno)d]: \n\t[message]: %(message)s'
file_handler_date_fmt = '%Y-%m-%d %H:%M:%S'
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(logging.Formatter(file_handler_fmt, file_handler_date_fmt))
logger.addHandler(fileHandler)

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
logger.addHandler(streamHandler)

class RobotManagerServiceModule():
    def __init__(self, session):
        while True:
            try:
                # self.tts = ALProxy("ALTextToSpeech","127.0.0.1",9559)
                self.speech = session.service("ALTextToSpeech")
                self.behavior = session.service("ALBehaviorManager")
                self.posture = session.service("ALRobotPosture")
                self.motion = session.service("ALMotion")
                self.autonomouslife = session.service("ALAutonomousLife")
                self.basic = session.service("ALBasicAwareness")
                self.audiodevice = session.service("ALAudioDevice")
                self.aup = session.service("ALAudioPlayer")
                self.memory = session.service("ALMemory")
                break
            except:
                time.sleep(1)

    def setVolume(self, *args):
        if isinstance(args[0], tuple):
            args = args[0]
        if isinstance(args[0], int) or isinstance(args[0], long):
            self.audiodevice.setOutputVolume(args[0])
        else:
            volume = self.audiodevice.getOutputVolume()
            if args[0] == "add":
                if volume <= 90:
                    self.audiodevice.setOutputVolume(volume+10)
                else:
                    self.audiodevice.setOutputVolume(100)
            elif args[0] == "sub":
                if volume >= 10:
                    self.audiodevice.setOutputVolume(volume-10)
                else:
                    self.audiodevice.setOutputVolume(0)

    def sayText(self, *args):
        if isinstance(args[0], tuple):
            args = args[0]
        self.speech.stopAll()
        if len(args) == 2:
            self.speech.say(args[0], _async=True)
        elif len(args) == 1:
            self.speech.say(args[0])

    def saidOrNot(self, *args): # 返回1表示说完，0表示没说完
        return self.memory.getData("ALTextToSpeech/TextDone")

    def stopToSay(self, *args):
        self.speech.stopAll()

    def runBehavior(self, *args):
        if isinstance(args[0], tuple):
            args = args[0]
        if len(args) < 1:
            return
        if self.behavior.isBehaviorInstalled(args[0]):
            if self.behavior.isBehaviorRunning(args[0]) == False:
                try:
                    if len(args) == 2:
                        self.behavior.startBehavior(args[0])
                    else:
                        self.behavior.runBehavior(args[0])
                except:
                    self.speech.say("对不起，应用程序启动失败")
            else:
                self.speech.say("这个应用我已经正在运行了")
        else:
            self.speech.say("对不起，我没有安装这个行为程序")

    def stopBehavior(self, *args):
        if isinstance(args[0], tuple):
            args = args[0]
        if len(args) > 0:
            if self.behavior.isBehaviorRunning(args[0]):
                try:
                    self.behavior.stopBehavior(args[0])
                except:
                    return
            elif args[0] == "All":
                self.behavior.stopAllBehaviors()
            else:
                return
        else:
            self.behavior.stopAllBehaviors()
        if self.motion.robotIsWakeUp() == False \
        or self.posture.getPosture() == "Crouch":
            return
        else:
            self.posture.goToPosture("Stand", 0.5)
            self.lockOrNot("False")

    def stopAllBehavior(self, *args):
        self.behavior.stopAllBehaviors()
        self.posture.goToPosture("Stand", 0.5)
        self.lockOrNot("False")

    def wakeUp(self, *args):
        if self.posture.getPosture() == "Stand":
            self.posture.goToPosture("Stand", 0.5)
        if self.motion.robotIsWakeUp() == False:
            self.motion.wakeUp()
        elif self.posture.getPosture() == "Crouch":
            self.setState("disabled")
        self.posture.goToPosture("Stand", 0.5)
        # self.lockOrNot("False")

    def rest(self, *args):
        if self.motion.robotIsWakeUp():
            self.motion.rest()
            # 注：若在对话使用，请勿使用以下这句，否则会停掉对话
            self.setState("disabled")

    def goToPosture(self, *args):
        if isinstance(args[0], tuple):
            args = args[0]
        curPosture = self.posture.getPosture()
        if args[0] == "Crouch":
            self.rest()
        elif args[0] == "Stand":
            if self.motion.robotIsWakeUp() == False:
                self.motion.wakeUp()
            else:
                self.posture.goToPosture("Stand", 0.5)
        else:
            self.posture.goToPosture(args[0], 0.5)

    def setState(self, *args):
        if isinstance(args[0], tuple):
            args = args[0]
        try:
            self.autonomouslife.setState(args[0])
        except:
            pass

    def _lockMotor(self):
        if self.motion.robotIsWakeUp() == False:
            return
        while self.motion.getBreathEnabled("Legs") == True \
        or self.motion.getBreathEnabled("Arms") == True \
        or self.basic.isAwarenessRunning() == True:
            self.motion.setBreathEnabled("Legs", False)
            self.motion.setBreathEnabled("Arms", False)
            self.basic.stopAwareness()
        self.posture.goToPosture("Stand", 0.5)
        while self.motion.getBreathEnabled("Legs") == True \
        or self.motion.getBreathEnabled("Arms") == True \
        or self.basic.isAwarenessRunning() == True:
            self.motion.setBreathEnabled("Legs", False)
            self.motion.setBreathEnabled("Arms", False)
            self.basic.stopAwareness()

    def _unlockMotor(self):
        self.setState("solitary")
        if self.motion.robotIsWakeUp() == False \
        or self.autonomouslife.getState() == "disabled":
            return
        while self.motion.getBreathEnabled("Legs") == False \
        or self.motion.getBreathEnabled("Arms") == False \
        or self.basic.isAwarenessRunning() == False:
            self.motion.setBreathEnabled("Legs", True)
            self.motion.setBreathEnabled("Arms", True)
            self.basic.startAwareness()

    def lockOrNot(self, *args):
        if isinstance(args[0], tuple):
            args = args[0]
        if args[0] == "True":
            self._lockMotor()
        elif args[0] == "False":
            self._unlockMotor()

def main():
    global session
    app = qi.Application()
    session = qi.Session()
    session.connect("tcp://127.0.0.1:9559")
    RobotManagerService = RobotManagerServiceModule(session)
    session.registerService("RobotManagerService", RobotManagerService)
    print 'Start RobotManagerService...'

    # 尝试加载河东的控制服务
    try:
      from SmartHome.HDL.HDLControlService import HDLControlServiceModule
      HDLControlService = HDLControlServiceModule(session)
      session.registerService("HDLControlService", HDLControlService)
      print 'Start HDLControlService...'
    except Exception as e:
      print e

    # 尝试加载Hue的控制服务
    try:
      from SmartHome.Hue.HueControlService import HueControlServiceModule
      HueControlService = HueControlServiceModule(session)
      session.registerService("HueControlService", HueControlService)
      print 'Start HueControlService...'
    except Exception as e:
      print e

    # 尝试加载LifeSmart的控制服务
    try:
      from SmartHome.LifeSmart.LifeSmartControlService import LifeSmartControlServiceModule
      LifeSmartControlService = LifeSmartControlServiceModule(session)
      session.registerService("LifeSmartControlService", LifeSmartControlService)
      print 'Start LifeSmartControlService...'
    except Exception as e:
      print e

    # 尝试加载BoardLink的控制服务
    try:
      from SmartHome.BoardLink.BoardLinkControlService import BoardLinkControlServiceModule
      BoardLinkControlService = BoardLinkControlServiceModule(session)
      session.registerService("BoardLinkControlService", BoardLinkControlService)
      print 'Start BoardLinkControlService...'
    except Exception as e:
      print e


    app.run()


if __name__ == "__main__":
    main()
