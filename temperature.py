'''
This script will operate the temperature sensors. This script contains the TempSensor class
'''

import machine, onewire, ds18x20, time

EXT_ADD = b'(\xb3\xb4e\x0e\x00\x00\xf5'
INT_ADD = b'(\x03iT\x0f\x00\x00,'


class TempSensors:
    
    def __init__(self, pin):
        self.pin = pin
        one_wire = machine.Pin(self.pin)
        self.connection = ds18x20.DS18X20(onewire.OneWire(one_wire))
        self.addresses = self.connection.scan()

    def read_temp(self):
        self.connection.convert_temp()
        temps_str = []
        for i in self.addresses:
            tempC = self.connection.read_temp(i)
            if tempC <0:
                temps_str.append(f'{tempC:.3f}')
            # If the temp is positive must add a + sign
            else:
                temps_str.append(f'+{tempC:.3f}')
        
        return temps_str





T_sensors = TempSensors(15)
temps = T_sensors.read_temp()
print(T_sensors.addresses[1],temps)

'''
# This loop should work for any number of sensors
for i in roms:
    time.sleep_ms(750)
    tempC = temperature_sensors.read_temp(i)
    # Print with f string to format the value to 3dp
    print(f'Temperature(C): {tempC:.3f}')'''

