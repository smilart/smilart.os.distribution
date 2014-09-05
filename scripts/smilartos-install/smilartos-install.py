# -*- coding: utf-8 -*-
import os
import urwid
import subprocess

def save(fileName, data):
	f = open(fileName, "w+")
	f.write(data)
	f.close()

class NetworkInfo:
	def __init__(self):
		self.ip = None
		self.mask = None
		self.gateway = None
		self.dns = None
		self.hostName = None
		self.name = "name network interface"
		self.updateServer = "name update server"

	def setIP(self, edit, text):
		self.ip = text

	def setMask(self, edit, text):
		self.mask = text

	def setGateway(self, edit, text):
		self.gateway = text

	def setDNS(self, edit, text):
		self.dns = text

	def setHostName(self, edit, text):
		self.hostName = text

	def getAllSettings(self):
		return ("--ip=%s" % self.ip  + " --mask=%s" % self.mask + " --gateway=%s" % self.gateway +
			" --dns=%s" % self.dns)
	def getPrefix(self):
		prefix = sum([bin(int(x)).count('1') for x in self.mask.split('.')])
		return prefix

class CloudConfig:
	def __init__(self, networkInfo, pathToCloudConfig):
		self.hostname = "__hostname__"
		self.name = "__name__" # network interface name
		self.ip = "__ip__"
		self.gateway = "__gateway__"
		self.dns = "__dns__"
		self.updateserver = "__updateserver__"
		self.cloudConfig = pathToCloudConfig
		self.networkInfo = networkInfo

	def makeCloudConfig(self):
		templateFile = open(self.cloudConfig, 'r')
		lines = templateFile.readlines()
		templateFile.close()

		file = open(self.cloudConfig, 'w')
		lines = self.insertVariables(lines)
		file.writelines(lines)
		file.close()

	def insertVariables(self, lines):
		newLines= []
		for line in lines:
			if line.find(self.hostname) != -1:
				line = line.replace(self.hostname, self.networkInfo.hostName)
			elif line.find(self.name) != -1:
				line = line.replace(self.name, self.networkInfo.name)
			elif line.find(self.ip) != -1:
				ip = self.networkInfo.ip + "/" + str(self.networkInfo.getPrefix())
				line = line.replace(self.ip, ip)
			elif line.find(self.gateway) != -1:
				line = line.replace(self.gateway, self.networkInfo.gateway)
			elif line.find(self.dns) != -1:
				line = line.replace(self.dns, self.networkInfo.dns)
			elif line.find(self.updateserver) != -1:
				line = line.replace(self.updateserver, self.networkInfo.updateServer)
			newLines.append(line)
		return newLines

