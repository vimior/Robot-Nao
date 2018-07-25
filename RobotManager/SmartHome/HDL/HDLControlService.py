#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'vinman'

import time
import socket
from socket import *
import re
import struct
import platform
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import logging
logger = logging.getLogger()
from .. import find_all_broad



crc16tab = [
	0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
	0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
	0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
	0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
	0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
	0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
	0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
	0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
	0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
	0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
	0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
	0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
	0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
	0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
	0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
	0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
	0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
	0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
	0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
	0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
	0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
	0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
	0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
	0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
	0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
	0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
	0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
	0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
	0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
	0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
	0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
	0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]

def My_crc16xmodem(data):
	size = len(data)
	crc = 0 & 0xffff
	for i in range(size):
		crc = crc16tab[((crc >> 8) ^ data[i]) & 0xff] ^ (crc << 8) & 0xffff
	return crc & 0xffff

def UDP_Package(IP_List,Original_SubNetID,Original_DeviceID,Target_SubNetID,Target_DeviceID,Command,ContentList):
	Size_Contents = len(ContentList)
	Size_Package = 11 + Size_Contents
	Contents = ""
	# Target_DeviceType = 0xFFFD
	Original_DeviceType = 0xFAFE

	Original_SubNetID = int(Original_SubNetID)
	Original_DeviceID = int(Original_DeviceID)
	Original_DeviceType = int(Original_DeviceType)
	Target_SubNetID = int(Target_SubNetID)
	Target_DeviceID = int(Target_DeviceID)

	if isinstance(Command, str) and Command.lower().startswith('0x'):
		Command = int(Command, 16)
	Command = int(Command)
	# fmt = "!" + str(Size_Contents) + "B"
	for content in ContentList:
		Contents += struct.pack("!B", int(content))

	fmt = "!3B2H2B" + str(Size_Contents) + "s"
	strr = struct.pack(fmt, Size_Package, Original_SubNetID, Original_DeviceID,
				Original_DeviceType, Command, Target_SubNetID, Target_DeviceID, Contents)
	fmt = "!" + str(9+len(Contents)) + "B"
	List = struct.unpack(fmt,strr)

	CRC = My_crc16xmodem(List)

	fmt = "!14BH3B2H2B" + str(len(Contents)) + "sH"
	packet = struct.pack(fmt, IP_List[0], IP_List[1], IP_List[2], IP_List[3],\
				0x48, 0x44, 0x4C, 0x4D, 0x49, 0x52, 0x41, 0x43, 0x4C, 0x45, 0xAAAA,\
				Size_Package, Original_SubNetID, Original_DeviceID, Original_DeviceType,\
				Command, Target_SubNetID, Target_DeviceID, Contents, CRC)
	List = struct.unpack(fmt,packet)
	# print "====================================="
	logger.info(List)
	# print "====================================="
	return packet

def SendToDevice(IP_Addr, Original_SubNetID, Original_DeviceID, Target_SubNetID, Target_DeviceID, Command, ContentList):
	s = socket(AF_INET, SOCK_DGRAM)

	# 广播的形式
	s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	# IP_List = GetIp()

	# 指定一端口交换机IP的形式
	# IP_List = [192,168,10,255,"192.168.10.255"]
	IP_List = []
	for i in IP_Addr.split('.'):
		IP_List.append(int(i))
	if IP_List[3] != 255:
		IP_List[3] = 255
	IP_List.append(str(IP_List[0]) + '.' + str(IP_List[1]) + '.' + str(IP_List[2]) + '.' + str(IP_List[3]))
	print IP_List
	address = (IP_List[4], 6000)
	s.bind(("", 6000))
	packet = UDP_Package(IP_List, Original_SubNetID, Original_DeviceID, Target_SubNetID, Target_DeviceID, Command, ContentList)
	s.sendto(packet, address)

class HDLControlServiceModule():
	def __init__(self, session):
		pass

	def HDLDeviceControl(self, Original_SubNetID, Original_DeviceID,
						Target_SubNetID, Target_DeviceID,
						Command, *args):
		"""
        此版本不需要提供IP地址，已经自动获取
		"""
		ContentList = []
		if len(args) > 0:
			if isinstance(args[0], tuple) or isinstance(args[0], list):
				args = args[0]
				ContentList = args
			else:
				for i in range(len(args)):
					ContentList.append(args[i])
		system = platform.system()
		board_addrs = find_all_broad(system)
		for board_addr in board_addrs:
			SendToDevice(board_addr, Original_SubNetID,Original_DeviceID,Target_SubNetID,Target_DeviceID,Command,ContentList)

def test():
	IP_Addr = '192.168.199.255'
	Original_SubNetID = 0
	Original_DeviceID = 0
	Target_SubNetID = 2
	Target_DeviceID = 1
	Command = 0xE01C
	args = (1,255) # args是可变参数

	HDLControlServiceModule.HDLDeviceControl_1(IP_Addr, Original_SubNetID, Original_DeviceID, Target_SubNetID, Target_DeviceID, Command, args)
	# HDLControlServiceModule.HDLDeviceControl(IP_Addr, Original_SubNetID, Original_DeviceID, Target_SubNetID, Target_DeviceID, Command, 1, 255)



if __name__ == '__main__':
	logger.setLevel(logging.DEBUG)
	streamHandler = logging.StreamHandler()
	streamHandler.setLevel(logging.DEBUG)
	logger.addHandler(streamHandler)
	test()

