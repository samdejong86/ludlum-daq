import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import serial
import argparse

parser = argparse.ArgumentParser(description='View a single waveform coming from UART')
parser.add_argument('-p','--port', help='The port to listen to', default="/dev/ttyUSB0", required=False)
parser.add_argument('-f','--filename', help='Name of data file', default="ludlum.dat", required=False)
parser.add_argument('-g','--gamma', help='Plot gamma dose instead of neutron dose', action='store_true', required=False)

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


f=open(args.filename, 'w')

f.write("Neutron Dose (uSv/hr)\tGamma Dose (uSv/hr)\n")

n = 100
number_of_frames = 10
data = []



def update_hist(num, data):

    global f
    
    message="RR\r\n"
    set_ser.write(message.encode('utf-8'))
    
    d=set_ser.read(5000)

    #global data
    
    if len(d) == 22:
    
        neutronDose=float(d[0:6])/100
        gammaDose = float(d[7:13])/100

        f.write(str(neutronDose)+"\t"+str(gammaDose)+"\n")
        
        if args.gamma:
            data.append(gammaDose)
        else:
            data.append(neutronDose)


    global particle
        
    plt.cla()
    plt.hist(data,100)
    plt.xlabel(particle+"dose ($\mu$Sv/hr)")
    plt.ylabel("Counts")

data.append(0)
fig = plt.figure()
hist = plt.hist(0,100)


animation = animation.FuncAnimation(fig, update_hist, number_of_frames, fargs=(data, ) )

particle=""
if args.gamma:
    particle="$\gamma$ "
else:
    particle="Neutron "


plt.xlabel(particle+"dose ($\mu$Sv/hr)")
plt.ylabel("Counts")
plt.show()

set_ser.close()
f.close()
