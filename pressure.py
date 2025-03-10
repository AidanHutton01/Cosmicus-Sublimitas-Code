'''
This script will operate the pressure sensor. This script contains the PressSensor class.
'''


import machine, time

def unpack(buffer):
    """ Unpacks MSB - ordered buffer of bytes into an unsigned integer .
    Note : buffer must be a bytes - like object or a list of integers in the
    range [0, 255].
    Usage :
    >>> unpack ([0x01, 0x00])
    256
    >>> unpack ([0x10, 0x00])
    4096
    >>> unpack ([0xFF, 0xFF, 0xFF])
    16777215
    """
    _buffer = reversed(bytearray(buffer))
    return sum(_byte << (_i*8) for _i, _byte in enumerate(_buffer))


class PressSensor:
    
    
    def __init__(self, bus, scl, sda):
        
        self.bus = bus
        self.scl = scl
        self.sda = sda
        self.connection = machine.I2C(self.bus, scl = machine.Pin(self.scl), sda = machine.Pin(self.sda))
        self.device_address = self.connection.scan()
        self.const_addresses = [0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC]
        self.temp_address = b'\x58'
        self.press_address = b'\x48'
    

    #function to find sensor constants (device address, reg position of constants)
    def get_const(self):
        #list of constants to be appended, index 0 is None so that indexes match coefficient names in datasheet
        consts = [None]
        #loop to get each constant from each registry position
        for i in self.const_addresses:
            cxbytes = self.connection.readfrom_mem(self.device_address, i, 2)
            consts.append(unpack(cxbytes))
        return consts
    

    #This function reads the adc value. Didn't feel like a cmd input was
    #necessary, you just have to change the registry position to find either
    #temperature or pressure
    def read_adc(self):
        adc_vals = []
        for i in [self.press_address, self.temp_address]:
            # send temperature ADC command and pause for response
            self.connection.writeto(self.device_address, i)
            time.sleep_ms(50)
            # read the ADC values
            adc_bytes = self.connection.readfrom_mem(add, 0x00, 3)
            # unpack value as integer
            adc_vals.append(unpack(adc_bytes))
            return adc_vals


    #function to calculate the pressure, follows datasheet flowchart
    def calc_pressure(self):
        coeffs = self.get_const()
        adc_P, adc_T = self.read_adc()

        dT = adc_T - (coeffs[5] * 2**8)
        TEMP = 2000 + dT*(coeffs[6]/(2**23))
        OFF = (coeffs[2]*2**16) + (coeffs[4]*dT)/(2**7)
        SENS = (coeffs[1]*2**15) + (coeffs[3]*dT)/(2**8)
        P = (adc_P*(SENS/(2**21)) - OFF)/(2**15)
    
        return P, TEMP

#This is the actual loop
while True:
    #find adc values
    adc_temp = read_adc(devices[0], temp_pos)
    adc_press = read_adc(devices[0], press_pos)
    #calculate actual pressure and temperature values
    P,TEMP = calc_pressure(adc_press, adc_temp, coeffs)
    #timestamp
    t = time.ticks_ms()/1000
    #Print out the pressure and temperature (need to divide the values by 100)
    print(f'{t:.6f}, {P/100:.2f}mbar, {TEMP/100:.2f}C')
    #sleep to change the measurement interval
    time.sleep_ms(500)