class Installator:

	def __init__(self):
		self.pathToNodeInfo = "/var/lib/smilart_srv/utils/nodeinfo"
		self.pathToConfigNetwork = "/var/lib/smilart_srv/scripts/config_network.sh"
		self.pathToCoreosInstall = "/var/lib/smilart_srv/coreos/coreos-install"
		self.pathToCloudConfig = "/var/lib/smilart_srv/scripts/cloud-config"
		self.titleMenu = u"Smilart Operation System"
		self.firstMenuChoices = [u'Сбор данных для лицензии', u'Установка', u'Выход']
		self.StartMenu = None
		self.pathToLicenseFile = None
		self.networkInfo = NetworkInfo()

		self.palette = [
			('reversed', 'standout', ''),
			('body','black','light gray', 'standout'),
			('main shadow',  'dark gray',  'black'),
        	('line',         'black',      'light gray', 'standout'),
        	('bg background','light gray', 'black'),
			('reverse','light gray','black'),
			('header','white','dark red', 'bold'),
			('important','dark blue','light gray',('standout','underline')),
			('editfc','white', 'dark blue', 'bold'),
			('editbx','light gray', 'dark blue'),
			('editcp','black','light gray', 'standout'),
			('bright','dark gray','light gray', ('bold','standout')),
			('buttn','black','dark cyan'),
			('buttnf','white','dark blue','bold'),
		]

	def firstMenu(self, choices):
		body = [urwid.Text(self.titleMenu), urwid.Divider()]
		for c in choices:
			button = urwid.Button(c)
			urwid.connect_signal(button, 'click', self.firstMenuItemChosen, c)
			body.append(urwid.AttrMap(button, None, focus_map='reversed'))
		return urwid.ListBox(urwid.SimpleFocusListWalker(body))


	def firstMenuItemChosen(self, button, choice):
		if self.firstMenuChoices.index(choice) == 0:
			self.getLicenseData()
		elif self.firstMenuChoices.index(choice) == 1:
			self.installLicense()
		elif self.firstMenuChoices.index(choice) == 2:
			self.exit_program(button)

	def getLicenseData(self):
		info = self.getInfo()
		fileName = "/var/lib/smilart_srv/utils/result"
		save(fileName, info)
		body = [urwid.Text(self.titleMenu), urwid.Divider()]
		body.append(urwid.Text([u'NodeInfo saved to file ', fileName, u'\n']))
		done = urwid.Button(u'Ok')
		urwid.connect_signal(done, 'click', self.exit_program)
		body.append(urwid.AttrMap(done, None, focus_map='reversed'))
		self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))

	def getInfo(self):
		proc = subprocess.Popen(self.pathToNodeInfo, stdout=subprocess.PIPE)
		out, err = proc.communicate()
		code = proc.returncode
		if code != 0:
			print "Error"
			raise urwid.ExitMainLoop()
		return out

	def getPathToLicenseFile(self, edit, text):
		self.pathToLicenseFile = text

	def installLicense(self):
		body = [urwid.Text(self.titleMenu), urwid.Divider()]
		body.append(urwid.Text(u'Укажите путь к файлу лицензии\n'))
		filePathEdit = urwid.Edit()
		body.append(urwid.AttrWrap(filePathEdit, '', 'reversed'))
		body.append(urwid.Divider())
		done = urwid.Button(u'Ok')
		urwid.connect_signal(filePathEdit, 'change', self.getPathToLicenseFile)
		urwid.connect_signal(done, 'click', self.checkLicense)
		body.append(urwid.AttrMap(done, None, focus_map='reversed'))
		self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))

	def checkLicense(self, button):
		# open License File
		body = [urwid.Text(self.titleMenu), urwid.Divider()]
		done = urwid.Button(u'Ok')
		if os.path.exists(self.pathToLicenseFile):
			body.append(urwid.Text(u'Файл лицензии установлен\n'))
			urwid.connect_signal(done, 'click', self.networkSettings)
		else:
			body.append(urwid.Text(u'Файл лицензии не найден\n'))
			urwid.connect_signal(done, 'click', self.exit_program)

		body.append(urwid.AttrMap(done, None, focus_map='reversed'))
		self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))

	def networkSettings(self, button):
		ip_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input Ip: ")), '', 'reversed')
		urwid.connect_signal(ip_edit.base_widget, 'change', self.networkInfo.setIP)

		mask_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input Mask: ")), '', 'reversed')
		urwid.connect_signal(mask_edit.base_widget, 'change', self.networkInfo.setMask)

		gateway_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input Gateway: ")), '', 'reversed')
		urwid.connect_signal(gateway_edit.base_widget, 'change', self.networkInfo.setGateway)

		dns_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input DNS: ")),	'', 'reversed')
		urwid.connect_signal(dns_edit.base_widget, 'change', self.networkInfo.setDNS)

		hostName_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input Host name: ")), '', 'reversed')
		urwid.connect_signal(hostName_edit.base_widget, 'change', self.networkInfo.setHostName)

		blank = urwid.Divider()
		done = urwid.Button(u'Ok')

		urwid.connect_signal(done, 'click', self.configNetwork)

		listbox_content = [
			urwid.Text(self.titleMenu),
			blank,
			urwid.Padding(urwid.Text("Network Settings"), left=2, right=2, min_width=20),
			ip_edit,
			mask_edit,
			gateway_edit,
			dns_edit,
			hostName_edit,
        	blank,
			urwid.AttrMap(done, None, focus_map='reversed')
		]
		listbox = urwid.ListBox(urwid.SimpleFocusListWalker(listbox_content))
		self.StartMenu.original_widget = listbox

	def configNetwork(self, button):
		command = self.pathToConfigNetwork + " " + self.networkInfo.getAllSettings()
		proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
		out, err = proc.communicate()
		code = proc.returncode
		if code != 0:
			body = [urwid.Text(self.titleMenu), urwid.Divider()]
			text = u'Network config error!\n ' + out + '\n ' + err
			done = urwid.Button(u'Выход')
			urwid.connect_signal(done, 'click', self.exit_program)
			body.append(urwid.Text(text))
			body.append(urwid.Divider())
			body.append(urwid.AttrMap(done, None, focus_map='reversed'))
			self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
		else:
			body = [urwid.Text(self.titleMenu), urwid.Divider()]
			text = u'Network configure success!\n ' + out
			done = urwid.Button(u'Далее')
			urwid.connect_signal(done, 'click', self.createCloudConfig)
			body.append(urwid.Text(text))
			body.append(urwid.Divider())
			body.append(urwid.AttrMap(done, None, focus_map='reversed'))
			self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))


	def createCloudConfig(self, button):
		config = CloudConfig(self.networkInfo, self.pathToCloudConfig)
		config.makeCloudConfig()

		body = [urwid.Text(self.titleMenu), urwid.Divider()]
		install = urwid.Button(u'Установка CoreOS')
		urwid.connect_signal(install, 'click', self.installCoreOS)
		done = urwid.Button(u'Выход')
		urwid.connect_signal(done, 'click', self.exit_program)
		body.append(urwid.AttrMap(install, None, focus_map='reversed'))
		body.append(urwid.AttrMap(done, None, focus_map='reversed'))
		self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))


	def installCoreOS(self, button):
		command =  self.pathToCoreosInstall + " -d dba -C stable -c " + self.pathToCloudConfig
		proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
		out, err = proc.communicate()
		code = proc.returncode
		if code != 0:
			body = [urwid.Text(self.titleMenu), urwid.Divider()]
			text = u"CoreOS didn't install!\n + " + out + "\n " + err
			done = urwid.Button(u'Выход')
			urwid.connect_signal(done, 'click', self.exit_program)
			body.append(urwid.Text(text))
			body.append(urwid.Divider())
			body.append(urwid.AttrMap(done, None, focus_map='reversed'))
			self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
		else:
			body = [urwid.Text(self.titleMenu), urwid.Divider()]
			text = u'CoreOS installed successful'
			copy = urwid.Button(u'Копировать файлы')
			urwid.connect_signal(copy, 'click', self.copyServiceContainer)

			done = urwid.Button(u'Выход')
			urwid.connect_signal(done, 'click', self.exit_program())
			body.append(urwid.Text(text))
			body.append(urwid.Divider())
			body.append(urwid.AttrMap(copy, None, focus_map='reversed'))
			body.append(urwid.AttrMap(done, None, focus_map='reversed'))
			self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))


	def copyServiceContainer(self, button):
		pathFrom = ""
		pathTo = ""


	def exit_program(self, button):
		raise urwid.ExitMainLoop()

	def main(self):
		urwid.set_encoding("UTF-8")
		self.StartMenu = urwid.Padding(self.firstMenu(self.firstMenuChoices), left=5, right=5)
		top = urwid.Overlay(self.StartMenu, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
							align='center', width=('relative', 60),
							valign='middle', height=('relative', 60),
							min_width=20, min_height=9)
		urwid.MainLoop(top, self.palette).run()



if __name__ == '__main__':
	Installator().main()
