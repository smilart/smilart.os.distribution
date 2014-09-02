# -*- coding: utf-8 -*-
import os
import urwid
import subprocess

def save(fileName, data):
	f = open(fileName, "w+")
	f.write(data)
	f.close()

class NetworkInfo:
	ip = None
	mask = None
	gateway = None
	dns = None
	hostName = None

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

class InstallMenu:

	pathToNodeInfo = "/var/lib/smilart_srv/utils/nodeinfo"
	pathToConfigNetwork = "/var/lib/smilart_srv/scripts/config_network.sh"
	titleMenu = u"Smilart Operation System"
	firstMenuChoices = [u'Сбор данных для лицензии', u'Установка', u'Выход']
	StartMenu = None
	pathToLicenseFile = None

	palette = [
		('reversed', 'standout', ''),
		('body','black','light gray', 'standout'),
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
		info = "HDD_SERIAL MOTHERBOARD_SERIAL CPUID"
		fileName = "/var/lib/smilart_srv/utils/result"
		save(fileName, info)
		body = [urwid.Text(self.titleMenu), urwid.Divider()]
		body.append(urwid.Text([u'NodeInfo saved to file ', fileName, u'\n']))
		done = urwid.Button(u'Ok')
		urwid.connect_signal(done, 'click', self.exit_program)
		body.append(urwid.AttrMap(done, None, focus_map='reversed'))
		self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))

	def getInfo(self):
		proc = subprocess.Popen(self.pathToNodeInfo, shell=True, stdout=subprocess.PIPE)
		out, err = proc.communicate()
		if err:
			e = ReturnedError(err)
			e.output = out
			raise e
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
		license = True
		body = [urwid.Text(self.titleMenu), urwid.Divider()]
		done = urwid.Button(u'Ok')
		if license:
			body.append(urwid.Text(u'Файл лицензии установлен\n'))
			urwid.connect_signal(done, 'click', self.networkSettings)
		else:
			body.append(urwid.Text(u'Файл лицензии не верный\n'))
			urwid.connect_signal(done, 'click', self.exit_program)

		body.append(urwid.AttrMap(done, None, focus_map='reversed'))
		self.StartMenu.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))

	def networkSettings(self, button):
		networkInfo = NetworkInfo()

		ip_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input Ip: ")), '', 'reversed')
		urwid.connect_signal(ip_edit.base_widget, 'change', networkInfo.setIP)

		mask_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input Mask: ")), '', 'reversed')
		urwid.connect_signal(ip_edit.base_widget, 'change', networkInfo.setMask)

		gateway_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input Gateway: ")), '', 'reversed')
		urwid.connect_signal(ip_edit.base_widget, 'change', networkInfo.setGateway)

		dns_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input DNS: ")),	'', 'reversed')
		urwid.connect_signal(ip_edit.base_widget, 'change', networkInfo.setDNS)

		hostName_edit = urwid.AttrWrap(urwid.Edit(('editcp', u"Input Host name: ")), '', 'reversed')
		urwid.connect_signal(ip_edit.base_widget, 'change', networkInfo.setHostName)

		blank = urwid.Divider()
		done = urwid.Button(u'Ok')

		urwid.connect_signal(done, 'click', self.configNetwork, networkInfo)

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

	def configNetwork(self, button, networkInfo):
		proc = subprocess.Popen([self.pathToConfigNetwork, networkInfo.getAllSettings()], shell=True, stdout=subprocess.PIPE)
		out, err = proc.communicate()
		if err:
			e = ReturnedError(err)
			e.output = out
			raise e
		self.exit_program(button)


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
	InstallMenu().main()
