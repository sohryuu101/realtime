import serial
import serial.tools.list_ports
import numpy as np


ports = serial.tools.list_ports.comports()
for port, desc, hwid in sorted(ports):
    portc = port
    print("{}\n".format(portc))
    print("{}\n".format(desc))
    print("{}\n".format(hwid))
    #
    #raw = serial.Serial(port=portc, baudrate=20000000, timeout=1)

raw = serial.Serial(port='COM6', baudrate=2000000, timeout=1)

nSample = 1024

while True:
    # data raw berupa buffer byte atau sinyal dari radar
    dat1 = raw.read(nSample * 2)
    # data yang diolah dari raw menjadi numpy type data integer 16bit
    dat2 = np.frombuffer(dat1, dtype="int16", offset=0)
    print(dat2)