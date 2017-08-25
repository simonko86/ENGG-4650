from __future__ import print_function
import sys
import urllib
import urllib2
import time
import socket
import httplib
from gattlib import GATTRequester
from gattlib import GATTResponse
from gattlib import DiscoveryService

public_hash = '7JYarO9dElfVn7vnlG5q'
private_hash = 'mzM2eZoRN4SpkJ7kRGPK'
base_url = "data.sparkfun.com"

fields = ["bpressure", "hrate"]

class Reader(object):
    def __init__(self, address):
        writeResponse = False
        try:
            self.requester = GATTRequester(address, False)
            self.connect()
            self.send_data()
        except:
            print("Connection failed")
            self.requester.connect(False)

    def connect(self):
        print("Connecting...", end=' ')
        sys.stdout.flush()

        self.requester.connect(True)
        print("OK!")

    def send_data(self):
        status = True
        profile = self.requester.read_by_handle(0x61)
        time.sleep(2)
        print(profile)
        #Checks the profile loaded by the FPGA, if it's 12, then stop loop
        while ("\x0c" not in profile):
            #Attempt to set profile to 12
            try:
                self.requester.write_by_handle(0x61, str(bytearray([12])))
            except RuntimeError:
                status = False
                break
            #Delay time to allow for successful transfer
            time.sleep(2)
            print("Currently in profile loop")
            try:
                profile = self.requester.read_by_handle(0x61)
            except RuntimeError:
                status = False
                break
            time.sleep(2)
        #time.sleep(3)
        while status:
            #Write the button press to reset data
            try:
                writeResponse = GATTResponse()
                self.requester.write_by_handle_async(0x72, str(bytearray([1])), writeResponse)
                counter = 0
                time.sleep(0.4)
                    
                information_taken = self.requester.read_by_handle(0xa2)[0]
                
                counter = 0
                time.sleep(0.5)
                print("bytes received:", end=' ')
                print(int(ord(information_taken[0])))
                #first array containing value
                data = {}
                data[fields[0]] = 0
                #send to bpressure array
                data[fields[1]] = int(ord(information_taken[0]))
                params = urllib.urlencode(data)
                data = urllib.urlencode(data)
                headers = {}
                headers["Content-Type"] = 'application/x-www-form-urlencoded'
                headers["Connection"] = "close"
                headers["Content-Length"] = len(params)
                headers["Phant-Private-Key"] = private_hash

                c = httplib.HTTPConnection(base_url)
                c.request("POST", "/input/" + public_hash + ".txt", params, headers)
                #send to website https://data.sparkfun.com/streams/7JYarO9dElfVn7vnlG5q
                r = c.getresponse()
                #print (r.status,r.reason)
                #time.sleep(2)
            except:
                break
        try:
            self.requester.disconnect()
        except:
            print("disconnect failed")
       
if __name__ == '__main__':


    service = DiscoveryService("hci0")
    devices= service.discover(5)

    counter = 0
    flag = True
    while flag:
        counter = counter + 1;
        for address, name in list(devices.items()):
            print("name: {}, address: {}".format(name, address))
            if(address == "C0:44:49:45:47:4F"):
                print("FPGA found")
                Reader("C0:44:49:45:47:4F")
                counter = 0
                time.sleep(4)
        if(counter == 20):
            flag = False
        time.sleep(2)
    
    
    print("Done.")