#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'vinman'

import colormodels
import thread
import threading
import time
from phue import Bridge, Group, PhueRegistrationException, PhueRequestTimeout

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging
logger = logging.getLogger()

def xyzFromRGB(red, green=None, blue=None):
	"""
	RGB转成xyz
	"""
	if isinstance(red, basestring):
		# assume a hex string is passed
		if red[0] == "#":
			colorString = red[1:]
		else:
			colorString = red
		red = int(colorString[0:2], 16)
		green = int(colorString[2:4], 16)
		blue = int(colorString[4:], 16)

	# We need to convert the RGB value to Yxy.
	redScale = float(red) / 255.0
	greenScale = float(green) / 255.0
	blueScale = float(blue) / 255.0
	colormodels.init(
		phosphor_red=colormodels.xyz_color(0.64843, 0.33086),
		phosphor_green=colormodels.xyz_color(0.4091, 0.518),
		phosphor_blue=colormodels.xyz_color(0.167, 0.04))
	xyz = colormodels.irgb_color(red, green, blue)
	xyz = colormodels.xyz_from_rgb(xyz)
	xyz = colormodels.xyz_normalize(xyz)
	return xyz

def write_HueIp_to_file(ip):
	with open('./hue_ip.txt', 'w') as f:
		f.write(ip)
def read_HueIp_from_file():
	try:
		with open('./hue_ip.txt', 'r') as f:
			return f.readline()
	except:
		return None

