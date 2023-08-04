# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import sys
from getspectrum import preprocessing, spectrum, convertDatatoExcel, getPeak
import pandas as pd
import serial
import numpy as np

##############################################################

raw = serial.Serial(port='COM6', baudrate=20000000, timeout=1)
nSample = 1024

class Plot():
    def __init__(self):
        super().__init__()
        
        # Create the plot window
        self.app = QApplication([])
        self.windowplot = pg.GraphicsLayoutWidget()
        self.windowplot.setFixedWidth(1000)

        # Set up for raw data plot
        self.rawdata = self.windowplot.addPlot(row=0, col=0, title='Raw Data Plot') # Add subplot to window
        self.rawdata.setRange(xRange=[0, nSample]) # Set range to plot 
        self.rawdata_plot = self.rawdata.plot(pen='y')
        self.rawdata.setFixedWidth(500)
        
        #Set up for spectrum
        self.spectrum = self.windowplot.addPlot(row=0, col=1, title='Spectrum Plot') # Add subplot to window
        self.spectrum.setRange(xRange=[1, 512]) # Set range to plot 
        self.spectrum_plot = self.spectrum.plot(pen='y')
        self.spectrum.setFixedWidth(500)
        
        # Set up for max index
        self.max_index = self.windowplot.addLabel(row=1, col=0, size='20pt', text='Max Index: -1') # Add subplot to window
        
        self.windowplot.show()
        
    def update_rawdata(self, data):
        self.rawdata_plot.setData(data)
    
    def update_spectrum(self, data):
        self.spectrum_plot.setData(data)
        
    def update_range(self, nSampleX):
        self.rawdata.setRange(xRange=[0, nSampleX]) # Set range to plot
        
    def update_max_index(self, data):
        index = getPeak(data)
        self.max_index.setText(f'Max Index: {index}')
        
    def run(self):
        self.app.instance().exec_()
        
    def stop(self):
        self.app.exit()
            
if __name__ == '__main__':
    plot = Plot()
    
    raw_data = []
    spectrum_data = []
    
    def update():
        dat1 = raw.read(nSample*2) # Read raw data from serial
        dat2 = np.frombuffer(dat1, dtype='int16', offset=0) # Convert to int16
        
        # if len(dat2) == nSample:
        #     s = np.array(dat2[0:nSample])
        #     cekF0F = s[nSample - 1]
        #     nSampleX = s[nSample - 2]
        #     sr = s[nSample - 3]
        #     prf = s[nSample - 4]
        #     cekIns = s[nSample - 5]
        # else:
        #     cekF0F = 0

        # if cekF0F == 3855:
        #     s[nSampleX:nSample] = 0
        #     s = s - (np.sum(s)) / nSampleX
            
        #     s[nSampleX:nSample] = 0
        #     ss = s
        #     print(ss)
        #     s = s * np.hamming(nSample)
        #     # S = 20*np.log10(abs(np.fft.rfft(s))/np.sqrt(nSampleX)+.001)
        #     S = 20 * np.log10(abs(np.fft.rfft(s)) / (nSampleX) + 0.001)
        #     S = S * S / 15
        #     raw_data.append(ss)
        #     spectrum_data.append(S)
        #     # S = 2*(S-30)

        #     plot.update_rawdata(ss)
        #     plot.update_spectrum(S)
        
        s = np.array(dat2[0:nSample]) # Make np array
        
        # Read some variables
        nSampleX = s[nSample-2]
        #sf = s[nSample-3]
        #prf = s[nSample-4]
        plot.update_range(nSampleX)
        s = preprocessing(s, nSampleX) # Data preprocessing
        spect = spectrum(s, nSampleX) # Calculate PSD
        
        raw_data.append(s)
        spectrum_data.append(spect)
        
        plot.update_rawdata(s)
        plot.update_spectrum(spect)
        plot.update_max_index(spect)

    try:
        raw.flushInput()
        raw.flushOutput()
        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(1)
        plot.run()
    except KeyboardInterrupt: # masih ada masalah
        plot.stop()
        convertDatatoExcel(raw_data, 'rawdata')
        convertDatatoExcel(spectrum_data, 'spectrum')
        print("Data collection stopped.")
        sys.exit()

            