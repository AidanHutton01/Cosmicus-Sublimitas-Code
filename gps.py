#setup the UART connection
from machine import UART , Pin
import time
uart = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17
                                                 ))
uart.init(9600, bits=8, parity=None, stop=1)
#print(uart.readline())

#function to listen for GPS signals
def listen_for_sentence (port , sentence_type ):
    """ Listen for NMEA sentence_type on GPS serial port .
    Parameters
    ----------
    port : uart
    the ( open ) serial port connection to the GPS unit
    sentence_type : str
    the 3 character sentence identifier ( eg GLL , RMC , etc .)
    Returns
    -------
    str
    the NMEA GPS sentence
    """
    while port.any():
        sentence = port.readline().decode('ascii')
        sentenceid = sentence [3:6]
        if sentenceid == sentence_type:
            return sentence

#open empty dictionary with the correct keys
data = {'longitude':[], 'latitude':[], 'altitude':[], 'timestamp':[],
        'sentence':[], 'checksum':[]}
#function will take a dictionary with the specified format and fill it with sentence data
def sort_data(sentence, dic):
    #values are found by spliting the string
    #the last 3 fields are still joined because they use different delimiters
    vals = sentence.split(",")
    #I noticed that sometimes not all the fields are in the sentance
    #this part checks to see if there is 14, if not it appeneds Nones to fill out the data
    if not len(vals)==14:
        for i in range(14-len(vals)):
            vals.append(None)
    #for lat, long, alt and time check to see if None        
    if vals[2]==None:
        dic['latitude'].append(None)
    else:
        #if not None take first 2 numbers as deg and the rest as arcmin
        ulong = int(vals[2][0:2])+(float(vals[2][2:])/60)
        #check hemisphere and add the sign
        if vals[3] == 'N':
            sign = '+'
        else:
            sign = '-'
        slong = sign+str(ulong)
        dic['latitude'].append(slong)
    #long is processed pretty much the same as lat
    if vals[4]==None:
        dic['longitude'].append(None)
    else:
        ulat = int(vals[4][0:3])+(float(vals[4][3:])/60)
        if vals[5] == 'E':
            sign = '+'
        else:
            sign = '-'
        slat = sign+str(ulat)
        dic['longitude'].append(slat)
    
    if vals[8]==None:
        dic['altitude'].append(None)
    else:
        #add orthometric hieght to geoid seperation for alt from MSL
        dic['altitude'].append(float(vals[9])+float(vals[11]))
    
    if vals[1]==None:
        dic['timestamp'].append(None)
    else:
        dic['timestamp'].append(vals[1])
        
    dic['sentence'].append(sentence)
    dic['checksum'].append(vals[-1][-2:])
    
    return dic


time.sleep_ms(1000)
while True:
    time.sleep_ms(1000)
    #get sentence
    sentence = listen_for_sentence(uart, 'GGA')
    #update data dictionary
    data = sort_data(sentence, data)
    #print new row
    print(f"{data['timestamp'][-1]}, {data['latitude'][-1]}, {data['longitude'][-1]}, {data['altitude'][-1]}")