class HueClass():
	def __init__(self, Hue_IP):
		self.isFound = False # 是否已经找到
		self.isConnect = False # 是否已经连接
		self.lights_info = None # 用来记录网桥上所有lights的信息
		self.isSame = True
		self.reachable_lights_ids = [] # 用来记录网桥上在线的lights的id号
		self.b = None

		# 开启两个线程分别尝试用配置文件的IP和参数传过来的IP来连接网桥
		ip = read_HueIp_from_file()
		t1 = threading.Thread(target=self.thread_func_to_search, args=(ip,))
		t2 = threading.Thread(target=self.thread_func_to_search, args=(Hue_IP,))
		t1.setDaemon(True)
		t2.setDaemon(True)
		t1.start()
		t2.start()
		count = 300
		# 等待连接或者线程结束
		while count:
			# 当有其中一个线程连接上网桥就退出等待
			if self.isFound is True and self.isConnect is True:
				break
			# 当两个线程都结束就退出等待
			elif t1.isAlive() is False and not t2.isAlive() is False:
				time.sleep(1)
				break
			else:
				count -= 1
				time.sleep(0.1)

		# 当还没发现网桥并且没有连接上网桥就开始搜索参数传过来的Hue_IP整个网段的IP进行尝试连接
		# 可以考虑搜索本地IP的整个网段
		if self.isFound is False and self.isConnect is False:
			ipList = Hue_IP.split('.')[:-1]
			preIp = ''
			for i in ipList:
				preIp += i + '.'
			for i in xrange(1,256):
				if self.isFound is False:
					ip = '%s%s' % (preIp, i)
					print ip
					t = thread.start_new_thread(self.thread_func_to_search, (ip,))
					time.sleep(0.05)
		count = 30

		# 当搜索到网桥但还没连接上就等待连接
		if self.isFound is True and self.isConnect is False:
			while count:
				if self.isConnect is True:
					break
				else:
					count -= 1
					time.sleep(1)

		self.get_lights()

	def thread_func_to_search(self, ip):
		"""
		搜索网桥的线程函数
		"""
		try:
			if ip is None or ip is '':
				self.b = Bridge()
			else:
				self.b = Bridge(ip)
			if self.b is not None:
				if ip is None or ip is '':
					try:
						ip = self.b.get_ip_address()
					except:
						pass
				if self.isSame is True:
					self.isSame = False
					logger.info("Hue_IP: %s" % ip)
				self.isFound = True
				self.isConnect = True
				write_HueIp_to_file(ip)
				
		except PhueRegistrationException as e:
			self.isFound = True
			if self.isSame is True:
				self.isSame = False
				logger.info('请按一下网桥按键进行连接')
			while True:
				try:
					self.b = Bridge(ip)
					if self.isSame is True:
						self.isSame = False
						logger.info("Hue_IP: %s" % ip)
					self.isConnect = True		
					write_HueIp_to_file(ip)
					break
				except:
					time.sleep(2)
		except Exception,e:
			pass

	# {u'name': u'Hue color lamp 2', 	u'swversion': u'66009663', 		u'manufacturername': u'Philips', u'state': {u'on': False, u'hue': 25720, 	u'colormode': u'xy', u'effect': u'none', u'alert': u'none', u'xy': [0.4076, 0.5153], 	u'reachable': True, 	u'bri': 200, 	u'sat': 254, 	u'ct': 287}, 	u'uniqueid': u'00:17:88:01:00:fc:79:b2-0b', u'type': u'Extended color light', 	u'modelid': u'LCT001'}
	# {u'name': u'Hue color lamp 3', 	u'swversion': u'66013452', 		u'manufacturername': u'Philips', u'state': {u'on': False, u'hue': 25600, 	u'colormode': u'xy', u'effect': u'none', u'alert': u'none', u'xy': [0.409, 0.518], 		u'reachable': True, 	u'bri': 200, 	u'sat': 254, 	u'ct': 290}, 	u'uniqueid': u'00:17:88:01:00:fc:81:a4-0b', u'type': u'Extended color light', 	u'modelid': u'LCT001'}
	# {u'name': u'Hue color lamp 1', 	u'swversion': u'66009663', 		u'manufacturername': u'Philips', u'state': {u'on': False, u'hue': 0, 		u'colormode': u'hs', u'effect': u'none', u'alert': u'none', u'xy': [0.0, 0.0], 			u'reachable': False, 	u'bri': 0, 		u'sat': 0, 		u'ct': 0}, 		u'uniqueid': u'00:17:88:01:00:fc:80:31-0b', u'type': u'Extended color light', 	u'modelid': u'LCT001'}
	# {u'name': u'Hue bloom 1', 		u'swversion': u'5.23.1.13452', 	u'manufacturername': u'Philips', u'state': {u'on': False, u'hue': 0, 		u'colormode': u'hs', u'effect': u'none', u'alert': u'none', u'xy': [0.0, 0.0], 			u'reachable': True, 	u'bri': 0, 		u'sat': 0}, 					u'uniqueid': u'00:17:88:01:00:c2:81:c6-0b', u'type': u'Color light', 			u'modelid': u'LLC011'}
	# {u'name': u'Hue lightstrip 1', 	u'swversion': u'66013452', 		u'manufacturername': u'Philips', u'state': {u'on': False, u'hue': 0, 		u'colormode': u'hs', u'effect': u'none', u'alert': u'none', u'xy': [0.0, 0.0], 			u'reachable': False, 	u'bri': 0, 		u'sat': 0}, 					u'uniqueid': u'00:17:88:01:00:cb:47:cb-0b', u'type': u'Color light', 			u'modelid': u'LST001'}
	def get_lights(self):
		"""
		获取网桥上所有lights信息以及记录所有可达(在线)light的id
		"""
		if self.b is None:
			logger.error("没有连接到网桥")
			return []
		lights = self.b.get_light()

		if  isinstance(lights, list) and lights[0].has_key('error'):
			logger.error("保存的.python_hue过期,请删除该文件重新连接")
			return
		self.lights_info = lights
		for light_id in lights:
			if lights[light_id]['state']['reachable']:
				self.reachable_lights_ids.append(int(light_id))

	def get_lights_info(self):
		"""
		获取网桥上所有lights的信息
		"""
		if self.b is None:
			logger.error("没有连接到网桥")
			return []
		return self.b.get_light()

	def setLights(self, args):
		"""
		设置灯光的开关、颜色...
		"""
		if self.b is None:
			return False
		if len(self.reachable_lights_ids) == 0:
			logger.info('当前网桥上没有在线的灯,请检查灯是否上电')
			return False
		Dict = {}
		Control_Dict = {}
		if isinstance(args, str):
			try:
				Dict = eval(args)
			except:
				if args.lower() == 'on':
					Dict['on'] = True
				elif args.lower() == 'off':
					Dict['on'] = False
				else:
					logger.error("参数有错")
					return False
		elif isinstance(args, dict):
			Dict = args
		else:
			logger.error("参数有错")
			return False
		# print Dict
		if Dict.has_key('lights'):
			Lights = Dict['lights']
			if len(Lights) == 0:
				Lights = self.reachable_lights_ids
			else:
				Lights_tmp = []
				for light in Lights:
					if light in self.reachable_lights_ids:
						Lights_tmp.append(light)
				Lights = Lights_tmp
				if len(Lights) == 0:
					Lights = self.reachable_lights_ids
		else:
			Lights = self.reachable_lights_ids
		if len(Lights) == 0:
			logger.error("参数中的lights id有误,网桥没有添加这个id的设备")
			return False

		Control_Dict['on']  = Dict['on'] if Dict.has_key('on') else True
		if Dict.has_key('xy'):
			if (Dict.has_key('red') or Dict.has_key('green') or Dict.has_key('blue')):
				logger.error('字典参数中不能同时出现xy字段和[red,green,blue]中的一种')
				return False
			Control_Dict['xy'] = Dict['xy']
		elif Dict.has_key('red') and Dict.has_key('green') and Dict.has_key('blue'):
			red = Dict['red']
			green = Dict['green']
			blue = Dict['blue']
			xyz = xyzFromRGB(red, green, blue)
			Control_Dict['xy'] = [xyz[0], xyz[1]]
		else:
			pass
			# logger.error('字典参数中必须出现xy字段或[red,green,blue]')
			# return False
			# Control_Dict['xy'] = self.get_lights_info()[str(Lights[0])]['state']['xy']
		# 35786  47104

		# Control_Dict['hue'] = Dict['hue'] if Dict.has_key('hue') else 35786
		Control_Dict['bri'] = Dict['bri'] if Dict.has_key('bri') else 160
		# Control_Dict['sat'] = Dict['sat'] if Dict.has_key('sat') else 254
		# Control_Dict['ct'] = Dict['ct'] if Dict.has_key('ct') else 500
		# print Control_Dict
		print Control_Dict
		result = False
		for i in xrange(3):
			try:
				self.b.set_light(Lights, Control_Dict)
				result = True
				break
			except:
				logger.error("设置灯光异常,正在重新请求")
				result = False

		return result

	# =================================================================================
	# 以下是一些固定的场景设置,例如开关、红色、闪烁....
	# =================================================================================
	def controlLights(self, lights=[], flag=''):
		"""
		flag是标志,根据标志选择场景
		"""
		if flag.lower() == 'on':
			args = {
				'on': True, 
			}
		elif flag.lower() == 'off':
			args = {
				'on': False, 
			}
		elif flag.lower() == 'red':
			args = {
				'on': True, 
				'red': 255, 
				'green': 0, 
				'blue': 0,
			}
		elif flag.lower() == 'green':
			args = {
				'on': True, 
				'red': 0, 
				'green': 255, 
				'blue': 0,
			}
		elif flag.lower() == 'blue':
			args = {
				'on': True, 
				'red': 0, 
				'green': 0, 
				'blue': 255,
			}
		elif flag.lower() == 'yellow':
			args = {
				'on': True, 
				'xy': [0.4408, 0.5248],
			}
		elif flag.lower() == 'white':
			args = {
				'on': True, 
				'xy': [0.3459, 0.3534],
			}
		elif flag.lower() == 'orange':
			args = {
				'on': True, 
				'xy': [0.6093, 0.381],#[0.5779, 0.409]
			}
		elif flag.lower() == 'pink':
			args = {
				'on': True, 
				'xy': [0.3685, 0.1633]
			}
		# elif flag.lower() == 'blue':
		# 	args = {
		# 		'on': True, 
		# 		'red': 0, 
		# 		'green': 255, 
		# 		'blue': 0,
		# 		'bri': 200,
		# 		'sat': 254,
		# 		'ct': 500,
		# 		'xy': ,
		# 	}
		else:
			args = {}

		if isinstance(lights, list):
			pass
		elif isinstance(lights, str):
			lights_tmp = []
			List = lights.split('_')
			if len(List) > 0:
				for i in List[1:]:
					lights_tmp.append(int(i))
				lights = lights_tmp
			else:
				lights = []
		else:
			lights = []
		args['lights'] = lights
		self.setLights(args)

class HueControlServiceModule():
	def __init__(self, session):
		self.Hue_IP = None
		pass

	def HueLightControl(self, ip=None, lights=[], flag=''):
		hue = HueClass(ip)
		hue.controlLights(lights, flag)

	@staticmethod
	def HueLightControl_1(ip=None, lights=[], flag=''):
		hue = HueClass(ip)
		hue.controlLights(lights, flag)

def test():
	HueControlServiceModule.HueLightControl_1('192.168.199.123', 'HueAllLights','off')

if __name__ == '__main__':
	logger.setLevel(logging.DEBUG)
	streamHandler = logging.StreamHandler()
	streamHandler.setLevel(logging.DEBUG)
	logger.addHandler(streamHandler)
	test()

