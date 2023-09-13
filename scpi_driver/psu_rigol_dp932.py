
# -*- coding: utf-8 -*-
"""
@author: Edward Lai

Implements pyvisa communication with Rigol Device over USB SPCI protocal 
"""
import pyvisa
import time, sys

class Rigol_DP932():
    def __init__(self, usb_serial=None):
        self.rm = pyvisa.ResourceManager()
        self.instrument_list = self.rm.list_resources()
        self.usb_address = []
        
        print(self.instrument_list)

        for d in self.instrument_list:
            if usb_serial is None:
                if 'USB'.lower() in d.lower():
                    print("WARN: Device SN not specified. Using default usb device")
                    self.usb_address.append(d)
                continue

            if usb_serial.lower() in d.lower():
                self.usb_address.append(d)
            
        if self.usb_address:
            self.dev = self.rm.open_resource(self.usb_address[0])
        else:        
            raise Exception("Pyvista is not able to find the connection") 
        


    def mywrite(self, message):
        self.dev.write(message)
        time.sleep(0.1)
        error = self.dev.query('SYST:ERR?')
        if not error[0]:
            print(message+' recieved. An Error occured: '+ str(error))

    
    
    def myWriteAndRead(self, message):
        resp = self.dev.query(message)
        time.sleep(0.1)
        error = self.dev.query('SYST:ERR?')
        if not error[0]:
            print(message+' recieved. An Error occured: '+ str(error))
        print(message + ': ' + resp) 
        return resp

    def reset(self):
        """resets the instrument, registers,buffers"""
        self.mywrite("*RST")
        time.sleep(0.2)


    def close_instrument(self):
        self.dev.close()

    def set_bias(self, channel=1, i=0.1, i_protection_level=0.1, v=0.5):
        self.mywrite(':INST CH{channel}'.format(channel=int(channel)))
        self.mywrite(':CURR {i}'.format(i = i))
        self.mywrite(':CURR:PROT {i_level}'.format(i_level = i_protection_level))
        self.mywrite(':CURR:PROT:STAT ON')
        self.mywrite(':VOLT {0}'.format(v))

    def get_channel_state(self, channel=1):
        self.myWriteAndRead(':MEAS:CURR? CH{channel}'.format(channel=int(channel)))
        self.myWriteAndRead(':MEAS:POWE? CH{channel}'.format(channel=int(channel)))

        # voltage, current, power
        self.myWriteAndRead(':MEAS:ALL? CH{channel}'.format(channel=int(channel)))

    def turn_off(self, channel = 1):
        self.mywrite(':OUTP CH{channel},OFF'.format(channel = channel))

    def turn_on(self, channel = 1):
        self.mywrite(':OUTP CH{channel},ON'.format(channel = channel))

    def console(self):
        """
        opens a console to send commands. See the commands in the user manual.
        """
        cmd = ''
        while cmd != 'exit()':
            cmd = raw_input('Rigol DP832 console, Type exit() to leave> ')
            if cmd.find('?') >= 0:
                answer = self.dev.query(cmd)
                print (answer)
            elif cmd.find('?') < 0 and cmd != 'exit()':
                self.dev.write(cmd)
        else:
            print ("Exiting the Rigol DP832 console")


if __name__ == "__main__":
    USB_SN= None
    r = Rigol_DP932(usb_serial=USB_SN)
    
	#To start a console
	# r.console()
    
	# This will reset the instrument, apply a bias of 1 V wih 0.1A of protection current for 10 sec and then turn off
    r.reset()
    r.get_channel_state()

    r.set_bias(channel=1, i=0.1, i_protection_level=0.2, v=1)
    r.turn_on(channel=1)
    r.get_channel_state()
    time.sleep(10)
    r.turn_off(channel=1)    
    r.close_instrument()