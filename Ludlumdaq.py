import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import serial
import argparse

#get command line arguments
parser = argparse.ArgumentParser(description='View a single waveform coming from UART')
parser.add_argument('-p','--port', help='The port to listen to', default="/dev/ttyUSB0", required=False)
parser.add_argument('-f','--filename', help='Name of data file', default="ludlum.dat", required=False)

args = parser.parse_args()


#set the serial port settings
set_ser = serial.Serial()
set_ser.port=args.port             #the location of the USB port 
set_ser.baudrate=38400             #baud rate of 1MHz
set_ser.parity = serial.PARITY_NONE
set_ser.stopbits=serial.STOPBITS_ONE
set_ser.bytesize = serial.EIGHTBITS
set_ser.timeout=0.5

set_ser.open()

#open the output filename
f=open(args.filename, 'w')

#data header
f.write("Neutron Dose (uSv/hr)\tGamma Dose (uSv/hr)\n")

n = 100
number_of_frames = 10
gammaData = []
neutronData=[]
data=[]

#draw histogram each time this is called
def update_hist(num, data):

    global f

    #send message to survey meter. 'RR' requests dose
    message="RR\r\n"
    set_ser.write(message.encode('utf-8'))

    #read response
    d=set_ser.read(5000)
    
    if len(d) == 22:

        #parse response
        neutronDose=float(d[0:6])/100
        gammaDose = float(d[7:13])/100

        f.write(str(neutronDose)+"\t"+str(gammaDose)+"\n")

        #don't add 0 events to plot. They will be saved to file though.
        if gammaDose != 0:
            gammaData.append(gammaDose)
        if neutronDose != 0:
            neutronData.append(neutronDose)


    #plot the histograms
    plt.cla()
    plt.hist(neutronData,n, alpha=0.5, label='Neutron dose')
    plt.hist(gammaData  ,n, alpha=0.5, label='$\gamma$ dose');
    plt.xlabel("dose ($\mu$Sv/hr)")
    plt.ylabel("Counts")
    plt.legend(loc='upper right')

fig = plt.figure()


animation = animation.FuncAnimation(fig, update_hist, number_of_frames, fargs=(data, ) )

plt.show()

set_ser.close()
f.close()
