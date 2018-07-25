#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

from naoqi import ALProxy
import time

# dialog = ALProxy("ALDialog", "127.0.0.1", 9559)

# topics = dialog.getLoadedTopics("Chinese")
# print "mnc:", topics
# for topic in topics:
#     if topic == "Robot_topic":
#         dialog.unloadTopic("Robot_topic")
# topics = dialog.getLoadedTopics("English")
# print "enu:", topics
# for topic in topics:
#     if topic == "Robot_topic":
#         dialog.unloadTopic("Robot_topic")

# path_mnc = "/home/nao/RobotManager/test/Robot_mnc.top"
# path_enu = "/home/nao/RobotManager/test/Robot_enu.top"

# topic = dialog.loadTopic(path_mnc)
# print "topic_mnc:", topic
# topic = dialog.loadTopic(path_enu)
# print "topic_enu:", topic
# try:
#     dialog.subscribe('TopicModule')
# except Exception as e:
#     print e

# dialog.setLanguage("Chinese")
# dialog.activateTopic(topic)
# # dialog.activateTopic(topic_enu)
# # time.sleep(5)
# # dialog.forceInput("你好")

# time.sleep(90)
# print dialog.getActivatedTopics()

# try:
#     dialog.deactivateTopic(topic)
#     dialog.unloadTopic(topic)
# except Exception as e:
#     print e
# dialog.unsubscribe('TopicModule')


# dialog = ALProxy("ALDialog", "192.168.123.46", 9559)
# memory = ALProxy("ALMemory", "192.168.123.46", 9559)

# topics = dialog.getLoadedTopics("Chinese")
# print "mnc:", topics
# # for topic in topics:
# #     if topic == "Robot_topic":
# #         dialog.unloadTopic("Robot_topic")
# topics = dialog.getLoadedTopics("English")
# print "enu:", topics
# # for topic in topics:
# #     if topic == "Robot_topic":
# #         dialog.unloadTopic("Robot_topic")

# print memory.getData("SoundDetected")
# subscribersInfo = dialog.getSubscribersInfo()
# print subscribersInfo
# # time.sleep(5)
# # for subscriberInfo in subscribersInfo:
# #     dialog.unsubscribe(subscriberInfo[0])

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
# import paramiko
# client = paramiko.SSHClient()
# client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# client.connect('192.168.123.1', 22, username='robot0', password='robot501', timeout=4)
# stdin, stdout, stderr = client.exec_command('sudo su')
# for std in stdout.readlines():
#   print std,
# print "======================="
# stdin, stdout, stderr = client.exec_command('robot501')
# for std in stdout.readlines():
#   print std,
# print "************************"
# stdin, stdout, stderr = client.exec_command('ifconfig eht0:0 192.168.188.188')
# for std in stdout.readlines():
#   print std,
# client.close()

#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import os,sys
import paramiko  
import threading  
import platform
 
curr_ssh = None 
curr_prompt = ">>"
 
#使用说明       
def printUsage():
    print "    !ls                     :list sessions."
    print "    !session id             :connect session."
    print "    !conn host user password:connect host with user."
    print "    !exit                   :exit."
 
#连接 
def conn(ip,username,passwd):
    try:
        ssh = paramiko.SSHClient()  
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
        ssh.connect(ip,22,username,passwd,timeout=5)  
        print "Connect to ",ip," with ",username
        global curr_prompt
        curr_prompt=username+"@"+ip+">>"
        return ssh
    except:
        return None
         
#加载以前的连接信息
sessions=[]
def loadSessions():
    global sessions
    try:
        f = open("sessions")
        sessions = f.readlines()
        f.close()
    except:
        pass
 
#执行本地命令,ssh.py的命令       
def exe_cmd_local(cmd):
    if(cmd == "!ls"):
        loadSessions()
        global sessions
        i=0
        print "Sessions:"
        for s in sessions:
            print"[%d] %s" %(i,s)
            i+=1
    else:
        vals = cmd.split(' ')
        if(vals[0]=="!session"):
            id = (int)(vals[1])
            if(id<len(sessions)):
                os_name="platform.system()" 
                new_console_cmd="" 
                if(os_name == "Linux"):
                    new_console_cmd="gnome-terminal -e \"./ssh.py " + sessions[id]+"\""
                elif(os_name == "Windows"):
                    new_console_cmd="start ssh.py " + sessions[id]
                os.system(new_console_cmd)
            else:
                print "Didn't hava sessoin ",vals[1]
        elif(vals[0]=="!conn"):
            global curr_ssh
            curr_ssh = conn(vals[1],vals[2],vals[3])
            f = open("sessions","a")
            line = vals[1]+" "+vals[2]+" "+vals[3]+"\n"
            f.write(line)
            f.close()
 
#在ssh连接的主机上执行命令         
def exe_cmd_ssh(ssh,cmd):
    if(ssh == None):
        print "Didn't connect to a server. Use '!conn' to connect please."
        return
    stdin, stdout, stderr = ssh.exec_command(cmd)  
    #stdin.write("Y")   #简单交互，输入 ‘Y’   
    #屏幕输出
    print stdout.read().decode('utf-8')
    print stderr.read().decode('utf-8')
         
# 入口函数
if __name__=='__main__':
    loadSessions()
    if(len(sys.argv)==4):
        curr_ssh = conn(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        printUsage()
    while True:
        cmd = raw_input(curr_prompt)
        if(len(cmd)==0):
            continue
        if cmd.startswith('put'):
            name = cmd.split(' ')[1].strip().strip('\n')
            cmd = "echo '' > %s" % (name)
            exe_cmd_ssh(curr_ssh,cmd)
            with open(name, "r") as f:
                lines = f.readlines()
                for line in lines:
                    cmd = "echo \"%s\" >> %s" % (line.strip('\n'), name)
                    exe_cmd_ssh(curr_ssh,cmd)
            cmd = ""
        if(len(cmd)==0):
            continue
        if(cmd == "!exit"):
            if(curr_ssh != None):
                curr_ssh.close();
            break
        else:
            if(cmd[0] == '!'):
                exe_cmd_local(cmd)
            else:
                exe_cmd_ssh(curr_ssh,cmd)


# import winpexpect
# from getpass import getpass

# password = getpass()

# def ssh_cmd(cmd):
#     ssh = winpexpect.winspawn('ssh.exe robot0@192.168.123.1')
#     ssh.logfile = sys.stdout
#     # ssh = pexpect.spawn('ssh robot0@192.168.123.1')
#     try:
#         i = ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=5)
#         if i == 0:
#             ssh.sendline(password)
#         elif i == 1:
#             ssh.sendline('yes')
#             ssh.expect('password: ')
#             ssh.sendline(password)
#     except Exception as e:
#         print e
#     else:
#         r = ssh.read()
#         print r
#     ssh.close()

# if __name__ == '__main__':
#     ssh_cmd("ls")


# import subprocess

# subprocess.Popen('putty.exe -pw robot501 -m cmd.sh robot0@192.168.123.1')
# print 